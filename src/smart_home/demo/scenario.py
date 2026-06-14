from __future__ import annotations

from datetime import datetime, timedelta, timezone

RECURRING_DEVICE_ID = 1
SIMULATION_DAYS = 10
START_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc)
AI_TICK_TIME = START_DATE + timedelta(days=SIMULATION_DAYS, hours=17)
DEMO_INITIAL_TIME = START_DATE + timedelta(days=SIMULATION_DAYS)
TASK_LOOKAHEAD_TIME = START_DATE + timedelta(days=SIMULATION_DAYS + 2)

DEMO_DEVICE_DEFINITIONS: list[tuple[int, str, dict[str, str], dict[str, str]]] = [
    (1, "entry_lamp", {"power": "on/off"}, {"power": "off"}),
    (2, "kitchen_lamp", {"power": "on/off"}, {"power": "off"}),
    (3, "desk_lamp", {"power": "on/off"}, {"power": "off"}),
    (4, "hall_motion_sensor", {"motion": "detected/clear"}, {"motion": "clear"}),
    (5, "bedroom_lamp", {"power": "on/off"}, {"power": "off"}),
    (6, "living_room_ac", {"mode": "off/cool/heat"}, {"mode": "off"}),
    (7, "garden_lamp", {"power": "on/off"}, {"power": "off"}),
    (8, "garage_door", {"state": "open/closed"}, {"state": "closed"}),
    (9, "bathroom_fan", {"power": "on/off"}, {"power": "off"}),
    (10, "thermostat", {"target_temperature": "16-26"}, {"target_temperature": "20"}),
]


def device_name(device_id: int) -> str:
    for did, name, _capabilities, _state in DEMO_DEVICE_DEFINITIONS:
        if did == device_id:
            return name
    return f"device_{device_id}"


def to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def format_timestamp(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def build_history_records(
    *,
    simulation_days: int = SIMULATION_DAYS,
    start_date: datetime = START_DATE,
) -> list[tuple[int, int, dict[str, str]]]:
    records: list[tuple[int, int, dict[str, str]]] = []

    for day in range(simulation_days):
        day_start = start_date + timedelta(days=day)
        day_records = [
            (RECURRING_DEVICE_ID, to_timestamp(day_start + timedelta(hours=18)), {"power": "on"}),
            (RECURRING_DEVICE_ID, to_timestamp(day_start + timedelta(hours=19)), {"power": "off"}),
            (2, to_timestamp(day_start + timedelta(hours=6 + day % 2)), {"power": "on"}),
            (2, to_timestamp(day_start + timedelta(hours=7 + day % 2)), {"power": "off"}),
            (3, to_timestamp(day_start + timedelta(hours=21, minutes=(day * 7) % 45)), {"power": "on"}),
            (3, to_timestamp(day_start + timedelta(hours=22, minutes=(day * 5) % 45)), {"power": "off"}),
            (4, to_timestamp(day_start + timedelta(hours=8 + day % 4)), {"motion": "detected"}),
            (4, to_timestamp(day_start + timedelta(hours=8 + day % 4, minutes=10)), {"motion": "clear"}),
            (5, to_timestamp(day_start + timedelta(hours=20 + day % 3)), {"power": "on"}),
            (5, to_timestamp(day_start + timedelta(hours=21 + day % 2)), {"power": "off"}),
            (6, to_timestamp(day_start + timedelta(hours=15 + day % 5)), {"mode": "cool"}),
            (6, to_timestamp(day_start + timedelta(hours=17 + day % 4)), {"mode": "off"}),
            (7, to_timestamp(day_start + timedelta(hours=16 + day % 3)), {"power": "on"}),
            (7, to_timestamp(day_start + timedelta(hours=23)), {"power": "off"}),
            (8, to_timestamp(day_start + timedelta(hours=7 + day % 2)), {"state": "open"}),
            (8, to_timestamp(day_start + timedelta(hours=7 + day % 2, minutes=5)), {"state": "closed"}),
            (9, to_timestamp(day_start + timedelta(hours=6, minutes=(day * 11) % 50)), {"power": "on"}),
            (9, to_timestamp(day_start + timedelta(hours=6, minutes=(day * 11) % 50 + 20)), {"power": "off"}),
            (10, to_timestamp(day_start + timedelta(hours=5)), {"target_temperature": str(19 + day % 4)}),
        ]
        records.extend(day_records)

    return records
