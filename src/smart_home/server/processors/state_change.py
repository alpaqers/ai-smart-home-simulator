class StateChangeProcessor:
    async def handle(self, event) -> None:
        print(f"[StateChangeProcessor] Received state change from device {event.device_id}")