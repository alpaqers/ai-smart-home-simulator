"""Client-side unique device id allocation.

The server trusts the ``device_id`` supplied in a ``DeviceRegisterReq`` and
echoes it back (see ``server/processors/register.py``). Without an explicit id
the proto3 field defaults to ``0`` for every device, so the second registration
collides in the server registry and fails. The client is therefore responsible
for handing out a fresh id per device.

Allocation happens on the client's single asyncio loop, so a plain counter is
sufficient; the first device gets id ``0``, the next ``1``, and so on.
"""

from __future__ import annotations

from itertools import count

_counter = count(0)

def seed_device_id_allocator(start: int) -> None:
    global _counter
    _counter = count(start)

def next_device_id() -> int:
    return next(_counter)
