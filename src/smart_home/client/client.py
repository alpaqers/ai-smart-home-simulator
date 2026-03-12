import asyncio

from asyncio import StreamReader, StreamWriter

from smart_home.client.connection_handler import handle_connection
from smart_home.common.config import config


async def start_client() -> None:
    reader: StreamReader
    writer: StreamWriter

    reader, writer = await asyncio.open_connection(
        config.host,
        config.port,
    )

    print(f"Connected to server {config.host}:{config.port}")

    await handle_connection(reader, writer)