import asyncio

from smart_home.server.connection_handler import handle_client
from smart_home.common.config_loader import HOST, PORT


async def start_server() -> None:
    #tutaj otwiera sie socket
    server = await asyncio.start_server(
        handle_client,
        HOST,
        PORT,
    )

    print(f"Server started on: {HOST}:{PORT}")

    async with server:
        await server.serve_forever()