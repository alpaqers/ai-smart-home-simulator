from asyncio import StreamWriter

from smart_home.proto.v1 import message_pb2
from smart_home.server.events import DeviceStateChangeEvent, DeviceResponseEvent, DeviceRegisterEvent


def parse_envelope(data: bytes) -> message_pb2.Envelope:
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)
    return envelope


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


def msg_to_event(
    envelope: message_pb2.Envelope, writer: StreamWriter
) -> DeviceStateChangeEvent | DeviceResponseEvent | DeviceRegisterEvent | None:
    msg_type = envelope.WhichOneof("payload")

    if msg_type == "device_state_change":
        msg = envelope.device_state_change
        return DeviceStateChangeEvent(
            device_id=msg.device_id,
            writer=writer,
            timestamp=msg.timestamp,
            device_type=msg.device_type,
            parameters=dict(msg.parameters),
        )
    elif msg_type == "device_response":
        msg = envelope.device_response
        return DeviceResponseEvent(
            device_id=msg.device_id,
            writer=writer,
            timestamp=msg.timestamp,
            success=msg.success,
            message=msg.message,
        )
    elif msg_type == "device_register_req":
        msg = envelope.device_register_req
        return DeviceRegisterEvent(
            device_id=msg.device_id,
            writer=writer,
            device_type=msg.device_type,
            capabilities=dict(msg.capabilities),
            device_state=dict(msg.device_state),
            timestamp=msg.timestamp,
        )
    return None


def handle_message(envelope: message_pb2.Envelope):
    msg_type = envelope.WhichOneof("payload")

    if msg_type == "device_state_change":
        msg = envelope.device_state_change
        print(f"Device {msg.device_id} state change: {dict(msg.parameters)}")

    elif msg_type == "device_response":
        msg = envelope.device_response
        status = "OK" if msg.success else "FAILED"
        print(f"Device {msg.device_id} response: {status} - {msg.message}")

    else:
        print(f"Unknown message type: {msg_type}")

    return msg_type
