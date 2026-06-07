import asyncio
from smart_home.server.connection_handler import handle_client
from smart_home.common.config_loader import HOST, PORT
from smart_home.server.event_bus import EventBus
from smart_home.server.events import (
    DeviceRegisterEvent,
    DeviceResponseEvent,
    DeviceStateChangeEvent,
    TimeShiftEvent,
)
from smart_home.server.processors import (
    RegisterProcessor,
    ResponseProcessor,
    StateChangeProcessor,
)
from smart_home.server.processors.time_shift import TimeShiftProcessor
from smart_home.server.registry import DeviceRegistry
from smart_home.server.state_history import DeviceStateHistory
from smart_home.server.time_service import TimeService


async def start_server() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    bus = EventBus()
    time_service = TimeService()

    register_processor = RegisterProcessor(registry)
    state_change_processor = StateChangeProcessor(registry, history)
    response_processor = ResponseProcessor()
    time_shift_processor = TimeShiftProcessor(time_service)

    await bus.subscribe(DeviceRegisterEvent, register_processor.handle)
    await bus.subscribe(DeviceStateChangeEvent, state_change_processor.handle)
    await bus.subscribe(DeviceResponseEvent, response_processor.handle)
    await bus.subscribe(TimeShiftEvent, time_shift_processor.handle)

    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, registry, bus),
        HOST,
        PORT,
    )
    print(f"Server started on: {HOST}:{PORT}")
    async with server:
        await server.serve_forever()
