import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable, Type


EventHandler = Callable[[Any], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type, list[EventHandler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: Type, handler: EventHandler) -> None:
        async with self._lock:
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    async def publish(self, event: Any) -> None:
        async with self._lock:
            handlers = list(self._subscribers.get(type(event), []))

        if not handlers:
            print(f"[EventBus] No handlers for {type(event).__name__}")
            return

        await asyncio.gather(*(handler(event) for handler in handlers))