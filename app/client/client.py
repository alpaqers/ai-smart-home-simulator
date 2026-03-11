import asyncio

from asyncio import StreamReader, StreamWriter

from app.common.config import config
from app.client.connection_handler import handle_connection


async def start_client() -> None:
    reader: StreamReader
    writer: StreamWriter

    reader, writer = await asyncio.open_connection(
        config.host,
        config.port,
    )

    print(f"Connected to server {config.host}:{config.port}")

    await handle_connection(reader, writer)