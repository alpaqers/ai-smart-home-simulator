from pathlib import Path
import sys
import asyncio


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from smart_home.client.controllers.event_handler import EventHandler


def test_event_is_dispatched_once_to_each_subscriber():
    async def scenario() -> None:
        bus = EventHandler()
        calls: list[tuple[str, str]] = []

        def sub_a(data: str) -> None:
            calls.append(("a", data))

        def sub_b(data: str) -> None:
            calls.append(("b", data))

        bus.subscribe(sub_a)
        bus.subscribe(sub_b)

        await bus.start()
        await bus.put_event("E1")
        await bus._queue.join()
        await bus.stop()

        assert calls.count(("a", "E1")) == 1
        assert calls.count(("b", "E1")) == 1
        assert len(calls) == 2

    asyncio.run(scenario())


def test_sync_and_async_subscribers_both_run():
    async def scenario() -> None:
        bus = EventHandler()
        calls: list[str] = []

        def sync_sub(data: str) -> None:
            calls.append(f"sync:{data}")

        async def async_sub(data: str) -> None:
            await asyncio.sleep(0)
            calls.append(f"async:{data}")

        bus.subscribe(sync_sub)
        bus.subscribe(async_sub)

        await bus.start()
        await bus.put_event("E2")
        await bus._queue.join()
        await bus.stop()

        assert "sync:E2" in calls
        assert "async:E2" in calls
        assert len(calls) == 2

    asyncio.run(scenario())


def test_stop_cancels_background_task_cleanly():
    async def scenario() -> None:
        bus = EventHandler()
        await bus.start()

        assert bus._task is not None
        assert not bus._task.done()

        await bus.stop()

        assert bus._task is None
        assert bus._running is False

    asyncio.run(scenario())
