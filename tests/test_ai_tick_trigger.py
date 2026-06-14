from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.proto.v1 import message_pb2
from smart_home.server.event_bus import EventBus
from smart_home.server.events import AITickEvent, AITickRequestEvent
from smart_home.server.message_handler import decode_wire_message, msg_to_event, parse_envelope
from smart_home.server.processors.ai_tick_trigger import AITickTriggerProcessor
from smart_home.server.processors.automation_ai import AutomationAIProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_history import DeviceStateHistory
from smart_home.server.tasks import TaskDatabase
from smart_home.server.time_service import TimeService
from tests.test_automation_ai_processor import FakeAITransport


def test_msg_to_event_maps_ai_tick_request() -> None:
    writer = Mock()
    envelope = message_pb2.Envelope()
    envelope.ai_tick_request.SetInParent()
    event = msg_to_event(envelope, writer, "req-ai")
    assert isinstance(event, AITickRequestEvent)
    assert event.request_id == "req-ai"


@pytest.mark.asyncio
async def test_ai_tick_trigger_publishes_event_and_reports_added_tasks() -> None:
    bus = EventBus()
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    task_database = TaskDatabase()
    time_service = TimeService()
    time_service.use_simulated_epoch(100)
    writer = Mock()

    await registry.register(
        RegisteredDevice(
            device_id=1,
            writer=writer,
            device_type="entry_lamp",
            capabilities={"power": "on/off"},
            device_state={"power": "off"},
            timestamp=1,
        )
    )

    ai_processor = AutomationAIProcessor(
        registry,
        history,
        FakeAITransport(
            {
                "automations": [
                    {"device_id": 1, "parameters": {"power": "on"}, "timestamp": 200}
                ]
            }
        ),
        task_database,
    )
    await bus.subscribe(AITickEvent, ai_processor.handle)

    trigger = AITickTriggerProcessor(bus, task_database, time_service, ai_enabled=True)
    response_writer = Mock()
    response_writer.write = Mock()
    response_writer.drain = AsyncMock()

    await trigger.handle(AITickRequestEvent(request_id="req-1", writer=response_writer))

    sent_request_id, sent_proto_bytes = decode_wire_message(response_writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)
    resp = sent_envelope.ai_tick_resp
    assert sent_request_id == "req-1"
    assert resp.success is True
    assert resp.tasks_added == 1
