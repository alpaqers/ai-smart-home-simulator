import asyncio

from app.config import config
from app.connection_handler import handle_client


async def start_server() -> None:
    #tutaj otwiera sie socket
    server = await asyncio.start_server(
        handle_client,
        config.host,
        config.port,
    )

    async with server:
        await server.serve_forever()