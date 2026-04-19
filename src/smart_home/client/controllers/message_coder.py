from __future__ import annotations

import base64

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


def encode_state_change(device_id: int, parameters: dict[str, str], device_type: str) -> str:
    """
    Encodes a DeviceStateChange message into a base64 string.
    
    Args:
        device_id: The unique identifier of the device.
        parameters: A dictionary containing the state changes.
        device_type: String representing the type of the device (np. "lampka").
    """
    msg = message_pb2.DeviceStateChange()

    msg.device_id = device_id
    msg.timestamp = int(time())
    msg.device_type = device_type #string
    
    if parameters:
        msg.parameters.update(parameters)

    payload_bytes = msg.SerializeToString()
    payload_b64 = base64.b64encode(payload_bytes).decode("utf-8")
    
    return payload_b64
