from __future__ import annotations

from .connection_handler import ConnectionHandler
from .message_coder import decode_register_response, encode_register_request


async def register_device(handler: ConnectionHandler, device_type: str) -> int | None:
    try:
        payload_b64, req = encode_register_request(device_type)
        print(f"Register request sent (Type: {device_type}, ID: {req.device_id})...")

        response_b64 = await handler.send_and_wait(payload_b64)
        resp = decode_register_response(response_b64)

        if resp.success:
            print(f"Device registered successfully (At {resp.timestamp})")
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