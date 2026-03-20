import time
import json
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DeviceRegisterReq:
    device_id: int
    device_type: str
    capabilities: Dict[str, str] = field(default_factory=dict)
    device_state: Dict[str, str] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time()))

    def to_json(self) -> str:
        return json.dumps({
            "type": "device_register_req",
            "device_id": self.device_id,
            "device_type": self.device_type,
            "capabilities": self.capabilities,
            "device_state": self.device_state,
            "timestamp": self.timestamp,
        })


@dataclass
class DeviceRegisterResp:
    device_id: int
    success: bool
    timestamp: int
    cause: Optional[str] = None

    @staticmethod
    def from_json(data: str) -> "DeviceRegisterResp":
        d = json.loads(data)
        return DeviceRegisterResp(
            device_id=d["device_id"],
            success=d["success"],
            timestamp=d["timestamp"],
            cause=d.get("cause"),
        )