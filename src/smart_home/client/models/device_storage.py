from dataclasses import dataclass, field
from typing import Dict

from ..controllers.connection_handler import ConnectionHandler
from .device import Device


@dataclass
class DeviceStorage:
    #id urządzenia -> konkretne urządzenie
    lamps: Dict[int, Device] = field(default_factory=dict)
    thermometers: Dict[int, Device] = field(default_factory=dict)
    sensors: Dict[int, Device] = field(default_factory=dict)
    ACs: Dict[int, Device] = field(default_factory=dict) #klima
    connections: Dict[int, ConnectionHandler] = field(default_factory=dict)
