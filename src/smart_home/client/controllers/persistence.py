import json
import os
from dataclasses import asdict
from models.containers import DeviceStorage
from models.device import Device

STORAGE_FILE = "device_storage.json"

def save_to_file(storage: DeviceStorage):
    """Converts DeviceStorage to JSON and saves it to the disk."""
    data = asdict(storage)
    with open(STORAGE_FILE, "in", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_from_file() -> DeviceStorage:
    """Loads JSON and rebuilds Device class objects."""
    if not os.path.exists(STORAGE_FILE):
        return DeviceStorage()

    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        storage = DeviceStorage()
        # Manually fix keys (str -> int) and instantiate Device objects
        # JSON keys are always strings, but DeviceStorage expects ints 
        for attribute_name in ["lamps", "thermometers", "sensors", "ACs"]:
            if attribute_name in data:
                raw_devices = data[attribute_name]
                rebuilt = {int(k): Device(**v) for k, v in raw_devices.items()}
                setattr(storage, attribute_name, rebuilt)
        return storage
    except Exception as e:
        print(f"Fail to load file: {e}")
        return DeviceStorage()