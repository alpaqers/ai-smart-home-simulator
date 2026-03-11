from asyncio import StreamReader, StreamWriter

from app.common.config import config


async def handle_client(reader: StreamReader, writer: StreamWriter) -> None:
    try:
        while True:
            data = await reader.read(config.buffer_size)

            if not data:
                break

            response = f"Server received: {data}\n\r"

            writer.write(response.encode("utf-8"))
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()