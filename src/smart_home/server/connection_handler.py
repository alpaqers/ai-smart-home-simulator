import base64
from asyncio import StreamReader, StreamWriter

from smart_home.server.message_handler import parse_envelope, msg_to_event
from smart_home.common.config import config
from smart_home.server.event_bus import EventBus
from smart_home.server.registry import DeviceRegistry


async def handle_client(reader: StreamReader, writer: StreamWriter, registry: DeviceRegistry, bus: EventBus) -> None:
    try:
        while True:
            data = await reader.read(config.buffer_size)

            if not data:
                break

            #request_id, payload_b64 = line.decode().strip().split("|", 1)
            #raw_bytes = base64.b64decode(payload_b64)

            envelope = parse_envelope(data)
            event = msg_to_event(envelope, writer)
            if event is None:
                print("[handle_client] Unsupported or unknown message type")
                continue

            await bus.publish(event)

    except Exception as e:
            print(f"[handle_client] Error: {e}")

    finally:
        await registry.unregister_by_writer(writer)
        writer.close()
        await writer.wait_closed()