import asyncio

from asyncio import StreamReader, StreamWriter

from smart_home.common.config_loader import BUFFER_SIZE


async def handle_connection(reader: StreamReader, writer: StreamWriter) -> None:
    try:
        while True:
            message = input("Client > ")

            writer.write(message.encode("utf-8"))
            await writer.drain()

            data = await reader.read(BUFFER_SIZE)

            if not data:
                print("Server closed connection")
                break

            print(f"Server > {data.decode('utf-8')}")

    finally:
        writer.close()
        await writer.wait_closed()
