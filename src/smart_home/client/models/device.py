from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Device:
    device_id: int
    device_type: str
    capabilities: Dict[str, str] = field(default_factory=dict)
    device_state: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)


_CAPABILITIES_SCHEMA: dict[str, list[str]] = {
    "lamp": ["brightness", "color"],
    "thermometer": ["min_temp", "max_temp"],
    "sensor": ["sensitivity", "unit"],
    "ac": ["min_temp", "max_temp", "modes"],
    "airconditioning": ["min_temp", "max_temp", "modes"],
}

_STATE_SCHEMA: dict[str, list[str]] = {
    "lamp": ["is_on", "brightness", "color"],
    "thermometer": ["temperature"],
    "sensor": ["value"],
    "ac": ["is_on", "temperature", "mode"],
    "airconditioning": ["is_on", "temperature", "mode"],
}