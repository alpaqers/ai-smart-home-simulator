from __future__ import annotations
from datetime import datetime, timedelta


class TimeService:
    def __init__(self) -> None:
        self._simulated: bool = False
        self._simulated_time: datetime = datetime.now()

    def use_real_time(self) -> None:
        """Switch to real system time."""
        self._simulated = False

    def use_simulated_time(self, new_time: datetime) -> None:
        """Set simulated time to given datetime."""
        self._simulated = True
        self._simulated_time = new_time

    def make_time_shift(self, time_delta: timedelta) -> None:
        """Shift simulated time by given delta."""
        if self._simulated:
            self._simulated_time += time_delta

    def now(self) -> datetime:
        """Returns current time — real or simulated."""
        if self._simulated:
            return self._simulated_time
        return datetime.now()

    def now_as_timestamp(self) -> int:
        """Returns current time as unix timestamp for protobuf."""
        return int(self.now().timestamp())

    def advance_seconds(self, seconds: float) -> None:
        """Advance simulated clock by the given interval (no-op in real-time mode)."""
        if self._simulated:
            self._simulated_time += timedelta(seconds=seconds)

    def is_simulated(self) -> bool:
        """Returns True if using simulated time."""
        return self._simulated
