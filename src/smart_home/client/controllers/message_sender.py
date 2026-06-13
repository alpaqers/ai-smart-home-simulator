from __future__ import annotations

from .connection_handler import ConnectionHandler
from .device_id_allocator import next_device_id
from ..models.device import Device
from .message_coder import decode_register_response, encode_register_request
from .time_service import TimeService


async def register_device(
    handler: ConnectionHandler,
    device_type: str,
    capabilities: dict[str, str],
    device_state: dict[str, str],
    time_service: TimeService | None = None,
) -> int | None:
    try:
        device_id = next_device_id()
        payload_b64, req = encode_register_request(
            device_type, capabilities, device_state, device_id, time_service
        )
        print(f"Register request sent (Type: {device_type}, ID: {req.device_id})...")

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

async def reregister_device(
    handler: ConnectionHandler,
    device: Device,
) -> int | None:

    if device.device_id is None:
        return None

    try:
        payload_b64, _ = encode_register_request(
            device.device_type,
            device.capabilities,
            device.device_state,
            device.device_id,
        )
        print(f"Re-register request sent (ID: {device.device_id}, Type: {device.device_type})")

        response_b64 = await handler.send_and_wait(payload_b64)
        resp = decode_register_response(response_b64)

        if resp.success:
            print(f"Device re-registered successfully (ID: {resp.device_id} At {resp.timestamp})")
            return resp.device_id

        print(f"Re-registration failed: {resp.cause}")
        return None

    except TimeoutError:
        print("Server failed to respond during re-registration")
        return None
    except Exception as e:
        print(f"Critical connection error during re-registration: {e}")
        return None