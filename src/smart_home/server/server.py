import asyncio

from smart_home.common.config import config
from smart_home.server.connection_handler import handle_client
from smart_home.server.event_bus import EventBus
from smart_home.server.events import (
    DeviceRegisterEvent,
    DeviceResponseEvent,
    DeviceStateChangeEvent,
)
from smart_home.server.processors import (
    RegisterProcessor,
    ResponseProcessor,
    StateChangeProcessor,
)
from smart_home.server.registry import DeviceRegistry
from smart_home.server.state_history import DeviceStateHistory


async def start_server() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    bus = EventBus()

    register_processor = RegisterProcessor(registry)
    state_change_processor = StateChangeProcessor(registry, history)
    response_processor = ResponseProcessor()

    await bus.subscribe(DeviceRegisterEvent, register_processor.handle)
    await bus.subscribe(DeviceStateChangeEvent, state_change_processor.handle)
    await bus.subscribe(DeviceResponseEvent, response_processor.handle)

    #moved from main_server.py
    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, registry, bus),
        config.host,
        config.port,
    )

    print(f"Server started on {config.host}:{config.port}")

    async with server:
        await server.serve_forever()