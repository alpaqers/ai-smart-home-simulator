from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smart_home.common.config_loader import (
    AI_ENDPOINT,
    AI_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from smart_home.server.ai.transport import GeminiAITransport, HttpAITransport
from smart_home.server.events import AITickEvent, TimeShiftEvent
from smart_home.server.processors.automation_ai import AutomationAIProcessor
from smart_home.server.processors.time_shift import TimeShiftProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord
from smart_home.server.tasks import ScheduledTask, TaskDatabase
from smart_home.server.time_service import TimeService


RECURRING_DEVICE_ID = 1
SIMULATION_DAYS = 10
START_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc)
AI_TICK_TIME = START_DATE + timedelta(days=SIMULATION_DAYS, hours=17)
NEXT_ON_TIME = START_DATE + timedelta(days=SIMULATION_DAYS, hours=18)
NEXT_OFF_TIME = START_DATE + timedelta(days=SIMULATION_DAYS, hours=19)
TASK_LOOKAHEAD_TIME = START_DATE + timedelta(days=SIMULATION_DAYS + 2)


DEVICE_DEFINITIONS = [
    ("entry_lamp", {"power": "on/off"}, {"power": "off"}),
    ("kitchen_lamp", {"power": "on/off"}, {"power": "off"}),
    ("desk_lamp", {"power": "on/off"}, {"power": "off"}),
    ("hall_motion_sensor", {"motion": "detected/clear"}, {"motion": "clear"}),
    ("bedroom_lamp", {"power": "on/off"}, {"power": "off"}),
    ("living_room_ac", {"mode": "off/cool/heat"}, {"mode": "off"}),
    ("garden_lamp", {"power": "on/off"}, {"power": "off"}),
    ("garage_door", {"state": "open/closed"}, {"state": "closed"}),
    ("bathroom_fan", {"power": "on/off"}, {"power": "off"}),
    ("thermostat", {"target_temperature": "16-26"}, {"target_temperature": "20"}),
]


