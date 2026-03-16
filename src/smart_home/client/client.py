import asyncio

from asyncio import StreamReader, StreamWriter

from smart_home.client.connection_handler import handle_connection
from smart_home.common.config_loader import SERVER_HOST, SERVER_PORT


async def start_client() -> None:
    reader: StreamReader
    writer: StreamWriter

    reader, writer = await asyncio.open_connection(
        SERVER_HOST,
        SERVER_PORT,
    )

    print(f"Connected to server: {SERVER_HOST}:{SERVER_PORT}")

    await handle_connection(reader, writer)