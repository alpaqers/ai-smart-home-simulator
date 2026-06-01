
from __future__ import annotations

import asyncio

from ..controllers.event_handler import EventHandler
from ..models.connection_storage import ConnectionStorage
from ..controllers.logger_service import LoggerService, _show_logs
from ..controllers.device_service import _show_devices, _change_device_state, _add_device
from ..models.device_storage import DeviceStorage

_MENU = """
┌──────────────────────────────┐
│     Smart Home Client        │
├──────────────────────────────┤
│  1) Show devices             │
│  2) Add device               │
│  3) Update device state      │
│  4) Show logs                │
│  5) Disconnect               │
└──────────────────────────────┘"""


async def run_cli(
        logger: LoggerService,
        device_storage: DeviceStorage,
        connection_storage: ConnectionStorage,
        bus: EventHandler
) -> None:
    while True:
        choice = await asyncio.to_thread(input, _MENU + "\n› ")

        if choice == "1":
            await asyncio.to_thread(_show_devices, device_storage)

        elif choice == "2":
            await _add_device(device_storage, connection_storage, logger, bus)

        elif choice == "3":
            pass
        #    await asyncio.to_thread(_change_device_state, storage, writer, logger)

        elif choice == "4":
            await asyncio.to_thread(_show_logs, logger)

        elif choice == "5":
            logger.info("Client disconnecting.")
            break

        else:
            print("  Invalid choice — try again.")