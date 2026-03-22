from pathlib import Path
import sys
import asyncio


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from smart_home.client.controllers.connection_handler import ConnectionHandler


class FakeReader:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[bytes] = asyncio.Queue()

    async def readline(self) -> bytes:
        return await self._queue.get()

    async def feed_line(self, text: str) -> None:
        await self._queue.put(f"{text}\n".encode("utf-8"))

    async def feed_eof(self) -> None:
        await self._queue.put(b"")


class FakeWriter:
    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, data: bytes) -> None:
        self.writes.append(data)

    async def drain(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return None


def _extract_request_id(raw_wire_message: bytes) -> str:
    message = raw_wire_message.decode("utf-8").rstrip("\n")
    request_id, _ = message.split("|", 1)
    return request_id


def test_send_and_wait_success():
    async def scenario() -> None:
        reader = FakeReader()
        writer = FakeWriter()
        handler = ConnectionHandler(reader, writer, "light")
        await handler.start()

        request_task = asyncio.create_task(handler.send_and_wait("TURN_ON", timeout=1.0))
        await asyncio.sleep(0)

        request_id = _extract_request_id(writer.writes[-1])
        await reader.feed_line(f"{request_id}|ACK_OK")

        result = await request_task
        assert result == "ACK_OK"

        await handler.stop()

    asyncio.run(scenario())


def test_send_and_wait_timeout():
    async def scenario() -> None:
        reader = FakeReader()
        writer = FakeWriter()
        handler = ConnectionHandler(reader, writer, "thermostat")
        await handler.start()

        try:
            await handler.send_and_wait("SET_22", timeout=0.02)
            assert False, "Expected TimeoutError"
        except TimeoutError as exc:
            assert "No response received" in str(exc)

        await handler.stop()

    asyncio.run(scenario())


def test_disconnect_fails_pending_futures():
    async def scenario() -> None:
        reader = FakeReader()
        writer = FakeWriter()
        handler = ConnectionHandler(reader, writer, "socket")
        await handler.start()

        request_task = asyncio.create_task(handler.send_and_wait("TURN_OFF", timeout=1.0))
        await asyncio.sleep(0)
        await reader.feed_eof()

        try:
            await request_task
            assert False, "Expected ConnectionError"
        except ConnectionError as exc:
            assert "Connection closed by server" in str(exc)

        await handler.stop()

    asyncio.run(scenario())


def test_multiple_parallel_requests_are_correlated():
    async def scenario() -> None:
        reader = FakeReader()
        writer = FakeWriter()
        handler = ConnectionHandler(reader, writer, "light")
        await handler.start()

        task_a = asyncio.create_task(handler.send_and_wait("A", timeout=1.0))
        task_b = asyncio.create_task(handler.send_and_wait("B", timeout=1.0))
        task_c = asyncio.create_task(handler.send_and_wait("C", timeout=1.0))

        await asyncio.sleep(0)

        req_a = _extract_request_id(writer.writes[0])
        req_b = _extract_request_id(writer.writes[1])
        req_c = _extract_request_id(writer.writes[2])

        await reader.feed_line(f"{req_b}|RESP_B")
        await reader.feed_line(f"{req_c}|RESP_C")
        await reader.feed_line(f"{req_a}|RESP_A")

        results = await asyncio.gather(task_a, task_b, task_c)
        assert results == ["RESP_A", "RESP_B", "RESP_C"]

        await handler.stop()

    asyncio.run(scenario())
