from ..models.device import Device
from ..models.device_storage import DeviceStorage
from .device_controller import save_device


def add_device_to_storage(storage: DeviceStorage, device: Device) -> tuple[bool, str]:
    return save_device(storage, device)