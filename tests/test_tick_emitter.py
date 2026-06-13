import asyncio

import pytest

from smart_home.server.event_bus import EventBus
from smart_home.server.events import AITickEvent, TickEvent
from smart_home.server.tick_emitter import TickEmitter


@pytest.mark.asyncio
async def test_emit_once_publishes_tick_event() -> None:
    bus = EventBus()
    events: list[TickEvent] = []

    async def handle_tick(event: TickEvent) -> None:
        events.append(event)

    await bus.subscribe(TickEvent, handle_tick)
    emitter = TickEmitter(bus, interval_seconds=1.0, time_provider=lambda: 123)

    event = await emitter.emit_once()

    assert event == TickEvent(timestamp=123)
    assert events == [event]


@pytest.mark.asyncio
async def test_start_emits_ticks_until_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    bus = EventBus()
    events: list[TickEvent] = []
    timestamp = 100

    def next_timestamp() -> int:
        nonlocal timestamp
        timestamp += 1
        return timestamp

    async def handle_tick(event: TickEvent) -> None:
        events.append(event)

    real_sleep = asyncio.sleep

    async def instant_sleep(_delay: float) -> None:
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", instant_sleep)

    await bus.subscribe(TickEvent, handle_tick)
    emitter = TickEmitter(bus, interval_seconds=0.01, time_provider=next_timestamp)

    emitter.start()
    await real_sleep(0.035)
    await emitter.stop()
    count_after_stop = len(events)
    await real_sleep(0.02)

    assert len(events) >= 2
    assert len(events) == count_after_stop
    assert [event.timestamp for event in events] == list(range(101, 101 + len(events)))


def test_tick_emitter_rejects_non_positive_interval() -> None:
    bus = EventBus()

    with pytest.raises(ValueError, match="greater than 0"):
        TickEmitter(bus, interval_seconds=0)


@pytest.mark.asyncio
async def test_emit_once_publishes_ai_tick_when_interval_is_due() -> None:
    bus = EventBus()
    tick_events: list[TickEvent] = []
    ai_tick_events: list[AITickEvent] = []
    timestamps = iter(
        [
            0,
            299,
            300,
            599,
            600,
        ]
    )

    async def handle_tick(event: TickEvent) -> None:
        tick_events.append(event)

    async def handle_ai_tick(event: AITickEvent) -> None:
        ai_tick_events.append(event)

    await bus.subscribe(TickEvent, handle_tick)
    await bus.subscribe(AITickEvent, handle_ai_tick)
    emitter = TickEmitter(
        bus,
        interval_seconds=300.0,
        ai_tick_interval_seconds=600.0,
        time_provider=lambda: next(timestamps),
    )

    await emitter.emit_once()
    await emitter.emit_once()
    await emitter.emit_once()
    await emitter.emit_once()
    await emitter.emit_once()

    assert tick_events == [
        TickEvent(timestamp=0),
        TickEvent(timestamp=300),
        TickEvent(timestamp=600),
    ]
    assert ai_tick_events == [
        AITickEvent(timestamp=0),
        AITickEvent(timestamp=600),
    ]


def test_tick_emitter_rejects_non_positive_ai_tick_interval() -> None:
    bus = EventBus()

    with pytest.raises(ValueError, match="AI tick interval"):
        TickEmitter(bus, interval_seconds=1.0, ai_tick_interval_seconds=0)
