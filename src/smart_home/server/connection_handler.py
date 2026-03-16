from asyncio import StreamReader, StreamWriter

from smart_home.common.config_loader import BUFFER_SIZE


async def handle_client(reader: StreamReader, writer: StreamWriter) -> None:
    try:
        while True:
            data = await reader.read(BUFFER_SIZE)

            if not data:
                break

            print(f"Server received: {data}")

            response = f"Server received: {data}"

            writer.write(response.encode("utf-8"))
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()