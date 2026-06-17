import pytest

from smart_home.server.daily_task_reset import DailyTaskReset
from smart_home.server.events import TickEvent
from smart_home.server.tasks import ScheduledTask, TaskDatabase


@pytest.mark.asyncio
async def test_daily_task_reset_resets_dispatched_tasks_on_date_change() -> None:
    task_database = TaskDatabase()
    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=7,
            parameters={"power": "on"},
            time=100,
        )
    )
    await task_database.claim_due_task_ids(timestamp=100)

    reset = DailyTaskReset(task_database)

    await reset.handle(TickEvent(timestamp=1704067200))
    assert (await task_database.get_by_task_id(1)).dispatched is True

    await reset.handle(TickEvent(timestamp=1704153600))
    assert (await task_database.get_by_task_id(1)).dispatched is False
