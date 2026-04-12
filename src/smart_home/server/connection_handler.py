from asyncio import StreamReader, StreamWriter

from smart_home.server.message_handler import parse_envelope, msg_to_event, decode_wire_message
from smart_home.server.event_bus import EventBus
from smart_home.server.registry import DeviceRegistry


async def handle_client(reader: StreamReader, writer: StreamWriter, registry: DeviceRegistry, bus: EventBus) -> None:
    try:
        while True:
            data = await reader.readline()

            if not data:
                break

            request_id, proto_bytes = decode_wire_message(data)

            envelope = parse_envelope(proto_bytes)
            event = msg_to_event(envelope, writer, request_id)
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