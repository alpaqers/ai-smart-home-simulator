import asyncio


from smart_home.server.connection_handler import handle_client
from smart_home.common.config_loader import HOST, PORT, TICK_INTERVAL_SECONDS
from smart_home.server.event_bus import EventBus
from smart_home.server.scheduler import Scheduler
from smart_home.server.tasks import TaskDatabase
from smart_home.server.events import (
    DeviceRegisterEvent,
    DeviceStateChangeRespEvent,
    DeviceStateChangeEvent,
)
from smart_home.server.processors import (
    RegisterProcessor,
    ResponseProcessor,
    StateChangeProcessor,
)
from smart_home.server.registry import DeviceRegistry
from smart_home.server.state_history import DeviceStateHistory
from smart_home.server.tick_emitter import TickEmitter

async def start_server() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    bus = EventBus()

    task_database = TaskDatabase()

    scheduler = Scheduler(
        event_bus=bus,
        task_database=task_database,
        max_delay_seconds=300,
    )
    await scheduler.start()

    register_processor = RegisterProcessor(registry)
    state_change_processor = StateChangeProcessor(registry, history)
    response_processor = ResponseProcessor()

    await bus.subscribe(DeviceRegisterEvent, register_processor.handle)
    await bus.subscribe(DeviceStateChangeEvent, state_change_processor.handle)
    await bus.subscribe(DeviceStateChangeRespEvent, response_processor.handle)

    tick_emitter = TickEmitter(bus, interval_seconds=TICK_INTERVAL_SECONDS)
    tick_emitter.start()

    #moved from main_server.py
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
