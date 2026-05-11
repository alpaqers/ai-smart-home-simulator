from .containers import DeviceStorage
from .device import Device


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

    return True, f"Device {device.device_id} saved to {dtype} storage."


def update_device_state(storage: DeviceStorage, device_id: int, new_state: dict[str, str]) -> tuple[bool, str]:
    for container in [storage.lamps, storage.thermometers, storage.sensors, storage.ACs]:
        if device_id in container:
            container[device_id].device_state.update(new_state)
            return True, f"Device {device_id} state updated."

    return False, f"Device {device_id} not found in storage."