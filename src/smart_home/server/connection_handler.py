from asyncio import StreamReader, StreamWriter

from ..common.config import config


async def handle_client(reader: StreamReader, writer: StreamWriter) -> None:
    try:
        while True:
            data = await reader.read(config.buffer_size)

            if not data:
                break

            print(f"Server recieved: {data}")

            response = f"Server received: {data}"

            writer.write(response.encode("utf-8"))
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()