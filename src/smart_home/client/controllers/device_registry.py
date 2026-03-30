from models.devices import Device
from models.containers import DeviceStorage


def add_device_to_storage(storage: DeviceStorage, device: Device) -> tuple[bool, str]:
    
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
        return False, f"Error: Container for type '{device.device_type}' does not exist."

    return True, f"Device with ID {device.device_id} successfully added to the {dtype} section."