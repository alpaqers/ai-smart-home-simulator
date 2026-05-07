from __future__ import annotations

import asyncio
import argparse
from asyncio import StreamReader, StreamWriter

from ..common.config import config
from ..client.controllers.connection_handler import ConnectionHandler
from ..client.controllers.message_sender import register_device
from ..client.controllers.event_handler import EventHandler
from ..client.controllers.event_router import ClientEventRouter
from ..client.controllers.logger_controller import LoggerController
from ..client.models.containers import DeviceStorage
from ..client.views.cli import run_cli
from ..client.controllers.logger_service import LoggerService


async def start_client(args: argparse.Namespace) -> None:
    host = args.ip or config.host
    port = args.port or config.port

    reader: StreamReader
    writer: StreamWriter
    reader, writer = await asyncio.open_connection(host, port)

    bus = EventHandler()
    storage = DeviceStorage()
    router = ClientEventRouter(storage)
    bus.subscribe(router.handle)
    await bus.start()

    connection_handler = ConnectionHandler(reader, writer, args.device_type)
    connection_handler.event_callback = bus.put_event
    await connection_handler.start()

    logger_ctrl = LoggerController()
    await logger_ctrl.start()
    logger_ctrl.create_session(device_type=args.device_type)
    logger = LoggerService(logger_ctrl)

    registered_device_id = await register_device(connection_handler, args.device_type)
    if registered_device_id is None:
        logger.error("Device registration did not complete.")
    else:
        logger.info(f"Connected to {host}:{port} as '{args.device_type}' (id={registered_device_id})")

    try:
        await run_cli(writer, logger, storage)
    finally:
        await connection_handler.stop()
        await bus.stop()
        await logger_ctrl.stop()