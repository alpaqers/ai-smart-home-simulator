from __future__ import annotations
from time import time


class TimeService:
    def __init__(self) -> None:
        self._simulated: bool = False
        self._simulated_time: int = 0

    def use_real_time(self) -> None:
        """Switch to real system time."""
        self._simulated = False

    def use_simulated_time(self, start_time: int) -> None:
        """Switch to simulated time with given unix timestamp."""
        self._simulated = True
        self._simulated_time = start_time

    def now(self) -> int:
        """Returns current time — real or simulated."""
        if self._simulated:
            return self._simulated_time
        return int(time())
    
    def is_simulated(self) -> bool:
        """Returns True if using simulated time."""
        return self._simulated