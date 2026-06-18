from __future__ import annotations

from models.events import StorageEvent
from .device_controller import save_device, update_device_state
from .persistence import save_event_to_file
from ..models.device_storage import DeviceStorage
from .time_service import TimeService
from . import message_coder


class ClientEventRouter:
    """Routes incoming client events to dedicated subhandlers."""

    def __init__(self, storage: DeviceStorage, time_service: TimeService) -> None:
        self._storage = storage
        self._time_service = time_service

    def handle(self, event_data: str) -> bool:
        """Handle one raw incoming event payload.

        Returns True when the event was recognized and handled.
        """
        if event_data.startswith("STATE_UPDATE:"):
            return self._handle_state_update(event_data)
        elif event_data.startswith("DEVICE_REGISTRATION:"):
            return self._handle_device_registration(event_data)
        elif self._handle_time_shift(event_data):
            return True
        else:
            print(f"WARN: Unknown event: {event_data}")
            return False

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

        success, message = save_device(
            storage=self._storage,
            device=new_device
        )

        if not success:
            print(f"WARN: {message}")

        return success

    def _handle_time_shift(self, event_data: str) -> bool:
        """Decode time shift from network payload, update local time service, and persist the event."""
        decode_func = getattr(message_coder, "decode_time_shift_message", None)
        if decode_func is None:
            return False

        time_shift_data = decode_func(event_data)
        if time_shift_data is None:
            return False

        duration = getattr(time_shift_data, "duration", None)
        if duration is not None:
            current_timestamp = self._time_service.now()
            new_simulated_timestamp = current_timestamp + duration
            self._time_service.use_simulated_time(new_simulated_timestamp)
            print(f"[NETWORK] Time shifted by {duration} seconds. New local timestamp: {new_simulated_timestamp}")

            event = StorageEvent(
                event_type="time_shift",
                duration=duration
            )
            save_event_to_file(event)
            return True

        return False
