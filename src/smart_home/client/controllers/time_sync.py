from __future__ import annotations

from smart_home.client.controllers.connection_handler import ConnectionHandler
from smart_home.client.controllers.message_coder import (
    decode_time_shift_response,
    encode_time_shift_request,
)
from smart_home.client.controllers.time_service import TimeService
from smart_home.demo.scenario import format_timestamp


async def sync_server_time_if_simulated(
    time_service: TimeService,
    handler: ConnectionHandler,
    *,
    timeout: float = 10.0,
) -> tuple[bool, str]:
    """Align server simulated clock with the client when the client uses simulated time."""
    if not time_service.is_simulated():
        return True, "Client uses real time; server unchanged."

    payload_b64 = encode_time_shift_request(time_service.now())
    response_b64 = await handler.send_and_wait(payload_b64, timeout=timeout)
    response = decode_time_shift_response(response_b64)
    if response is None or not response.success:
        detail = response.cause if response is not None else "invalid response"
        return False, f"Time sync failed: {detail}"

    return True, f"Server time synced to {format_timestamp(response.timestamp)}"
