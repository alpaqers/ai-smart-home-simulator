class ResponseProcessor:
    async def handle(self, event) -> None:
        print(f"[ResponseProcessor] Received response from device {event.device_id}")