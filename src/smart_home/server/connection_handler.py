from asyncio import StreamReader, StreamWriter

from smart_home.common.config import config
from smart_home.server.message_handler import parse_envelope, handle_message


async def handle_client(reader: StreamReader, writer: StreamWriter) -> None:
    try:
        while True:
            data = await reader.read(config.buffer_size)

            if not data:
                break
            
            envelope = parse_envelope(data)
            handle_message(envelope)
    finally:
        writer.close()
        await writer.wait_closed()