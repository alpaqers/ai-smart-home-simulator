from smart_home.proto.v1 import message_pb2


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
    return envelope.SerializeToString()


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
