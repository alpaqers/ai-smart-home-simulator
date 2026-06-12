from __future__ import annotations
from datetime import datetime
from smart_home.server.time_service import TimeService
from smart_home.server.events import TimeShiftEvent


class TimeShiftProcessor:
    def __init__(self, time_service: TimeService) -> None:
        self._time_service = time_service

    async def handle(self, event: TimeShiftEvent) -> None:
        """Receives TimeShiftRequest and sets server time to new datetime."""
        new_time = datetime(
            year=event.year,
            month=event.month,
            day=event.day,
            hour=event.hour,
            minute=event.minute,
            second=event.second,
        )
        self._time_service.use_simulated_time(new_time)
        print(f"[TimeShiftProcessor] Server time set to: {new_time}")
