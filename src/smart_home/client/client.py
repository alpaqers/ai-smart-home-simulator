import asyncio

from asyncio import StreamReader, StreamWriter

from src.smart_home.common.config import config
from src.smart_home.client.connection_handler import handle_connection


async def start_client() -> None:
    reader: StreamReader
    writer: StreamWriter

    reader, writer = await asyncio.open_connection(
        config.host,
        config.port,
    )

    print(f"Connected to server {config.host}:{config.port}")

    await handle_connection(reader, writer)