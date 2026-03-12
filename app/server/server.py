import asyncio

from app.common.config import config
from app.server.connection_handler import handle_client


async def start_server() -> None:
    #tutaj otwiera sie socket
    server = await asyncio.start_server(
        handle_client,
        config.host,
        config.port,
    )

    print(f"Server started on {config.host}:{config.port}")

    async with server:
        await server.serve_forever()