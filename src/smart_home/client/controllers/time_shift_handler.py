from __future__ import annotations

from datetime import timedelta

from .connection_handler import ConnectionHandler
from .message_coder import decode_time_shift_response, encode_time_shift_request
from .time_service import TimeService


async def handle_time_shift(time_service: TimeService, handler: ConnectionHandler) -> None:
    """Asks user for time shift delta, updates TimeService and sends request to server."""

    print("\n--------- Time Shift ---------")

    try:
        hours = int(input("Hours to shift (can be negative): ").strip())
        minutes = int(input("Minutes to shift (can be negative): ").strip())
    except ValueError:
        print("Invalid input — must be integers.")
        return

    delta = timedelta(hours=hours, minutes=minutes)
    time_service.make_time_shift(delta)

    new_time = time_service.now()
    payload_b64 = encode_time_shift_request(new_time)

    try:
        response_b64 = await handler.send_and_wait(payload_b64)
        resp = decode_time_shift_response(response_b64)
        if resp is None or not resp.success:
            detail = resp.cause if resp is not None else "invalid response"
            print(f"ERROR: Time shift failed: {detail}")
            return
        print(f"Time shifted to: {new_time}")
    except Exception as e:
        print(f"ERROR: Failed to send time shift: {e}")
