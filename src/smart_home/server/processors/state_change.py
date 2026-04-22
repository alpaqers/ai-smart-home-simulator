from smart_home.server.registry import DeviceRegistry
from smart_home.server.events import DeviceStateChangeEvent
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord

class StateChangeProcessor:
    def __init__(self, registry: DeviceRegistry, history: DeviceStateHistory) -> None:
        self._registry = registry
        self._history = history
    
    async def handle(self, event: DeviceStateChangeEvent) -> None:
        if not await self._registry.is_registered(event.device_id):
            print(f"[StateChangeProcessor] Device {event.device_id} not registered")
            return

        record = StateChangeRecord(
            device_id=event.device_id,
            timestamp=event.timestamp,
            parameters=dict(event.parameters),
            device_type=event.device_type,
        )
        await self._history.append(record)
        print(f"[StateChangeProcessor] Recorded state change for device {event.device_id}: {event.parameters!r}")