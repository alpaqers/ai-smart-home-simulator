from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from ...common.config_loader import SERVER_HOST, SERVER_PORT
from .connection_handler import ConnectionHandler
from .logger_service import LoggerService
from .message_coder import decode_task_list_response, encode_task_list_request


async def show_scheduler_tasks(
    logger: LoggerService,
    *,
    include_dispatched: bool = True,
) -> None:
    handler: ConnectionHandler | None = None

    try:
        reader, writer = await asyncio.open_connection(
            host=SERVER_HOST,
            port=SERVER_PORT,
        )
        handler = ConnectionHandler(reader, writer, "task-viewer")
        await handler.start()

        payload = encode_task_list_request(include_dispatched=include_dispatched)
        response_b64 = await handler.send_and_wait(payload, timeout=10.0)
        response = decode_task_list_response(response_b64)

        if response is None:
            print("  Invalid task list response from server.")
            logger.error("Invalid task list response from server.")
            return

        if not response.success:
            cause = response.cause if response.cause else "unknown error"
            print(f"  Could not load scheduler tasks: {cause}")
            logger.error(f"Could not load scheduler tasks: {cause}")
            return

        _print_tasks(response.tasks)
        logger.info(f"Loaded {len(response.tasks)} scheduler task(s).")
    except Exception as exc:
        print(f"  Could not load scheduler tasks: {exc}")
        logger.error(f"Could not load scheduler tasks: {exc}")
    finally:
        if handler is not None:
            await handler.stop()


def _print_tasks(tasks) -> None:
    if not tasks:
        print("  No scheduler tasks.")
        return

    print("\nScheduler tasks:")
    for task in tasks:
        status = "dispatched" if task.dispatched else "pending"
        print(
            "  "
            f"#{task.task_id} "
            f"device={task.device_id} "
            f"time={_format_timestamp(task.time)} "
            f"status={status} "
            f"parameters={dict(task.parameters)}"
        )


def _format_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
