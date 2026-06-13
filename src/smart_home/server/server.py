import asyncio

from smart_home.server.connection_handler import handle_client
from smart_home.common.config_loader import HOST, PORT, TICK_INTERVAL_SECONDS
from smart_home.server.event_bus import EventBus
from smart_home.server.scheduler import Scheduler
from smart_home.server.tasks import TaskDatabase
from smart_home.server.daily_task_reset import DailyTaskReset
from smart_home.server.events import (
    DeviceRegisterEvent,
    DeviceStateChangeRespEvent,
    DeviceStateChangeEvent,
    TaskDueEvent,
    TickEvent,
    TimeShiftEvent,
)
from smart_home.server.processors import (
    RegisterProcessor,
    ResponseProcessor,
    StateChangeProcessor,
    StateUpdateProcessor,
)
from smart_home.server.processors.time_shift import TimeShiftProcessor
from smart_home.server.registry import DeviceRegistry
from smart_home.server.state_history import DeviceStateHistory
from smart_home.server.state_update_sender import StateUpdateSender
from smart_home.server.tick_emitter import TickEmitter
from smart_home.server.time_service import TimeService

async def start_server() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    bus = EventBus()
    time_service = TimeService()

    task_database = TaskDatabase()

    scheduler = Scheduler(
        event_bus=bus,
        task_database=task_database,
        max_delay_seconds=300,
    )
    await scheduler.start()

    register_processor = RegisterProcessor(registry, time_service)
    state_change_processor = StateChangeProcessor(registry, history, time_service)
    response_processor = ResponseProcessor()
    time_shift_processor = TimeShiftProcessor(time_service)
    state_update_sender = StateUpdateSender(registry)
    state_update_processor = StateUpdateProcessor(state_update_sender, task_database)
    daily_task_reset = DailyTaskReset(task_database)

    await bus.subscribe(DeviceRegisterEvent, register_processor.handle)
    await bus.subscribe(DeviceStateChangeEvent, state_change_processor.handle)
    await bus.subscribe(DeviceStateChangeRespEvent, response_processor.handle)
    await bus.subscribe(TimeShiftEvent, time_shift_processor.handle)
    await bus.subscribe(TaskDueEvent, state_update_processor.handle)
    await bus.subscribe(TickEvent, daily_task_reset.handle)

    tick_emitter = TickEmitter(
        bus,
        interval_seconds=TICK_INTERVAL_SECONDS,
        time_service=time_service,
    )
    tick_emitter.start()

    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, registry, bus),
        HOST,
        PORT,
    )
    print(f"Server started on: {HOST}:{PORT}")

    try:
        async with server:
            await server.serve_forever()
    finally:
        await tick_emitter.stop()
