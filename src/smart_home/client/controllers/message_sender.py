from __future__ import annotations

from asyncio import StreamReader, StreamWriter

from .connection_handler import ConnectionHandler
from .message_coder import decode_register_response, encode_register_request


async def register_device(reader: StreamReader, writer: StreamWriter, device_type: str) -> None:
    handler = ConnectionHandler(reader, writer, device_type)
    await handler.start()

    try:
        payload_b64, req = encode_register_request(device_type)
        print(f"Register request sent (Type: {device_type}, ID: {req.device_id})...")

        response_b64 = await handler.send_and_wait(payload_b64)
        resp = decode_register_response(response_b64)

        if resp.success:
            print(f"Device registered successfully (At {resp.timestamp})")
        else:
            print(f"Registration failed: {resp.cause}")

    except TimeoutError:
        print("Server failed to respond")
    except Exception as e:
        print(f"Critical connection error: {e}")
    finally:
        await handler.stop()
        print("Client stopped")