def to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def format_timestamp(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


class FakeWriter:
    def __init__(self) -> None:
        self.writes: list[bytes] = []

    def write(self, data: bytes) -> None:
        self.writes.append(data)

    async def drain(self) -> None:
        return None


async def register_devices(registry: DeviceRegistry, writer: FakeWriter) -> None:
    registered_at = to_timestamp(START_DATE - timedelta(days=1))

    for index, (device_type, capabilities, state) in enumerate(
        DEVICE_DEFINITIONS,
        start=1,
    ):
        await registry.register(
            RegisteredDevice(
                device_id=index,
                writer=writer,
                device_type=device_type,
                capabilities=capabilities,
                device_state=state,
                timestamp=registered_at,
            )
        )


async def append_history(history: DeviceStateHistory) -> int:
    record_count = 0

    for day in range(SIMULATION_DAYS):
        day_start = START_DATE + timedelta(days=day)

        records = [
            (
                RECURRING_DEVICE_ID,
                day_start + timedelta(hours=18),
                {"power": "on"},
            ),
            (
                RECURRING_DEVICE_ID,
                day_start + timedelta(hours=19),
                {"power": "off"},
            ),
            (2, day_start + timedelta(hours=6 + day % 2), {"power": "on"}),
            (2, day_start + timedelta(hours=7 + day % 2), {"power": "off"}),
            (3, day_start + timedelta(hours=21, minutes=(day * 7) % 45), {"power": "on"}),
            (3, day_start + timedelta(hours=22, minutes=(day * 5) % 45), {"power": "off"}),
            (4, day_start + timedelta(hours=8 + day % 4), {"motion": "detected"}),
            (4, day_start + timedelta(hours=8 + day % 4, minutes=10), {"motion": "clear"}),
            (5, day_start + timedelta(hours=20 + day % 3), {"power": "on"}),
            (5, day_start + timedelta(hours=21 + day % 2), {"power": "off"}),
            (6, day_start + timedelta(hours=15 + day % 5), {"mode": "cool"}),
            (6, day_start + timedelta(hours=17 + day % 4), {"mode": "off"}),
            (7, day_start + timedelta(hours=16 + day % 3), {"power": "on"}),
            (7, day_start + timedelta(hours=23), {"power": "off"}),
            (8, day_start + timedelta(hours=7 + day % 2), {"state": "open"}),
            (8, day_start + timedelta(hours=7 + day % 2, minutes=5), {"state": "closed"}),
            (9, day_start + timedelta(hours=6, minutes=(day * 11) % 50), {"power": "on"}),
            (9, day_start + timedelta(hours=6, minutes=(day * 11) % 50 + 20), {"power": "off"}),
            (10, day_start + timedelta(hours=5), {"target_temperature": str(19 + day % 4)}),
        ]

        for device_id, event_time, parameters in records:
            await history.append(
                StateChangeRecord(
                    device_id=device_id,
                    timestamp=to_timestamp(event_time),
                    parameters=parameters,
                    device_type=device_id,
                )
            )
            record_count += 1

    return record_count


async def shift_time(time_service: TimeService, writer: FakeWriter) -> None:
    await TimeShiftProcessor(time_service).handle(
        TimeShiftEvent(
            request_id="script-time-shift",
            writer=writer,
            year=AI_TICK_TIME.year,
            month=AI_TICK_TIME.month,
            day=AI_TICK_TIME.day,
            hour=AI_TICK_TIME.hour,
            minute=AI_TICK_TIME.minute,
            second=AI_TICK_TIME.second,
        )
    )


def print_task(task: ScheduledTask) -> None:
    print(
        "  "
        f"task_id={task.task_id} "
        f"device_id={task.device_id} "
        f"time={format_timestamp(task.time)} "
        f"parameters={task.parameters}"
    )


def build_ai_transport() -> GeminiAITransport | HttpAITransport:
    provider = AI_PROVIDER.lower()

    if provider in {"", "gemini"}:
        if not GEMINI_API_KEY:
            raise SystemExit(
                "Missing GEMINI_API_KEY. Add it to .env or export it before running."
            )
        return GeminiAITransport(
            GEMINI_API_KEY,
            model=GEMINI_MODEL,
            timeout=60.0,
        )

    if provider == "http":
        if not AI_ENDPOINT:
            raise SystemExit(
                "AI_PROVIDER=http requires AI_ENDPOINT in .env or config.toml."
            )
        return HttpAITransport(AI_ENDPOINT, timeout=60.0)

    raise SystemExit(f"Unsupported AI_PROVIDER={AI_PROVIDER!r}")


async def main() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    task_database = TaskDatabase()
    time_service = TimeService()
    writer = FakeWriter()

    await register_devices(registry, writer)
    record_count = await append_history(history)
    await shift_time(time_service, writer)

    transport = build_ai_transport()
    processor = AutomationAIProcessor(
        registry=registry,
        history=history,
        transport=transport,
        task_database=task_database,
    )
    try:
        await processor.handle(AITickEvent(timestamp=time_service.now_as_timestamp()))
    finally:
        await transport.aclose()

    generated_tasks = sorted(
        await task_database.get_due_tasks(to_timestamp(TASK_LOOKAHEAD_TIME)),
        key=lambda task: (task.time, task.device_id, repr(task.parameters)),
    )

    print()
    print("Simulation summary")
    print(f"  devices={len(DEVICE_DEFINITIONS)}")
    print(f"  simulated_days={SIMULATION_DAYS}")
    print(f"  state_history_records={record_count}")
    print(f"  ai_tick={format_timestamp(time_service.now_as_timestamp())}")
    print(f"  ai_provider={AI_PROVIDER or 'gemini'}")
    if AI_PROVIDER.lower() in {"", "gemini"}:
        print(f"  gemini_model={GEMINI_MODEL}")

    print()
    print("Generated automations")
    if generated_tasks:
        for task in generated_tasks:
            print_task(task)
    else:
        print("  none")
        raise SystemExit("FAIL: no automation tasks were generated")

    recurring_device_tasks = [
        task
        for task in generated_tasks
        if task.device_id == RECURRING_DEVICE_ID
    ]
    if not recurring_device_tasks:
        raise SystemExit(
            "FAIL: AI did not generate an automation for the recurring entry lamp"
        )

    print()
    print("PASS: AI processor generated automations using the configured AI API")


if __name__ == "__main__":
    asyncio.run(main())
