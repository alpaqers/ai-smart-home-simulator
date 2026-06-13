from __future__ import annotations

from models.connection_storage import ConnectionStorage
from views.web.runtime import run_web
from ..client.controllers.event_handler import EventHandler
from ..client.controllers.event_router import ClientEventRouter
from ..client.controllers.logger_controller import LoggerController
from ..client.views.cli import run_cli
from ..client.controllers.logger_service import LoggerService
from ..client.controllers.persistence import load_from_file
from ..client.controllers.time_service import TimeService


async def start_client(frontend: str = "cli") -> None:

    time_service = TimeService()
    bus = EventHandler()
    device_storage = load_from_file(time_service)
    connection_storage = ConnectionStorage()
    router = ClientEventRouter(device_storage, time_service)
    bus.subscribe(router.handle)
    await bus.start()

    logger_ctrl = LoggerController()
    await logger_ctrl.start()
    logger_ctrl.create_session()
    logger = LoggerService(logger_ctrl)

    try:
        if frontend == "web":
            await run_web(logger, device_storage, connection_storage, bus)
        else:
            await run_cli(logger, device_storage, connection_storage, bus)
    finally:
        await bus.stop()
        await logger_ctrl.stop()