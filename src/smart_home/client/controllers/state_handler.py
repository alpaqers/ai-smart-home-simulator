from __future__ import annotations
from typing import TYPE_CHECKING

from . import message_coder

if TYPE_CHECKING:
    from ..models.device import Device
    from .connection_handler import ConnectionHandler

async def notify_state_change(
    device: Device, 
    new_params: dict[str, str], 
    handler: ConnectionHandler
) -> None:
    """
    Neutral handler for device state changes.
    Uses device.device_type (str) to keep the controller independent 
    of hardcoded ID mappings.
    """
    device.device_state.update(new_params)

    payload_b64 = message_coder.encode_state_change(
        device_id=device.device_id,
        parameters=new_params,
        device_type=device.device_type
    )
    
    try:
        print(f"DEBUG: Sending state change for device {device.device_id}...")

        await handler.send_and_wait(payload_b64)
        
    except Exception as e:
        print(f"ERROR: Failed to transmit state change: {e}")
