from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class StorageEvent:
    event_type: str         # "device_registration", "state_update", "time_shift"
    device_id: Optional[int] = None
    device_data: Optional[dict[str, Any]] = None  
    duration: Optional[int] = None
