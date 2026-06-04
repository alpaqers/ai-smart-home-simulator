import pytest

from smart_home.server.events import TaskDueEvent
from smart_home.server.tasks import ScheduledTask, TaskDatabase


@pytest.mark.asyncio
async def test_add_task_returns_false_for_duplicate_task_id() -> None:
    database = TaskDatabase()
    task = ScheduledTask(
        task_id=1,
        device_id=10,
        parameters={"power": "ON"},
        time=100,
    )

    assert await database.add_task(task) is True
    assert await database.add_task(task) is False

    stored = await database.get_by_task_id(1)
    assert stored == task


@pytest.mark.asyncio
async def test_get_due_tasks_returns_tasks_due_at_or_before_timestamp() -> None:
    database = TaskDatabase()
    due_task = ScheduledTask(
        task_id=1,
        device_id=1,
        parameters={"temperature": "22"},
        time=100,
    )
    later_task = ScheduledTask(
        task_id=2,
        device_id=2,
        parameters={"power": "OFF"},
        time=101,
    )

    await database.add_task(due_task)
    await database.add_task(later_task)

    assert await database.get_due_tasks(100) == [due_task]


@pytest.mark.asyncio
async def test_pop_due_tasks_removes_returned_tasks() -> None:
    database = TaskDatabase()
    due_task = ScheduledTask(
        task_id=1,
        device_id=1,
        parameters={"power": "ON"},
        time=100,
    )
    later_task = ScheduledTask(
        task_id=2,
        device_id=2,
        parameters={"power": "OFF"},
        time=200,
    )

    await database.add_task(due_task)
    await database.add_task(later_task)

    due_tasks = await database.pop_due_tasks(150)

    assert due_tasks == [due_task]
    assert await database.get_by_task_id(1) is None
    assert await database.get_by_task_id(2) == later_task
    assert await database.pop_due_tasks(150) == []


@pytest.mark.asyncio
async def test_remove_task_returns_whether_task_existed() -> None:
    database = TaskDatabase()
    task = ScheduledTask(
        task_id=1,
        device_id=10,
        parameters={},
        time=100,
    )

    await database.add_task(task)

    assert await database.remove_task(1) is True
    assert await database.remove_task(1) is False


@pytest.mark.asyncio
async def test_task_parameters_are_copied_at_storage_boundaries() -> None:
    database = TaskDatabase()
    parameters = {"power": "ON"}
    task = ScheduledTask(
        task_id=1,
        device_id=10,
        parameters=parameters,
        time=100,
    )

    await database.add_task(task)
    parameters["power"] = "OFF"

    stored = await database.get_by_task_id(1)
    assert stored is not None
    assert stored.parameters == {"power": "ON"}

    stored.parameters["power"] = "DIMMED"

    stored_again = await database.get_by_task_id(1)
    assert stored_again is not None
    assert stored_again.parameters == {"power": "ON"}


def test_task_due_event_carries_task_id() -> None:
    assert TaskDueEvent(task_id=1).task_id == 1