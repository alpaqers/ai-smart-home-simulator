from __future__ import annotations

import asyncio
from datetime import datetime

from ..controllers.event_handler import EventHandler
from ..models.connection_storage import ConnectionStorage
from ..controllers.logger_service import LoggerService, _show_logs
from ..controllers.device_service import _show_devices, _change_device_state, _add_device
from ..controllers.time_service import TimeService
from ..controllers.TimeShiftSubhandler import handle_time_shift
from ..controllers.connection_controller import all_connections
from ..models.device_storage import DeviceStorage

_MENU = """
┌──────────────────────────────┐
│     Smart Home Client        │
├──────────────────────────────┤
│  1) Show devices             │
│  2) Add device               │
│  3) Update device state      │
│  4) Show logs                │
│  5) Time shift               │
│  6) Disconnect               │
└──────────────────────────────┘"""


async def _setup_time(time_service: TimeService) -> None:
    """Ask user whether to use real or simulated time."""
    choice = await asyncio.to_thread(input, "Use simulated time? (y/n): ")
    if choice.strip().lower() == "y":
        raw = await asyncio.to_thread(input, "Enter simulated time (unix timestamp): ")
        try:
            time_service.use_simulated_time(datetime.fromtimestamp(int(raw.strip())))
            print("Using simulated time.")
        except ValueError:
            print("Invalid timestamp, using real time.")
            time_service.use_real_time()
    else:
        time_service.use_real_time()
        print("Using real time.")


async def run_cli(
        logger: LoggerService,
        device_storage: DeviceStorage,
        connection_storage: ConnectionStorage,
        bus: EventHandler,
        time_service: TimeService,
) -> None:
    await _setup_time(time_service)

    while True:
        choice = await asyncio.to_thread(input, _MENU + "\n› ")

        if choice == "1":
            await asyncio.to_thread(_show_devices, device_storage)

        elif choice == "2":
            await _add_device(device_storage, connection_storage, logger, bus, time_service)

        elif choice == "3":
            await _change_device_state(device_storage, connection_storage, logger, time_service)

        elif choice == "4":
            await asyncio.to_thread(_show_logs, logger)

        elif choice == "5":
            connections = all_connections(connection_storage)
            if not connections:
                print("  No active device connections — add a device first.")
            else:
                await handle_time_shift(time_service, connections[0])

        elif choice == "6":
            logger.info("Client disconnecting.")
            break

        else:
            print("  Invalid choice — try again.")
