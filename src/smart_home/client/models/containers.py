from dataclasses import dataclass, field
from typing import Dict
from .device import Device

@dataclass
class DeviceStorage:
    #id urządzenia -> konkretne urządzenie
    lamps: Dict[int, Device] = field(default_factory=dict)
    thermometers: Dict[int, Device] = field(default_factory=dict)
    sensors: Dict[int, Device] = field(default_factory=dict)
    ACs: Dict[int, Device] = field(default_factory=dict) #klima