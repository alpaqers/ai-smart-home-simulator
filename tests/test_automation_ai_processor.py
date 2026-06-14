from unittest.mock import Mock

import pytest

from smart_home.server.ai.transport import AITransport
from smart_home.server.ai.types import AIPrompt
from smart_home.server.events import AITickEvent
from smart_home.server.processors.automation_ai import AutomationAIProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord
from smart_home.server.tasks import TaskDatabase


class FakeAITransport(AITransport):
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.prompts: list[AIPrompt] = []

    async def send(self, prompt: AIPrompt) -> dict[str, object]:
        self.prompts.append(prompt)
        return self.response


@pytest.mark.asyncio
async def test_automation_ai_processor_adds_task_from_timestamp() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    task_database = TaskDatabase()
    transport = FakeAITransport(
        {
            "text": "Turn on the entry lamp in the evening.",
            "automations": [
                {
                    "device_id": 1,
                    "parameters": {"power": "on"},
                    "timestamp": 1704132000,
                }
            ],
        }
    )

    await registry.register(
        RegisteredDevice(
            device_id=1,
            writer=Mock(),
            device_type="lamp",
            capabilities={"power": "on/off"},
            device_state={"power": "off"},
            timestamp=100,
        )
    )
    await history.append(
        StateChangeRecord(
            device_id=1,
            timestamp=1704128400,
            parameters={"power": "on"},
            device_type="lamp",
        )
    )

    processor = AutomationAIProcessor(
        registry,
        history,
        transport,
        task_database,
    )

    await processor.handle(AITickEvent(timestamp=1704128400))

    tasks = await task_database.get_due_tasks(1704132000)
    assert len(tasks) == 1
    assert tasks[0].device_id == 1
    assert tasks[0].parameters == {"power": "on"}
    assert tasks[0].time == 1704132000
    assert transport.prompts
    assert "current_time" in transport.prompts[0].messages[1]["content"]


@pytest.mark.asyncio
async def test_automation_ai_processor_does_not_add_duplicate_task() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    task_database = TaskDatabase()
    transport = FakeAITransport(
        {
            "automations": [
                {
                    "device_id": 1,
                    "parameters": {"power": "on"},
                    "timestamp": 200,
                }
            ],
        }
    )

    await registry.register(
        RegisteredDevice(
            device_id=1,
            writer=Mock(),
            device_type="lamp",
            capabilities={},
            device_state={},
            timestamp=100,
        )
    )

    processor = AutomationAIProcessor(
        registry,
        history,
        transport,
        task_database,
    )

    await processor.handle(AITickEvent(timestamp=100))
    await processor.handle(AITickEvent(timestamp=100))

    tasks = await task_database.get_due_tasks(200)
    assert len(tasks) == 1
    assert tasks[0].time == 200


@pytest.mark.asyncio
async def test_automation_ai_processor_skips_unregistered_device() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    task_database = TaskDatabase()
    transport = FakeAITransport(
        {
            "automations": [
                {
                    "device_id": 99,
                    "parameters": {"power": "on"},
                    "timestamp": 200,
                }
            ],
        }
    )
    processor = AutomationAIProcessor(
        registry,
        history,
        transport,
        task_database,
    )

    await processor.handle(AITickEvent(timestamp=100))

    assert await task_database.get_due_tasks(200) == []


@pytest.mark.asyncio
async def test_automation_ai_processor_skips_past_automation() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    task_database = TaskDatabase()
    transport = FakeAITransport(
        {
            "automations": [
                {
                    "device_id": 1,
                    "parameters": {"power": "on"},
                    "timestamp": 99,
                }
            ],
        }
    )

    await registry.register(
        RegisteredDevice(
            device_id=1,
            writer=Mock(),
            device_type="lamp",
            capabilities={"power": "on/off"},
            device_state={"power": "off"},
            timestamp=1,
        )
    )

    processor = AutomationAIProcessor(
        registry,
        history,
        transport,
        task_database,
    )

    await processor.handle(AITickEvent(timestamp=100))

    assert await task_database.list_tasks() == []
