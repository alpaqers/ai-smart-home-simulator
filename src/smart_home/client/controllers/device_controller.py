from ..models.containers import DeviceStorage
from ..controllers.device_registry import add_device_to_storage
from ..controllers.device_factory import create_lamp, create_thermometer, create_sensor, create_ac
from ..models.device import Device

def device_registry(device_id: int, device_type: str, capabilities: dict, device_state: dict, storage: DeviceStorage) -> tuple[bool, str]:
    dtype = device_type.lower().strip().replace(" ", "")

    if dtype == "lamp":
        device = create_lamp(device_id, device_type, capabilities, device_state)
    elif dtype == "thermometer":
        device = create_thermometer(device_id, device_type, capabilities, device_state)
    elif dtype == "sensor":
        device = create_sensor(device_id, device_type, capabilities, device_state)
    elif dtype in ["ac", "airconditioning"]:
        device = create_ac(device_id, device_type, capabilities, device_state)
    else:
        return False, f"Nieznany typ urządzenia: {device_type}"

    return add_device_to_storage(storage, device)


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