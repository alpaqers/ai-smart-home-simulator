import base64
from asyncio import StreamWriter

from smart_home.proto.v1 import message_pb2
from smart_home.server.events import (
    AITickRequestEvent,
    DeviceStateChangeEvent,
    DeviceStateChangeRespEvent,
    DeviceRegisterEvent,
    TaskListRequestEvent,
    TimeShiftEvent,
)

def decode_wire_message(raw: bytes) -> tuple[str, bytes]:
    line = raw.decode("utf-8").strip()
    request_id, payload_b64 = line.split("|", 1)
    proto_bytes = base64.b64decode(payload_b64)
    return request_id, proto_bytes


def encode_wire_message(request_id: str, proto_bytes: bytes) -> bytes:
    payload_b64 = base64.b64encode(proto_bytes).decode("utf-8")
    return f"{request_id}|{payload_b64}\n".encode("utf-8")


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
    elif isinstance(message, message_pb2.TaskListRequest):
        envelope.task_list_request.CopyFrom(message)
    elif isinstance(message, message_pb2.TaskListResp):
        envelope.task_list_resp.CopyFrom(message)
    elif isinstance(message, message_pb2.AITickRequest):
        envelope.ai_tick_request.CopyFrom(message)
    elif isinstance(message, message_pb2.AITickResp):
        envelope.ai_tick_resp.CopyFrom(message)
    else:
        raise ValueError(f"Unsupported message type: {type(message).__name__}")
    
    return envelope.SerializeToString()


def msg_to_event(
    envelope: message_pb2.Envelope, writer: StreamWriter, request_id: str = ""
) -> DeviceStateChangeEvent | DeviceStateChangeRespEvent | DeviceRegisterEvent | TimeShiftEvent | TaskListRequestEvent | AITickRequestEvent | None:
    msg_type = envelope.WhichOneof("payload")

    if msg_type == "device_state_change":
        msg = envelope.device_state_change
        return DeviceStateChangeEvent(
            device_id=msg.device_id,
            writer=writer,
            request_id=request_id,
            timestamp=msg.timestamp,
            device_type=msg.device_type,
            parameters=dict(msg.parameters),
        )
    elif msg_type == "device_state_change_resp":
        msg = envelope.device_state_change_resp
        return DeviceStateChangeRespEvent(
            device_id=msg.device_id,
            writer=writer,
            request_id=request_id,
            timestamp=msg.timestamp,
            success=msg.success,
            message=msg.message,
        )
    elif msg_type == "device_register_req":
        msg = envelope.device_register_req
        return DeviceRegisterEvent(
            device_id=msg.device_id,
            writer=writer,
            request_id=request_id,
            device_type=msg.device_type,
            capabilities=dict(msg.capabilities),
            device_state=dict(msg.device_state),
            timestamp=msg.timestamp,
        )
    elif msg_type == "time_shift_request":
        msg = envelope.time_shift_request
        return TimeShiftEvent(
            request_id=request_id,
            writer=writer,
            year=msg.year,
            month=msg.month,
            day=msg.day,
            hour=msg.hour,
            minute=msg.minute,
            second=msg.second,
        )
    elif msg_type == "task_list_request":
        msg = envelope.task_list_request
        return TaskListRequestEvent(
            request_id=request_id,
            writer=writer,
            include_dispatched=msg.include_dispatched,
        )
    elif msg_type == "ai_tick_request":
        return AITickRequestEvent(
            request_id=request_id,
            writer=writer,
        )
    return None


def handle_message(envelope: message_pb2.Envelope):
    msg_type = envelope.WhichOneof("payload")

    if msg_type == "device_state_change":
        msg = envelope.device_state_change
        print(f"Device {msg.device_id} state change: {dict(msg.parameters)}")

    elif msg_type == "device_state_change_resp":
        msg = envelope.device_state_change_resp
        status = "OK" if msg.success else "FAILED"
        print(f"Device {msg.device_id} state change response: {status} - {msg.message}")

    elif msg_type == "time_shift_request":
        msg = envelope.time_shift_request
        print(f"Time shift request: {msg.year}-{msg.month}-{msg.day} {msg.hour}:{msg.minute}:{msg.second}")

    elif msg_type == "time_shift_resp":
        msg = envelope.time_shift_resp
        status = "OK" if msg.success else "FAILED"
        detail = msg.cause if msg.cause else str(msg.timestamp)
        print(f"Time shift response: {status} - {detail}")

    elif msg_type == "task_list_request":
        msg = envelope.task_list_request
        print(f"Task list request: include_dispatched={msg.include_dispatched}")

    elif msg_type == "task_list_resp":
        msg = envelope.task_list_resp
        status = "OK" if msg.success else "FAILED"
        print(f"Task list response: {status} - {len(msg.tasks)} tasks")

    elif msg_type == "ai_tick_request":
        print("AI tick request received")

    elif msg_type == "ai_tick_resp":
        msg = envelope.ai_tick_resp
        status = "OK" if msg.success else "FAILED"
        detail = msg.cause if msg.cause else f"tasks_added={msg.tasks_added}"
        print(f"AI tick response: {status} - {detail}")

    else:
        print(f"Unknown message type: {msg_type}")

    return msg_type
