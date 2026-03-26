import base64
from asyncio import StreamReader, StreamWriter

from smart_home.server.message_handler import parse_envelope, msg_to_event


async def handle_client(reader: StreamReader, writer: StreamWriter) -> None:
    try:
        while True:
            line = await reader.readline()

            if not line:
                break

            request_id, payload_b64 = line.decode().strip().split("|", 1)
            raw_bytes = base64.b64decode(payload_b64)

            envelope = parse_envelope(raw_bytes)
            event = msg_to_event(envelope, writer)
    finally:
        writer.close()
        await writer.wait_closed()