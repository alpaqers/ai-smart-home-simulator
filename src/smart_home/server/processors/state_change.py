from smart_home.server.registry import DeviceRegistry
from smart_home.server.events import DeviceStateChangeEvent

class StateChangeProcessor:
    def __init__(self, registry: DeviceRegistry) -> None:
        self._registry = registry
    
    async def handle(self, event: DeviceStateChangeEvent) -> None:
        success = await self._registry.update_state(
            device_id=event.device_id,
            parameters=event.parameters,
            timestamp=event.timestamp,
        )

        if not success:
            print(f"[StateChangeProcessor] Device {event.device_id} not registered")
            return

        print(f"[StateChangeProcessor] Updated device {event.device_id}: {event.parameters!r}")