"""
TBD:
handlers = {
        "1": lambda: show_devices(store),
        "2": lambda: add_device(store, logger, device_type),
        "3": lambda: change_device_state(store, logger, writer),
        "4": lambda: show_logs(logger),
    }
"""

from __future__ import annotations

import asyncio
from asyncio import StreamWriter

from ..controllers.logger_service import LoggerService, _show_logs
from ..controllers.device_service import _show_devices, _change_device_state, _add_device
from ..models.containers import DeviceStorage

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
        writer: StreamWriter,
        logger: LoggerService,
        storage: DeviceStorage,
) -> None:
    while True:
        choice = await asyncio.to_thread(input, _MENU + "\n› ")

        if choice == "1":
            await asyncio.to_thread(_show_devices, storage)

        elif choice == "2":
            await asyncio.to_thread(_add_device, storage, logger)

        elif choice == "3":
            await asyncio.to_thread(_change_device_state, storage, writer, logger)

        elif choice == "4":
            await asyncio.to_thread(_show_logs, logger)

        elif choice == "5":
            logger.info("Client disconnecting.")
            break

        else:
            print("  Invalid choice — try again.")