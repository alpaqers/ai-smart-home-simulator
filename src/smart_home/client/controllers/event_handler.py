import asyncio
import inspect
from typing import Any, Callable

class EventHandler:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[Any] = asyncio.Queue()
        self._subscribers: list[Callable[[Any], Any]] = []
        self._running = False
        self._task: asyncio.Task | None = None

    def subscribe(self, callback: Callable[[Any], Any]) -> None:
        """Register sync or async callback for incoming events."""
        self._subscribers.append(callback)

    async def put_event(self, data: Any) -> None:
        """Push raw event data into the internal queue."""
        await self._queue.put(data)

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._running = True
        self._task = asyncio.create_task(self.run(), name="EventHandler")

    async def run(self) -> None:
        try:
            while self._running:
                event_data = await self._queue.get()
                try:
                    for callback in self._subscribers:
                        result = callback(event_data)
                        if inspect.isawaitable(result):
                            await result
                finally:
                    self._queue.task_done()
        except asyncio.CancelledError:
            raise

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None