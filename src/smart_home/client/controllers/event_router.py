from __future__ import annotations

from ..models.containers import DeviceStorage
from ..controllers.device_storage import update_device_state, add_device_to_storage
from . import message_coder


class ClientEventRouter:
    """Routes incoming client events to dedicated subhandlers."""

    def __init__(self, storage: DeviceStorage) -> None:
        self._storage = storage

    def handle(self, event_data: str) -> bool:
        """Handle one raw incoming event payload.

        Returns True when the event was recognized and handled.
        """
        return self._handle_state_update(event_data)

    def _handle_state_update(self, event_data: str) -> bool:
        state_update = message_coder.decode_state_update_message(event_data)
        if state_update is None:
            return False

        success, message = update_device_state(
            storage=self._storage,
            device_id=state_update.device_id,
            new_state=dict(state_update.parameters),
        )

        if not success:
            print(f"WARN: {message}")

        return success

    def _handle_device_registration(self, event_data: str) -> bool:
        """Decode and register a new device from the raw event payload.

        Returns True when the device was successfully decoded and added to storage.
        """
        new_device = message_coder.decode_device_registration(event_data)
        if new_device is None:
            return False

        success, message = add_device_to_storage(
            storage=self._storage,
            device=new_device
        )

        if not success:
            print(f"WARN: {message}")

        return success
