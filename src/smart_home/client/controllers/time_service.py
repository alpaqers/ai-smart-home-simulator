from __future__ import annotations

import calendar
import time
from datetime import datetime, timedelta, timezone


def _datetime_to_epoch(dt: datetime) -> int:
    if dt.tzinfo is None:
        return int(calendar.timegm(dt.timetuple()))
    return int(dt.astimezone(timezone.utc).timestamp())


def _epoch_to_datetime(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(tzinfo=None)


class TimeService:
    def __init__(self) -> None:
        self._simulated: bool = False
        self._simulated_epoch: int = int(time.time())

    def use_real_time(self) -> None:
        """Switch to real system time."""
        self._simulated = False

    def use_simulated_epoch(self, epoch: int) -> None:
        """Set simulated time from a unix timestamp (UTC)."""
        self._simulated = True
        self._simulated_epoch = int(epoch)

    def use_simulated_time(self, start_time: datetime) -> None:
        """Set simulated time from a datetime (naive values treated as UTC)."""
        self._simulated = True
        self._simulated_epoch = _datetime_to_epoch(start_time)

    def make_time_shift(self, time_delta: timedelta) -> None:
        """Shift simulated time by given delta."""
        if self._simulated:
            self._simulated_epoch += int(time_delta.total_seconds())

    def now(self) -> datetime:
        """Returns current time - real or simulated (UTC wall clock when simulated)."""
        if self._simulated:
            return _epoch_to_datetime(self._simulated_epoch)
        return datetime.now()

    def now_as_timestamp(self) -> int:
        """Returns current time as int for protobuf."""
        if self._simulated:
            return self._simulated_epoch
        return int(time.time())

    def is_simulated(self) -> bool:
        """Returns True if using simulated time."""
        return self._simulated
