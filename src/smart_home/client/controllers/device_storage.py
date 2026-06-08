from ..models.containers import DeviceStorage
from ..models.device import Device
from ..models.events import StorageEvent
from .persistence import save_event_to_file


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
        return False, f"Unknown device type: {device.device_type}"

    # success: new evice added, now save the whole storage to disk
    from dataclasses import asdict
    event = StorageEvent(
        event_type="device_registration",
        device_id=device.device_id,
        device_data=asdict(device)
    )
    save_event_to_file(event)
    
    return True, f"Device {device.device_id} registered and saved to event storage."


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
            
            return True, f"Device {device_id} state updated and appended to event storage."

    return False, f"Device {device_id} not found in storage."
