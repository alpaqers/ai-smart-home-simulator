import asyncio
import argparse
from asyncio import StreamReader, StreamWriter
from ..common.config import config
from ..client.controllers.connection_handler import ConnectionHandler
from ..client.controllers.connection_handler import handle_connection

async def start_client(args: argparse.Namespace) -> None:
    reader: StreamReader
    writer: StreamWriter

    host = args.ip or config.host
    port = args.port or config.port

    reader, writer = await asyncio.open_connection(host, port)
    print(f"Connected to server {host}:{port} as '{args.device_type}'")

    handler = ConnectionHandler(reader, writer, args.device_type)
    await handle_connection(reader, writer, args.device_type)

    try:
        while True:
            message = await asyncio.to_thread(input, "Client > ")
            if message.lower() in {"exit", "quit"}:
                break

            response = await handler.send_and_wait(message)
            print(f"Server > {response}")
    finally:
        await handler.stop()