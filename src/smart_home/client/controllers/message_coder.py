from __future__ import annotations
import base64
import binascii
from datetime import datetime
from .time_service import TimeService
from ...proto.v1 import message_pb2


def _wrap_envelope(message) -> str:
    """Wraps a protobuf message into an Envelope and encodes it as base64."""
    envelope = message_pb2.Envelope()
    if isinstance(message, message_pb2.DeviceRegisterReq):
        envelope.device_register_req.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceStateChange):
        envelope.device_state_change.CopyFrom(message)
    elif isinstance(message, message_pb2.TimeShiftRequest):
        envelope.time_shift_request.CopyFrom(message)
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


def encode_register_request(device_type: str, time_service: TimeService) -> tuple[str, message_pb2.DeviceRegisterReq]:
    """Encodes a DeviceRegisterReq wrapped in an Envelope to a base64 string.
    Returns both the encoded payload and the original request object,
    so the caller can inspect fields such as device_id after encoding.
    """
    req = message_pb2.DeviceRegisterReq()
    req.device_type = device_type
    req.timestamp = time_service.now_as_timestamp()
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


def create_state_change_message(
    device_id: int,
    parameters: dict[str, str],
    device_type: int,
    time_service: TimeService,
) -> message_pb2.DeviceStateChange:
    msg = message_pb2.DeviceStateChange()
    msg.device_id = device_id
    msg.timestamp = time_service.now_as_timestamp()
    msg.device_type = device_type
    if parameters:
        msg.parameters.update(parameters)
    return msg


def encode_state_change(device_id: int, parameters: dict[str, str], device_type: int, time_service: TimeService) -> str:
    """Encodes a DeviceStateChange wrapped in an Envelope to a base64 string."""
    msg = create_state_change_message(device_id, parameters, device_type, time_service)
    return _wrap_envelope(msg)

def encode_time_shift_request(new_time: datetime) -> str:
    """Encodes a TimeShiftRequest wrapped in an Envelope to a base64 string.
    The new datetime to set as simulated time on the server.
    """
    msg = message_pb2.TimeShiftRequest()
    msg.year = new_time.year
    msg.month = new_time.month
    msg.day = new_time.day
    msg.hour = new_time.hour
    msg.minute = new_time.minute
    msg.second = new_time.second
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


def decode_device_registration(response_b64: str) -> message_pb2.DeviceRegisterReq | None:
    """Decodes a base64 string into a DeviceRegisterReq by unwrapping the Envelope.
    Returns None if the payload is not valid or not a DeviceRegisterReq.
    """
    
    envelope = _unwrap_envelope(response_b64)
    if envelope is None:
        return None
    
    if envelope.WhichOneof("payload") == "device_register_req":
        return envelope.device_register_req
    
    return None
