import asyncio
import contextlib
import uuid

from asyncio import StreamReader, StreamWriter


class ConnectionHandler:
    def __init__(self, reader: StreamReader, writer: StreamWriter, device_type: str) -> None:
        self.reader = reader
        self.writer = writer
        self.device_type = device_type
        self._pending: dict[str, asyncio.Future[str]] = {}
        self._write_lock = asyncio.Lock()
        self._reader_task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._reader_task = asyncio.create_task(self._read_loop())

    async def stop(self) -> None:
        if not self._running and self._reader_task is None:
            return

        self._running = False
        if self._reader_task is not None:
            self._reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task
            self._reader_task = None

        self.writer.close()
        with contextlib.suppress(ConnectionError):
            await self.writer.wait_closed()

    async def send_and_wait(self, payload: str, timeout: float = 5.0) -> str:
        if not self._running:
            raise RuntimeError("Connection handler is not started")

        request_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()
        self._pending[request_id] = future

        wire_message = f"{request_id}|{payload}\n"

        try:
            async with self._write_lock:
                self.writer.write(wire_message.encode("utf-8"))
                await self.writer.drain()

            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise TimeoutError(f"No response received within {timeout:.2f}s") from exc
        finally:
            self._pending.pop(request_id, None)

    async def _read_loop(self) -> None:
        try:
            while self._running:
                data = await self.reader.readline()
                if not data:
                    break

                message = data.decode("utf-8").rstrip("\n")
                if "|" not in message:
                    continue

                request_id, response = message.split("|", 1)
                future = self._pending.get(request_id)
                if future is not None and not future.done():
                    future.set_result(response)
        except asyncio.CancelledError:
            raise
        finally:
            self._running = False
            self._fail_all_pending(ConnectionError("Connection closed by server"))

    def _fail_all_pending(self, exc: Exception) -> None:
        for future in list(self._pending.values()):
            if not future.done():
                future.set_exception(exc)


async def handle_connection(reader: StreamReader, writer: StreamWriter, device_type: str) -> None:
    handler = ConnectionHandler(reader, writer, device_type)
    await handler.start()

    try:
        while True:
            message = await asyncio.to_thread(input, "Client > ")
            if message.lower() in {"exit", "quit"}:
                break

            response = await handler.send_and_wait(message)
            print(f"Server > {response}")
    finally:
        await handler.stop()