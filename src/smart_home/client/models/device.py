from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Device:
    device_id: int
    device_type: str
    capabilities: Dict[str, str] = field(default_factory=dict)
    device_state: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
