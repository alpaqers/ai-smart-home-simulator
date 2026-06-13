"""Bridge between the Django web frontend and the client's asyncio runtime.

The smart-home client lives entirely inside a single asyncio event loop (the
event bus, the per-device ``ConnectionHandler`` read loops and the logger
consumer all run there). Django, on the other hand, serves requests from a
synchronous, threaded dev server.

``run_web`` keeps the asyncio loop as the owner of the process: it captures the
running loop, publishes the shared collaborators through :data:`context`, then
starts Django's dev server in a daemon thread. Django views can hop back onto
the loop with :func:`call_async`.
"""

from __future__ import annotations

import asyncio
import os
import threading
from dataclasses import dataclass
from typing import Awaitable, Optional, TypeVar

from ...controllers.event_handler import EventHandler
from ...controllers.logger_service import LoggerService
from ...models.connection_storage import ConnectionStorage
from ...models.device_storage import DeviceStorage

T = TypeVar("T")


@dataclass
class AppContext:
    """Shared state handed from the asyncio runtime to the Django views."""

    loop: asyncio.AbstractEventLoop
    logger: LoggerService
    device_storage: DeviceStorage
    connection_storage: ConnectionStorage
    bus: EventHandler


# Module-level singleton populated by ``run_web`` and consumed by the Django
# views. It is ``None`` until the web frontend is started.
context: Optional[AppContext] = None


def get_context() -> AppContext:
    if context is None:
        raise RuntimeError("Web runtime is not initialised yet.")
    return context


def call_async(coro: Awaitable[T], timeout: float = 30.0) -> T:
    """Run an awaitable on the client's asyncio loop from a Django thread.

    Django views are synchronous and execute in the dev-server thread, so any
    coroutine that touches the asyncio runtime (opening connections, sending
    messages) must be scheduled back onto the loop owned by ``run_web``.
    """

    ctx = get_context()
    future = asyncio.run_coroutine_threadsafe(coro, ctx.loop)
    return future.result(timeout=timeout)


async def run_web(
    logger: LoggerService,
    device_storage: DeviceStorage,
    connection_storage: ConnectionStorage,
    bus: EventHandler,
) -> None:
    """Web counterpart of ``run_cli``: serve the Django frontend.

    Mirrors the signature of ``run_cli`` so the only change to existing code is
    selecting which view to launch.
    """

    global context

    loop = asyncio.get_running_loop()
    context = AppContext(
        loop=loop,
        logger=logger,
        device_storage=device_storage,
        connection_storage=connection_storage,
        bus=bus,
    )

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "smart_home.client.views.web.settings",
    )

    import django
    from django.core.management import call_command

    django.setup()

    host = os.getenv("WEB_HOST", "127.0.0.1")
    port = os.getenv("WEB_PORT", "8000")
    addr = f"{host}:{port}"

    shutdown = asyncio.Event()

    def _serve() -> None:
        try:
            call_command("runserver", addr, use_reloader=False, skip_checks=True)
        except Exception as exc:  # pragma: no cover - surfaced to the user
            logger.error(f"Web server stopped: {exc}")
        finally:
            loop.call_soon_threadsafe(shutdown.set)

    server_thread = threading.Thread(target=_serve, name="django-runserver", daemon=True)
    server_thread.start()

    logger.info(f"Web frontend available at http://{addr}")
    print(f"\nWeb frontend available at http://{addr}  (Ctrl+C to stop)\n")

    try:
        await shutdown.wait()
    except asyncio.CancelledError:
        raise
