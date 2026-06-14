from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta

from smart_home.client.controllers.connection_handler import ConnectionHandler
from smart_home.client.controllers.message_coder import (
    decode_register_response,
    decode_state_change_response,
    encode_register_request,
    encode_state_change,
)
from smart_home.client.models.device import Device
from smart_home.common.config_loader import SERVER_HOST, SERVER_PORT
from smart_home.demo.scenario import (
    DEMO_DEVICE_DEFINITIONS,
    START_DATE,
    build_history_records,
    to_timestamp,
)


@dataclass
class DemoSeedResult:
    device_connections: list[tuple[Device, ConnectionHandler]] = field(default_factory=list)
    history_records: int = 0

    @property
    def devices(self) -> list[Device]:
        return [device for device, _handler in self.device_connections]

    @property
    def handlers(self) -> list[ConnectionHandler]:
        return [handler for _device, handler in self.device_connections]


async def seed_demo_scenario(
    *,
    host: str = SERVER_HOST,
    port: int = SERVER_PORT,
    simulation_days: int = 10,
) -> DemoSeedResult:
    device_connections: list[tuple[Device, ConnectionHandler]] = []
    registered_at = to_timestamp(START_DATE - timedelta(days=1))

    for device_id, device_type, capabilities, device_state in DEMO_DEVICE_DEFINITIONS:
        reader, writer = await asyncio.open_connection(host=host, port=port)
        handler = ConnectionHandler(reader, writer, device_type)
        await handler.start()

        payload_b64, _req = encode_register_request(
            device_type,
            capabilities,
            device_state,
            device_id=device_id,
            timestamp=registered_at,
        )
        response_b64 = await handler.send_and_wait(payload_b64, timeout=10.0)
        resp = decode_register_response(response_b64)
        if resp is None or not resp.success:
            await handler.stop()
            cause = resp.cause if resp is not None else "invalid response"
            raise RuntimeError(f"Failed to register device {device_id} ({device_type}): {cause}")

        device_connections.append(
            (
                Device(
                    device_id=device_id,
                    device_type=device_type,
                    capabilities=dict(capabilities),
                    device_state=dict(device_state),
                ),
                handler,
            )
        )

    admin_reader, admin_writer = await asyncio.open_connection(host=host, port=port)
    admin = ConnectionHandler(admin_reader, admin_writer, "demo-admin")
    await admin.start()

    history_records = build_history_records(simulation_days=simulation_days)
    for device_id, timestamp, parameters in history_records:
        payload = encode_state_change(
            device_id,
            parameters,
            device_id,
            timestamp=timestamp,
        )
        response_b64 = await admin.send_and_wait(payload, timeout=10.0)
        resp = decode_state_change_response(response_b64)
        if resp is None or not resp.success:
            detail = resp.message if resp is not None else "invalid response"
            raise RuntimeError(
                f"Failed to record history for device {device_id}: {detail}"
            )

    await admin.stop()
    return DemoSeedResult(
        device_connections=device_connections,
        history_records=len(history_records),
    )


def print_seed_summary(result: DemoSeedResult) -> None:
    print()
    print("Demo data loaded")
    print(f"  devices={len(result.devices)}")
    print(f"  history_records={result.history_records}")
