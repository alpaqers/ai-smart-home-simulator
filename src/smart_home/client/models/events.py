from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

@dataclass
class StorageEvent:
    event_type: str #registration, state change, time shift
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    device_id: Optional[int] = None
    device_data: Optional[dict[str, Any]] = None 
    new_simulated_time: Optional[str] = None
