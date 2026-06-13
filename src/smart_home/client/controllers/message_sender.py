from __future__ import annotations

from .connection_handler import ConnectionHandler
from .device_id_allocator import next_device_id
from .message_coder import decode_register_response, encode_register_request, encode_state_change


async def register_device(
    handler:      ConnectionHandler,
    device_type:  str,
    capabilities: dict[str, str],
    device_state: dict[str, str],
) -> int | None:
    try:
        device_id = next_device_id()
        payload_b64, req = encode_register_request(device_type, capabilities, device_state, device_id)
        print(f"Register request sent (Type: {device_type}")

        response_b64 = await handler.send_and_wait(payload_b64)
        resp = decode_register_response(response_b64)

        if resp.success:
            print(f"Device registered successfully (ID: {resp.device_id} At {resp.timestamp})")
            return resp.device_id
        else:
            print(f"Registration failed: {resp.cause}")
            return None

    except TimeoutError:
        print("Server failed to respond")
        return None
    except Exception as e:
        print(f"Critical connection error: {e}")
        return None