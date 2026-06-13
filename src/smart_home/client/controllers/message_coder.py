from __future__ import annotations

import base64
from datetime import datetime
from time import time

from ...proto.v1 import message_pb2
from ..models.device import Device
from .time_service import TimeService


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
    elif isinstance(message, message_pb2.DeviceStateChangeResp):
        envelope.device_state_change_resp.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceRegisterReq):
        envelope.device_register_req.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceRegisterResp):
        envelope.device_register_resp.CopyFrom(message)
    elif isinstance(message, message_pb2.TimeShiftRequest):
        envelope.time_shift_request.CopyFrom(message)
    elif isinstance(message, message_pb2.TimeShiftResp):
        envelope.time_shift_resp.CopyFrom(message)
    else:
        raise ValueError(f"Unsupported message type: {type(message).__name__}")

    return envelope.SerializeToString()


def _wrap_envelope(message) -> str:
    return base64.b64encode(build_envelope(message)).decode("utf-8")


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


def _timestamp(time_service: TimeService | None) -> int:
    if time_service is not None:
        return time_service.now_as_timestamp()
    return int(time())


def encode_register_request(
    device_type: str,
    capabilities: dict[str, str] | None = None,
    device_state: dict[str, str] | None = None,
    device_id: int = 0,
    time_service: TimeService | None = None,
) -> tuple[str, message_pb2.DeviceRegisterReq]:
    req = message_pb2.DeviceRegisterReq()
    req.device_id = device_id
    req.device_type = device_type
    req.timestamp = _timestamp(time_service)
    req.capabilities.update(capabilities or {})
    req.device_state.update(device_state or {})

    payload_b64 = _wrap_envelope(req)
    return payload_b64, req


def decode_register_response(response_b64: str) -> message_pb2.DeviceRegisterResp | None:
    envelope = _decode_envelope(response_b64)
    if envelope is None or envelope.WhichOneof("payload") != "device_register_resp":
        return None
    return envelope.device_register_resp


def decode_state_change_response(response_b64: str) -> message_pb2.DeviceStateChangeResp | None:
    envelope = _decode_envelope(response_b64)
    if envelope is None or envelope.WhichOneof("payload") != "device_state_change_resp":
        return None
    return envelope.device_state_change_resp


def encode_state_change(
    device_id: int,
    parameters: dict[str, str],
    device_type: str | int,
    time_service: TimeService | None = None,
) -> str:
    msg = message_pb2.DeviceStateChange()
    msg.device_id = device_id
    msg.timestamp = _timestamp(time_service)
    msg.device_type = _device_type_code(device_type)
    if parameters:
        msg.parameters.update(parameters)

    return _wrap_envelope(msg)


def encode_time_shift_request(new_time: datetime) -> str:
    msg = message_pb2.TimeShiftRequest()
    msg.year = new_time.year
    msg.month = new_time.month
    msg.day = new_time.day
    msg.hour = new_time.hour
    msg.minute = new_time.minute
    msg.second = new_time.second
    return _wrap_envelope(msg)


def decode_time_shift_response(response_b64: str) -> message_pb2.TimeShiftResp | None:
    envelope = _decode_envelope(response_b64)
    if envelope is None or envelope.WhichOneof("payload") != "time_shift_resp":
        return None
    return envelope.time_shift_resp


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
