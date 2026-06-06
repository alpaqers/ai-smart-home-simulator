from __future__ import annotations
from datetime import datetime, timedelta


class TimeService:
    def __init__(self) -> None:
        self._simulated: bool = False
        self._simulated_time: datetime = datetime.now()

    def use_real_time(self) -> None:
        """Switch to real system time."""
        self._simulated = False

    def use_simulated_time(self, start_time: datetime) -> None:
        """Switch to simulated time with given unix timestamp."""
        self._simulated = True
        self._simulated_time = start_time

    def make_time_shift(self, time_delta: timedelta) -> None:
        """Shift simulated time by given delta."""
        if self._simulated:
            self._simulated_time += time_delta
    
    def now(self) -> datetime:
        """Returns current time - real or simulated."""
        if self._simulated:
            return self._simulated_time
        return datetime.now()

    def now_as_timestamp(self) -> int:
        """Returns current time as int for protobuf."""
        return int(self.now().timestamp())
    
    def is_simulated(self) -> bool:
        """Returns True if using simulated time."""
        return self._simulated
