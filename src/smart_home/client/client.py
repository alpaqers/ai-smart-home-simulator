from __future__ import annotations

from .models.connection_storage import ConnectionStorage
from .controllers.event_handler import EventHandler
from .controllers.event_router import ClientEventRouter
from .controllers.logger_controller import LoggerController
from .models.device_storage import DeviceStorage
from .views.cli import run_cli
from .controllers.logger_service import LoggerService
from .controllers.time_service import TimeService
from .views.web.runtime import run_web


async def start_client(frontend: str = "cli") -> None:

    bus = EventHandler()
    device_storage = DeviceStorage()
    connection_storage = ConnectionStorage()
    router = ClientEventRouter(device_storage)
    bus.subscribe(router.handle)
    await bus.start()

    logger_ctrl = LoggerController()
    await logger_ctrl.start()
    logger_ctrl.create_session()
    logger = LoggerService(logger_ctrl)
    time_service = TimeService()

    try:
        if frontend == "web":
            await run_web(logger, device_storage, connection_storage, bus)
        else:
            await run_cli(logger, device_storage, connection_storage, bus, time_service)
    finally:
        await bus.stop()
        await logger_ctrl.stop()
