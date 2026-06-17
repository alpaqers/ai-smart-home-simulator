from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.server.events import TimeShiftEvent
from smart_home.server.message_handler import decode_wire_message, parse_envelope
from smart_home.server.processors.time_shift import TimeShiftProcessor
from smart_home.server.time_service import TimeService


@pytest.mark.asyncio
async def test_time_shift_processor_sets_time_and_sends_response() -> None:
    time_service = TimeService()
    time_service.use_simulated_time(datetime(2025, 6, 13, 12, 0, 0))
    processor = TimeShiftProcessor(time_service)

    writer = Mock()
    writer.write = Mock()
    writer.drain = AsyncMock()

    event = TimeShiftEvent(
        request_id="req-time-1",
        writer=writer,
        year=2025,
        month=7,
        day=1,
        hour=8,
        minute=30,
        second=0,
    )

    await processor.handle(event)

    assert time_service.now() == datetime(2025, 7, 1, 8, 30, 0)

    writer.write.assert_called_once()
    writer.drain.assert_awaited_once()

    sent_request_id, sent_proto_bytes = decode_wire_message(writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)

    assert sent_request_id == "req-time-1"
    assert sent_envelope.WhichOneof("payload") == "time_shift_resp"
    assert sent_envelope.time_shift_resp.success is True
