from __future__ import annotations

import asyncio
from asyncio import StreamWriter

from ..controllers.logger_service import LoggerService, _show_logs
from ..controllers.device_service import _show_devices, _change_device_state, _add_device
from ..controllers.time_service import TimeService
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


async def _setup_time(time_service: TimeService) -> None:
    """Ask user whether to use real or simulated time."""
    choice = await asyncio.to_thread(input, "Use simulated time? (y/n): ")
    if choice.strip().lower() == "y":
        raw = await asyncio.to_thread(input, "Enter simulated time (unix timestamp): ")
        try:
            time_service.use_simulated_time(int(raw.strip()))
            print("Using simulated time.")
        except ValueError:
            print("Invalid timestamp, using real time.")
            time_service.use_real_time()
    else:
        time_service.use_real_time()
        print("Using real time.")


async def run_cli(
        writer: StreamWriter,
        logger: LoggerService,
        storage: DeviceStorage,
        time_service: TimeService,
) -> None:
    await _setup_time(time_service)

    while True:
        choice = await asyncio.to_thread(input, _MENU + "\n› ")

        if choice == "1":
            await asyncio.to_thread(_show_devices, storage)

        elif choice == "2":
            await asyncio.to_thread(_add_device, storage, logger)

        elif choice == "3":
            await asyncio.to_thread(_change_device_state, storage, writer, logger, time_service)

        elif choice == "4":
            await asyncio.to_thread(_show_logs, logger)

        elif choice == "5":
            logger.info("Client disconnecting.")
            break

        else:
            print("  Invalid choice — try again.")