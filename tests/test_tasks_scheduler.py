import pytest

from smart_home.server.tasks import ScheduledTask, TaskDatabase


@pytest.mark.asyncio
async def test_claim_keeps_task() -> None:
    # Checks that claiming returns the task ID,
    # marks the task as dispatched, and keeps it in the database.

    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    claimed_task_ids = await task_database.claim_due_task_ids(
        timestamp=100,
        max_delay_seconds=300,
    )

    assert claimed_task_ids == [1]

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.task_id == 1
    assert task.dispatched is True


@pytest.mark.asyncio
async def test_claim_once() -> None:
    # Checks that an already dispatched task
    # is not claimed again.

    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    first_claim = await task_database.claim_due_task_ids(
        timestamp=100,
        max_delay_seconds=300,
    )

    second_claim = await task_database.claim_due_task_ids(
        timestamp=101,
        max_delay_seconds=300,
    )

    assert first_claim == [1]
    assert second_claim == []

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.dispatched is True


@pytest.mark.asyncio
async def test_claim_skips_future() -> None:
    # Checks that a future task is not claimed.

    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    claimed_task_ids = await task_database.claim_due_task_ids(
        timestamp=50,
        max_delay_seconds=300,
    )

    assert claimed_task_ids == []

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.dispatched is False


@pytest.mark.asyncio
async def test_claim_skips_expired() -> None:
    # Checks that an expired task is not claimed.

    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    claimed_task_ids = await task_database.claim_due_task_ids(
        timestamp=401,
        max_delay_seconds=300,
    )

    assert claimed_task_ids == []

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.dispatched is False


@pytest.mark.asyncio
async def test_claim_many() -> None:
    # Checks that all due tasks are claimed
    # and future tasks are left untouched.

    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    await task_database.add_task(
        ScheduledTask(
            task_id=2,
            device_id=11,
            parameters={"temperature": "22"},
            time=120,
        )
    )

    await task_database.add_task(
        ScheduledTask(
            task_id=3,
            device_id=12,
            parameters={"power": "off"},
            time=200,
        )
    )

    claimed_task_ids = await task_database.claim_due_task_ids(
        timestamp=120,
        max_delay_seconds=300,
    )

    assert claimed_task_ids == [1, 2]

    task_1 = await task_database.get_by_task_id(1)
    task_2 = await task_database.get_by_task_id(2)
    task_3 = await task_database.get_by_task_id(3)

    assert task_1 is not None
    assert task_2 is not None
    assert task_3 is not None

    assert task_1.dispatched is True
    assert task_2.dispatched is True
    assert task_3.dispatched is False


@pytest.mark.asyncio
async def test_list_tasks_can_include_or_skip_dispatched_tasks() -> None:
    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=2,
            device_id=11,
            parameters={"temperature": "22"},
            time=120,
        )
    )
    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    await task_database.claim_due_task_ids(timestamp=100)

    all_tasks = await task_database.list_tasks()
    pending_tasks = await task_database.list_tasks(include_dispatched=False)

    assert [task.task_id for task in all_tasks] == [1, 2]
    assert all_tasks[0].dispatched is True
    assert [task.task_id for task in pending_tasks] == [2]


@pytest.mark.asyncio
async def test_reset_dispatched_flags_marks_tasks_pending_again() -> None:
    task_database = TaskDatabase()

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )
    await task_database.add_task(
        ScheduledTask(
            task_id=2,
            device_id=11,
            parameters={"power": "off"},
            time=200,
        )
    )

    await task_database.claim_due_task_ids(timestamp=100)

    reset_count = await task_database.reset_dispatched_flags()

    assert reset_count == 1
    tasks = await task_database.list_tasks()
    assert [task.dispatched for task in tasks] == [False, False]
