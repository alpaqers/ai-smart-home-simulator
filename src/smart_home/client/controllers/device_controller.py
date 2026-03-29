from ..models.containers import DeviceStorage
from ..models.device_registry import add_device_to_storage
from ..controllers.device_factory import create_lamp, create_thermometer, create_sensor, create_ac


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