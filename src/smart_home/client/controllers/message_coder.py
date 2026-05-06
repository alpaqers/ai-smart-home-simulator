from __future__ import annotations
import base64
import binascii
from time import time
from ...proto.v1 import message_pb2


def _wrap_envelope(message) -> str:
    """Wraps a protobuf message into an Envelope and encodes it as base64."""
    envelope = message_pb2.Envelope()
    if isinstance(message, message_pb2.DeviceRegisterReq):
        envelope.device_register_req.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceStateChange):
        envelope.device_state_change.CopyFrom(message)
    return base64.b64encode(envelope.SerializeToString()).decode("utf-8")


def _unwrap_envelope(response_b64: str) -> message_pb2.Envelope | None:
    """Decodes a base64 string and unwraps it into an Envelope.
    Returns None if decoding or parsing fails.
    """
    try:
        data = base64.b64decode(response_b64, validate=True)
        envelope = message_pb2.Envelope()
        envelope.ParseFromString(data)
        return envelope
    except Exception:
        return None


def encode_register_request(device_type: str) -> tuple[str, message_pb2.DeviceRegisterReq]:
    """Encodes a DeviceRegisterReq wrapped in an Envelope to a base64 string.
    Returns both the encoded payload and the original request object,
    so the caller can inspect fields such as device_id after encoding.
    """
    req = message_pb2.DeviceRegisterReq()
    req.device_type = device_type
    req.timestamp = int(time())
    req.capabilities[""] = ""
    # Wrap the request in an Envelope before encoding
    payload_b64 = _wrap_envelope(req)
    return payload_b64, req


def decode_register_response(response_b64: str) -> message_pb2.DeviceRegisterResp | None:
    """Decodes a base64 string into a DeviceRegisterResp by unwrapping the Envelope.
    Returns None if the payload is not a valid DeviceRegisterResp.
    """
    envelope = _unwrap_envelope(response_b64)
    if envelope is None:
        return None
    # Check if the envelope contains a DeviceRegisterResp
    if envelope.WhichOneof("payload") == "device_register_resp":
        return envelope.device_register_resp
    return None


def encode_state_change(device_id: int, parameters: dict[str, str], device_type: str) -> str:
    """Encodes a DeviceStateChange wrapped in an Envelope to a base64 string.
    
    Args:
        device_id: The unique identifier of the device.
        parameters: A dictionary containing the state changes.
        device_type: String representing the type of the device.
    """
    msg = message_pb2.DeviceStateChange()
    msg.device_id = device_id
    msg.timestamp = int(time())
    msg.device_type = device_type
    if parameters:
        msg.parameters.update(parameters)
    # Wrap the message in an Envelope before encoding
    return _wrap_envelope(msg)


def decode_state_update_message(response_b64: str) -> message_pb2.DeviceStateUpdate | None:
    """Decodes a base64 string into a DeviceStateUpdate by unwrapping the Envelope.
    Returns None if the payload is not valid or not a DeviceStateUpdate.
    """
    envelope = _unwrap_envelope(response_b64)
    if envelope is None:
        return None
    # Check if the envelope contains a DeviceStateUpdate
    if envelope.WhichOneof("payload") == "device_state_update":
        return envelope.device_state_update
    return None
