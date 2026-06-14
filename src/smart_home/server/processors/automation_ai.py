from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from smart_home.server.ai.transport import AITransport
from smart_home.server.ai.types import (
    AIContext,
    AIPrompt,
    AIResponse,
    AutomationSuggestion,
)
from smart_home.server.events import AITickEvent
from smart_home.server.processors.ai_processor import BaseAIProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord
from smart_home.server.tasks import ScheduledTask, TaskDatabase


class AutomationAIProcessor(BaseAIProcessor):
    def __init__(
        self,
        registry: DeviceRegistry,
        history: DeviceStateHistory,
        transport: AITransport,
        task_database: TaskDatabase,
    ) -> None:
        super().__init__(registry, history, transport)
        self._task_database = task_database
        self._current_tick_timestamp: int | None = None

    async def handle(self, event: AITickEvent) -> None:
        self._current_tick_timestamp = event.timestamp
        try:
            response = await self.run()
            added_count = 0

            for automation in response.automations:
                if not await self._registry.is_registered(automation.device_id):
                    continue

                if automation.timestamp <= event.timestamp:
                    continue

                task = ScheduledTask(
                    task_id=self._make_task_id(
                        automation.device_id,
                        automation.timestamp,
                        automation.parameters,
                    ),
                    device_id=automation.device_id,
                    parameters=automation.parameters,
                    time=automation.timestamp,
                )

                if await self._task_database.add_task(task):
                    added_count += 1

            print(f"[AutomationAIProcessor] Added {added_count} automation tasks")
        except Exception as e:
            print(f"[AutomationAIProcessor] Failed to process AI tick: {e}")
        finally:
            self._current_tick_timestamp = None

    async def gather_context(self) -> AIContext:
        devices = await self._registry.all_devices()
        history = await self._history.all_history()
        return AIContext(devices=devices, history=history)

    def build_prompt(self, context: AIContext) -> AIPrompt:
        current_timestamp = self._current_tick_timestamp
        payload = {
            "current_time": (
                _timestamp_to_prompt_data(current_timestamp)
                if current_timestamp is not None
                else None
            ),
            "devices": [_device_to_prompt_data(device) for device in context.devices],
            "history": {
                str(device_id): [
                    _record_to_prompt_data(record)
                    for record in records
                ]
                for device_id, records in context.history.items()
            },
        }

        return AIPrompt(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze smart-home device state history and propose "
                        "useful automations. Return JSON only. Prefer simple "
                        "automations for clear recurring patterns, and ignore "
                        "noisy or inconsistent behavior."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Suggest automations based on recurring device usage. "
                        "Return an object with an automations array. Each automation "
                        "must contain device_id, parameters, and timestamp as a "
                        "future unix timestamp in seconds, strictly after "
                        "current_time.timestamp. For an on/off pattern, return "
                        "separate automations for the on and off actions. "
                        "Return at most 5 automations. "
                        f"Data: {json.dumps(payload, sort_keys=True)}"
                    ),
                },
            ],
            parameters={
                "response_format": {"type": "json_object"},
            },
        )

    def parse_response(self, raw: dict[str, object]) -> AIResponse:
        automations_raw = raw.get("automations", [])
        if not isinstance(automations_raw, list):
            raise ValueError("AI response field 'automations' must be a list")

        automations = [
            self._parse_automation(item)
            for item in automations_raw
        ]

        text = raw.get("text", "")
        return AIResponse(
            text=text if isinstance(text, str) else "",
            raw=raw,
            automations=automations,
        )

    def _parse_automation(self, raw: object) -> AutomationSuggestion:
        if not isinstance(raw, dict):
            raise ValueError("Automation suggestion must be an object")

        device_id = raw.get("device_id")
        if not isinstance(device_id, int):
            raise ValueError("Automation suggestion requires integer device_id")

        parameters = raw.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError("Automation suggestion requires parameters object")

        parsed_parameters = {
            str(key): str(value)
            for key, value in parameters.items()
        }

        timestamp = raw.get("timestamp")
        if not isinstance(timestamp, int):
            raise ValueError("Automation timestamp must be an integer")

        return AutomationSuggestion(
            device_id=device_id,
            parameters=parsed_parameters,
            timestamp=timestamp,
        )

    def _make_task_id(
        self,
        device_id: int,
        task_time: int,
        parameters: dict[str, str],
    ) -> int:
        payload = json.dumps(
            {
                "device_id": device_id,
                "time": task_time,
                "parameters": parameters,
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(payload.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big", signed=False)


def _device_to_prompt_data(device: RegisteredDevice) -> dict[str, object]:
    return {
        "device_id": device.device_id,
        "device_type": device.device_type,
        "capabilities": dict(device.capabilities),
        "device_state": dict(device.device_state),
        "registered_at": device.timestamp,
    }


def _record_to_prompt_data(record: StateChangeRecord) -> dict[str, object]:
    return {
        "device_id": record.device_id,
        "timestamp": record.timestamp,
        "timestamp_iso": _timestamp_to_iso(record.timestamp),
        "parameters": dict(record.parameters),
        "device_type": record.device_type,
    }


def _timestamp_to_prompt_data(timestamp: int) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "timestamp_iso": _timestamp_to_iso(timestamp),
    }


def _timestamp_to_iso(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
