from __future__ import annotations

import asyncio

from ..models.connection_storage import ConnectionStorage
from ..models.device import Device
from ..models.device_storage import DeviceStorage
from .connection_controller import add_connection, get_connection
from .connection_handler import ConnectionHandler
from .device_controller import get_all_devices
from .event_handler import EventHandler
from .logger_service import LoggerService
from .message_sender import reregister_device
from ...common.config_loader import SERVER_HOST, SERVER_PORT


async def reconnect_device(device: Device, bus: EventHandler) -> tuple[ConnectionHandler | None, str]:

    if device.device_id is None:
        return None, "Cannot reconnect device without an id."

    reader, writer = await asyncio.open_connection(host=SERVER_HOST, port=SERVER_PORT)
    handler = ConnectionHandler(reader, writer, device.device_type)
    handler.event_callback = bus.put_event
    await handler.start()

    registered_id = await reregister_device(handler, device)
    if registered_id is None:
        await handler.stop()
        return None, f"Failed to re-register device {device.device_id}."

    if registered_id != device.device_id:
        await handler.stop()
        return None, (
            f"Server returned id {registered_id}, expected {device.device_id}."
        )

    return handler, f"Reconnected device {device.device_id} ({device.device_type})."


async def restore_connections(
    device_storage: DeviceStorage,
    connection_storage: ConnectionStorage,
    bus: EventHandler,
    logger: LoggerService,
) -> None:

    devices = get_all_devices(device_storage)
    if not devices:
        return

    logger.info(f"Restoring connections for {len(devices)} device(s)...")

    for device in devices:
        if device.device_id is None:
            logger.error(f"Skipping device with missing id (type={device.device_type}).")
            continue

        if get_connection(connection_storage, device.device_id) is not None:
            continue

        try:
            handler, msg = await reconnect_device(device, bus)
            if handler is None:
                logger.error(msg)
                continue

            add_connection(connection_storage, device.device_id, handler)
            logger.info(msg)

        except Exception as exc:
            logger.error(f"Failed to reconnect device {device.device_id}: {exc}")