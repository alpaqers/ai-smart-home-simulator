from __future__ import annotations

import asyncio

from smart_home.client.controllers.connection_controller import add_connection
from smart_home.client.controllers.connection_handler import ConnectionHandler
from smart_home.client.controllers.device_registry import add_device_to_storage
from smart_home.client.controllers.event_handler import EventHandler
from smart_home.client.controllers.logger_service import LoggerService
from smart_home.client.controllers.message_coder import (
    decode_ai_tick_response,
    encode_ai_tick_request,
)
from smart_home.client.controllers.time_service import TimeService
from smart_home.client.controllers.time_sync import sync_server_time_if_simulated
from smart_home.client.models.connection_storage import ConnectionStorage
from smart_home.client.models.device import Device
from smart_home.client.models.device_storage import DeviceStorage
from smart_home.common.config_loader import SERVER_HOST, SERVER_PORT
from smart_home.demo.scenario import format_timestamp
from smart_home.demo.seed_client import print_seed_summary, seed_demo_scenario


def _client_device_type(server_type: str) -> str:
    if server_type.endswith("_lamp") or server_type == "bathroom_fan":
        return "lamp"
    if "sensor" in server_type or server_type == "garage_door":
        return "sensor"
    if server_type.endswith("_ac"):
        return "ac"
    if server_type == "thermostat":
        return "thermometer"
    return "lamp"


async def load_demo_data(
    device_storage: DeviceStorage,
    connection_storage: ConnectionStorage,
    bus: EventHandler,
    time_service: TimeService,
    logger: LoggerService,
) -> None:
    print("\n--------- Load demo data ---------")
    print("Registering devices and replaying history...")

    try:
        result = await seed_demo_scenario()
    except Exception as exc:
        print(f"ERROR: Failed to load demo data: {exc}")
        logger.error(f"Failed to load demo data: {exc}")
        return

    for device, handler in result.device_connections:
        client_device = Device(
            device_id=device.device_id,
            device_type=_client_device_type(device.device_type),
            capabilities=dict(device.capabilities),
            device_state=dict(device.device_state),
        )
        ok, msg = add_device_to_storage(device_storage, client_device)
        if not ok:
            print(f"WARN: {msg}")
        else:
            handler.event_callback = bus.put_event
            add_connection(connection_storage, device.device_id, handler)

    if result.device_connections:
        sync_handler = result.device_connections[0][1]
        try:
            ok, message = await sync_server_time_if_simulated(time_service, sync_handler)
            if ok and time_service.is_simulated():
                print(f"  {message}")
            elif not ok:
                print(f"  WARN: {message}")
                logger.warning(message)
        except Exception as exc:
            print(f"  WARN: Could not sync server time: {exc}")
            logger.warning(f"Could not sync server time: {exc}")

    print_seed_summary(result)
    logger.info(
        f"Demo data loaded: devices={len(result.devices)}, "
        f"history={result.history_records}"
    )


async def trigger_ai_tick(time_service: TimeService, logger: LoggerService) -> None:
    print("\n--------- Trigger AI analysis ---------")
    handler: ConnectionHandler | None = None

    try:
        reader, writer = await asyncio.open_connection(
            host=SERVER_HOST,
            port=SERVER_PORT,
        )
        handler = ConnectionHandler(reader, writer, "ai-trigger")
        await handler.start()

        ok, message = await sync_server_time_if_simulated(time_service, handler)
        if not ok:
            print(f"  {message}")
            logger.error(message)
            return
        if time_service.is_simulated():
            print(f"  {message}")

        response_b64 = await handler.send_and_wait(encode_ai_tick_request(), timeout=90.0)
        response = decode_ai_tick_response(response_b64)

        if response is None:
            print("  Invalid AI tick response from server.")
            logger.error("Invalid AI tick response from server.")
            return

        if not response.success:
            cause = response.cause if response.cause else "unknown error"
            print(f"  AI tick failed: {cause}")
            logger.error(f"AI tick failed: {cause}")
            return

        print(
            "  AI tick completed at "
            f"{format_timestamp(response.timestamp)}; "
            f"tasks_added={response.tasks_added}"
        )
        logger.info(f"AI tick completed; tasks_added={response.tasks_added}")
    except Exception as exc:
        print(f"  AI tick request failed: {exc}")
        logger.error(f"AI tick request failed: {exc}")
    finally:
        if handler is not None:
            await handler.stop()
