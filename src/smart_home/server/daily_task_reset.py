from datetime import date, datetime, timezone

from smart_home.server.events import TickEvent
from smart_home.server.tasks import TaskDatabase


class DailyTaskReset:
    def __init__(self, task_database: TaskDatabase) -> None:
        self._task_database = task_database
        self._last_seen_date: date | None = None

    async def handle(self, event: TickEvent) -> None:
        current_date = datetime.fromtimestamp(event.timestamp, tz=timezone.utc).date()
        if self._last_seen_date is None:
            self._last_seen_date = current_date
            return
        if current_date != self._last_seen_date:
            count = await self._task_database.reset_dispatched_flags()
            print(f"[DailyTaskReset] Reset {count} task(s) at {current_date}")
            self._last_seen_date = current_date
