from ..models.device import Device

def create_device(device_type: str, capabilities: dict, device_state: dict) -> Device:
    return Device(
        device_id=None,
        device_type=device_type,
        capabilities=capabilities,
        device_state=device_state,
    )