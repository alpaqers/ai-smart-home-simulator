from __future__ import annotations
from datetime import timedelta
from .time_service import TimeService
from .message_coder import encode_time_shift_request
from .connection_handler import ConnectionHandler


async def handle_time_shift(time_service: TimeService, handler: ConnectionHandler) -> None:
    """Asks user for time shift delta, updates TimeService and sends request to server."""
    
    print("\n--------- Time Shift ---------")
    
    try:
        hours = int(input("Hours to shift (can be negative): ").strip())
        minutes = int(input("Minutes to shift (can be negative): ").strip())
    except ValueError:
        print("Invalid input — must be integers.")
        return

    # Apply shift to local TimeService
    delta = timedelta(hours=hours, minutes=minutes)
    time_service.make_time_shift(delta)

    # Send new time to server
    new_time = time_service.now()
    payload_b64 = encode_time_shift_request(new_time)

    try:
        await handler.send_and_wait(payload_b64)
        print(f"Time shifted to: {new_time}")
    except Exception as e:
        print(f"ERROR: Failed to send time shift: {e}")
