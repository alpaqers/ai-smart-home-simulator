import asyncio
from typing import Callable

class EventHandler:
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._subscribers: list[Callable] = []
        self._running = True
        self._task: asyncio.Task | None = None

    def subscribe(self, callback):
        """ DeviceStorage or AI"""
        self._subscribers.append(callback)

    async def put_event(self, data):
        """raw data"""
        await self._queue.put(data)


    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self.run(), name = "EventHandler")
    async def run(self):
        
        while self._running:
            try:
                event_data = await asyncio.wait_for( self._queue.get(), timeout=1.0)

                await asyncio.gather(
                    *[cb(event_data) for cb in self._subscribers],
                    return_exceptions=True
                )
                self._queue.task_done()
                for callback in self._subscribers:
                    callback(event_data)
                
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def stop(self):
        self._running = False
        if self._task:
            await self._task