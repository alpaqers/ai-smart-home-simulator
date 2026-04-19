from __future__ import annotations

import base64
import binascii

from time import time
from ...proto.v1 import message_pb2


def encode_register_request(device_type: str) -> tuple[str, message_pb2.DeviceRegisterReq]:
    """Encode a DeviceRegisterReq to a base64 string for transmission.

    Returns both the encoded payload and the original request object,
    so the caller can inspect fields such as device_id after encoding.
    """
    req = message_pb2.DeviceRegisterReq()
    req.device_type = device_type
    req.timestamp = int(time())
    req.capabilities[""] = ""

    payload_b64 = base64.b64encode(req.SerializeToString()).decode("utf-8")
    return payload_b64, req


def decode_register_response(response_b64: str) -> message_pb2.DeviceRegisterResp:
    """Decode a base64 string into a DeviceRegisterResp protobuf message."""
    resp_bytes = base64.b64decode(response_b64)
    return message_pb2.DeviceRegisterResp.FromString(resp_bytes)


def create_state_change_message(
    device_id: int,
    parameters: dict[str, str],
    device_type: int,
) -> message_pb2.DeviceStateChange:
    """Create a DeviceStateChange protobuf object with timestamp and parameters."""
    msg = message_pb2.DeviceStateChange()
    msg.device_id = device_id
    msg.timestamp = int(time())
    msg.device_type = device_type

    if parameters:
        msg.parameters.update(parameters)

    return msg


def encode_state_change(device_id: int, parameters: dict[str, str], device_type: int) -> str:
    """
    Encodes a DeviceStateChange message into a base64 string.
    
    Args:
        device_id: The unique identifier of the device.
        parameters: A dictionary containing the state changes (e.g., {"power": "ON"}).
        device_type: Integer ID representing the type of the device.
        
    Returns:
        A base64 encoded string of the serialized protobuf message.
    """
    msg = create_state_change_message(
        device_id=device_id,
        parameters=parameters,
        device_type=device_type,
    )

    payload_bytes = msg.SerializeToString()
    payload_b64 = base64.b64encode(payload_bytes).decode("utf-8")
    
    return payload_b64


def decode_state_update_message(response_b64: str) -> message_pb2.DeviceStateUpdate | None:
    """Decode base64 payload to DeviceStateUpdate when possible.

    Returns None when the payload is not valid base64/protobuf state update data.
    """
    try:
        payload = base64.b64decode(response_b64, validate=True)
    except (binascii.Error, ValueError):
        return None

    msg = message_pb2.DeviceStateUpdate()
    try:
        msg.ParseFromString(payload)
    except Exception:
        return None

    has_content = bool(msg.parameters) or msg.command_type != 0 or msg.timestamp != 0
    if msg.device_id <= 0 or not has_content:
        return None

    return msg
