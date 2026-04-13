import asyncio
import argparse
from asyncio import StreamReader, StreamWriter
from ..common.config import config
from ..client.controllers.connection_handler import ConnectionHandler
from ..client.controllers.message_sender import register_device
from ..client.controllers.event_handler import EventHandler

async def start_client(args: argparse.Namespace) -> None:
    reader: StreamReader
    writer: StreamWriter

    host = args.ip or config.host
    port = args.port or config.port

    reader, writer = await asyncio.open_connection(host, port)
    print(f"Connected to server {host}:{port} as '{args.device_type}'")

    bus = EventHandler()
    '''
    TO BE IMPLEMENTED
    Subscribing the SubHandlers
    '''
    await bus.start()

    connection_handler = ConnectionHandler(reader, writer, args.device_type)
    connection_handler.event_callback = bus.put_event
    await connection_handler.start()

    registered_device_id = await register_device(connection_handler, args.device_type)
    if registered_device_id is None:
        print("Registration did not complete.")

    try:
        while True:
            message = await asyncio.to_thread(input, "Client > ")
            if message.lower() in {"exit", "quit"}:
                break

            response = await connection_handler.send_and_wait(message)
            print(f"Server > {response}")
    finally:
        await connection_handler.stop()
        await bus.stop()
