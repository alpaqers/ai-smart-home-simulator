import asyncio

from ..controllers.message_coder import encode_state_change
from ..controllers.device_controller import get_devices_by_type, get_all_devices
from ..controllers.device_registry import add_device_to_storage
from ..controllers.logger_service import LoggerService
from ..models.containers import DeviceStorage
from ..controllers.device_storage import update_device_state
from ..models.device import _STATE_SCHEMA, _CAPABILITIES_SCHEMA
from ..controllers.device_factory import create_lamp, create_thermometer, create_sensor, create_ac
from ..controllers.time_service import TimeService

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


def _add_device(storage: DeviceStorage, logger: LoggerService) -> None:
    _FACTORY_MAP = {
        "lamp": create_lamp,
        "thermometer": create_thermometer,
        "sensor": create_sensor,
        "ac": create_ac,
        "airconditioning": create_ac,
    }
    print("\n── Add Device ───────────────────────────────")

    raw_id  = input("Device ID (int): ").strip()
    device_type = input("Device type (lamp / thermometer / sensor / ac): ").strip().lower()

    try:
        device_id = int(raw_id)
    except ValueError:
        print("Device ID must be an integer.")
        return

    factory = _FACTORY_MAP.get(device_type)
    if factory is None:
        print(f"Unknown device type '{device_type}'.")
        return

    capabilities = _prompt_fields("  Capabilities", _CAPABILITIES_SCHEMA.get(device_type, []))
    device_state = _prompt_fields("  Initial state", _STATE_SCHEMA.get(device_type, []))

    device = factory(device_id, device_type, capabilities, device_state)
    ok, msg = add_device_to_storage(storage, device)

    print(f"\n{msg}")
    logger.info(msg) if ok else logger.error(msg)


def _change_device_state(
    storage: DeviceStorage,
    writer:  asyncio.StreamWriter,
    logger:  LoggerService,
    time_service: TimeService,
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

    payload = encode_state_change(device_id, new_state, device.device_type, time_service)
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