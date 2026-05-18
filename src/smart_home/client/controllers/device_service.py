import asyncio

from ..models.connection_storage import ConnectionStorage
from .connection_controller import add_connection
from .connection_handler import ConnectionHandler
from .message_sender import register_device
from ..controllers.message_coder import encode_state_change
from ..controllers.device_controller import get_devices_by_type, get_all_devices
from ..controllers.device_registry import add_device_to_storage
from ..controllers.logger_service import LoggerService
from ..models.device_storage import DeviceStorage
from .device_controller import update_device_state
from ..models.device import _STATE_SCHEMA, _CAPABILITIES_SCHEMA
from ..controllers.device_factory import create_device
from ..controllers.event_handler import EventHandler
from ...common.config import config

def _show_devices(storage: DeviceStorage) -> None:
    filter_type = input("  Filter by type (leave blank for all): ").strip().lower()

    devices = (
        get_devices_by_type(storage, filter_type)
        if filter_type
        else get_all_devices(storage)
    )

    if not devices:
        print("  No devices found.")
        return

    print()
    for device in devices:
        print(f"  [{device.device_id}]  type={device.device_type}  state={device.device_state}")


async def _add_device(device_storage: DeviceStorage, connection_storage: ConnectionStorage, logger: LoggerService, bus: EventHandler) -> None:
    print("\n── Add Device ───────────────────────────────")

    device_type = (await asyncio.to_thread(input, "Device type: ")).strip().lower()
    if device_type not in _CAPABILITIES_SCHEMA:
        print(f"Unknown device type '{device_type}'.")
        return

    capabilities = await asyncio.to_thread(_prompt_fields, "  Capabilities", _CAPABILITIES_SCHEMA.get(device_type, []))
    device_state = await asyncio.to_thread(_prompt_fields, "  Initial state", _STATE_SCHEMA.get(device_type, []))

    device = create_device(device_type, capabilities, device_state)

    reader, writer = await asyncio.open_connection(port=config.port, host=config.host)
    handler = ConnectionHandler(reader, writer, device_type)
    handler.event_callback = bus.put_event
    await handler.start()

    registered_id = await register_device(handler, device_type, capabilities, device_state)
    if registered_id is None:
        print(f"Failed to register device with type '{device_type}'.")
        logger.error(f"Failed to register device with type '{device_type}'.")
        await handler.stop()
        return

    device.device_id = registered_id

    ok, msg = add_device_to_storage(device_storage, device)
    add_connection(connection_storage, registered_id, handler)

    print(f"\n{msg}")
    logger.info(msg) if ok else logger.error(msg)
    return


def _change_device_state(
    storage: DeviceStorage,
    writer:  asyncio.StreamWriter,
    logger:  LoggerService,
) -> None:
    print("\n── Change Device State ──────────────────────")

    raw_id = input("Device ID: ").strip()

    try:
        device_id = int(raw_id)
    except ValueError:
        print("Device ID must be an integer.")
        return

    all_devices = get_all_devices(storage)
    device = next((d for d in all_devices if d.device_id == device_id), None)
    if device is None:
        print(f"No device with ID {device_id}.")
        return

    print(f"Device type: {device.device_type}")
    print(f"Current state: {device.device_state}")

    new_state = _prompt_fields(
        "New state (leave blank to skip)",
        _STATE_SCHEMA.get(device.device_type.lower(), []),
        optional=True,
    )

    if not new_state:
        print("Nothing to update.")
        return

    success, message = update_device_state(
        storage=storage,
        device_id=device_id,
        new_state=new_state,
    )
    if not success:
        print(f"{message}")
        logger.error(message)
        return

    payload = encode_state_change(device_id, new_state, device.device_type)
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    writer.write(len(payload).to_bytes(4, "big") + payload)

    logger.info(f"State change sent: device={device_id} state={new_state}")
    print("State change sent.")


def _prompt_fields(label: str, fields: list[str], optional: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}

    if fields:
        print(f"{label}:")
        for key in fields:
            val = input(f"    {key}: ").strip()
            if val or not optional:
                result[key] = val
    else:
        print(f"{label} (key=value, blank line to finish):")
        while True:
            raw = input().strip()
            if not raw:
                break
            if "=" not in raw:
                print("Expected format: key=value")
                continue
            k, _, v = raw.partition("=")
            result[k.strip()] = v.strip()

    return result