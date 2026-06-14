#!/usr/bin/env python3
"""Load demo devices and history onto a running server."""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smart_home.demo.seed_client import print_seed_summary, seed_demo_scenario


async def main() -> None:
    stop = asyncio.Event()

    def _request_stop(*_args: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _request_stop)

    print("Seeding demo data on the running server...")
    result = await seed_demo_scenario()
    print_seed_summary(result)
    print()
    print("Device connections are active. Press Ctrl+C to disconnect.")

    await stop.wait()

    for _device, handler in result.device_connections:
        await handler.stop()


if __name__ == "__main__":
    asyncio.run(main())
