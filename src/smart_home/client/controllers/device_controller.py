from models.events import StorageEvent
from .persistence import save_event_to_file
from ..models.device_storage import DeviceStorage
from ..models.device import Device

def get_all_devices(storage: DeviceStorage) -> list[Device]:
    return [
        *storage.lamps.values(),
        *storage.thermometers.values(),
        *storage.sensors.values(),
        *storage.ACs.values(),
    ]


def get_devices_by_type(storage: DeviceStorage, device_type: str) -> list[Device]:
    dtype = device_type.lower().strip().replace(" ", "")

    containers = {
        "lamp": storage.lamps,
        "thermometer": storage.thermometers,
        "sensor": storage.sensors,
        "ac": storage.ACs,
        "airconditioning": storage.ACs,
    }

    container = containers.get(dtype)
    if container is None:
        return []

    return list(container.values())


def save_device(storage: DeviceStorage, device: Device) -> tuple[bool, str]:
    dtype = device.device_type.lower().strip().replace(" ", "")

    if dtype == "lamp":
        storage.lamps[device.device_id] = device
    elif dtype == "thermometer":
        storage.thermometers[device.device_id] = device
    elif dtype == "sensor":
        storage.sensors[device.device_id] = device
    elif dtype in ["ac", "airconditioning"]:
        storage.ACs[device.device_id] = device
    else:
        return False, f"Unknown device type: {device.device_type}"

    from dataclasses import asdict
    event = StorageEvent(
        event_type="device_registration",
        device_id=device.device_id,
        device_data=asdict(device)
    )
    save_event_to_file(event)

    return True, f"Device {device.device_id} saved to {dtype} storage."


def update_device_state(storage: DeviceStorage, device_id: int, new_state: dict[str, str]) -> tuple[bool, str]:
    for container in [storage.lamps, storage.thermometers, storage.sensors, storage.ACs]:
        if device_id in container:
            container[device_id].device_state.update(new_state)

            from dataclasses import asdict
            event = StorageEvent(
                event_type="state_update",
                device_id=device_id,
                device_data=asdict(container[device_id])
            )
            save_event_to_file(event)

            return True, f"Device {device_id} state updated."

    return False, f"Device {device_id} not found in storage."
