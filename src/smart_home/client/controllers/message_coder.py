from __future__ import annotations

import base64
from time import time

from ...proto.v1 import message_pb2
from ..models.device import Device


_DEVICE_TYPE_CODES = {
    "lamp": 1,
    "thermometer": 2,
    "sensor": 3,
    "ac": 4,
    "airconditioning": 4,
}


def build_envelope(message) -> bytes:
    envelope = message_pb2.Envelope()
    if isinstance(message, message_pb2.DeviceStateChange):
        envelope.device_state_change.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceStateUpdate):
        envelope.device_state_update.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceResponse):
        envelope.device_response.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceRegisterReq):
        envelope.device_register_req.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceRegisterResp):
        envelope.device_register_resp.CopyFrom(message)
    else:
        raise ValueError(f"Unsupported message type: {type(message).__name__}")

    return envelope.SerializeToString()


def parse_envelope(data: bytes) -> message_pb2.Envelope:
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)
    return envelope


def _decode_envelope(payload_b64: str) -> message_pb2.Envelope | None:
    try:
        return parse_envelope(base64.b64decode(payload_b64, validate=True))
    except Exception:
        return None


def _device_type_code(device_type: str | int) -> int:
    if isinstance(device_type, int):
        return device_type
    return _DEVICE_TYPE_CODES.get(device_type.lower().strip().replace(" ", ""), 0)


def encode_register_request(
    device_type: str,
    capabilities: dict[str, str] | None = None,
    device_state: dict[str, str] | None = None,
    device_id: int = 0,
) -> tuple[str, message_pb2.DeviceRegisterReq]:
    req = message_pb2.DeviceRegisterReq()
    req.device_id = device_id
    req.device_type = device_type
    req.timestamp = int(time())
    req.capabilities.update(capabilities or {})
    req.device_state.update(device_state or {})

    payload_b64 = base64.b64encode(build_envelope(req)).decode("utf-8")
    return payload_b64, req


def decode_register_response(response_b64: str) -> message_pb2.DeviceRegisterResp | None:
    envelope = _decode_envelope(response_b64)
    if envelope is None or envelope.WhichOneof("payload") != "device_register_resp":
        return None
    return envelope.device_register_resp


def encode_state_change(device_id: int, parameters: dict[str, str], device_type: str | int) -> str:
    msg = message_pb2.DeviceStateChange()
    msg.device_id = device_id
    msg.timestamp = int(time())
    msg.device_type = _device_type_code(device_type)
    if parameters:
        msg.parameters.update(parameters)

    return base64.b64encode(build_envelope(msg)).decode("utf-8")


def decode_state_update_message(response_b64: str) -> message_pb2.DeviceStateUpdate | None:
    envelope = _decode_envelope(response_b64)
    if envelope is None or envelope.WhichOneof("payload") != "device_state_update":
        return None

    msg = envelope.device_state_update
    has_content = bool(msg.parameters) or msg.command_type != 0 or msg.timestamp != 0
    if msg.device_id <= 0 or not has_content:
        return None

    return msg


def decode_device_registration(response_b64: str) -> Device | None:
    envelope = _decode_envelope(response_b64)
    if envelope is None or envelope.WhichOneof("payload") != "device_register_req":
        return None

    req = envelope.device_register_req
    return Device(
        device_id=req.device_id,
        device_type=req.device_type,
        capabilities=dict(req.capabilities),
        device_state=dict(req.device_state),
    )
