"""Django request handlers for the smart-home web frontend.

These views are the web equivalent of the CLI's ``device_service`` helpers.
They deliberately re-orchestrate the same underlying controllers
(``create_device``, ``register_device``, ``add_device_to_storage`` ...) instead
of reusing the CLI helpers, because those helpers prompt via ``input()`` and
print to stdout. The reusable core is shared; only the view layer differs.
"""

from __future__ import annotations

import asyncio
import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ...controllers.connection_controller import add_connection, get_connection
from ...controllers.connection_handler import ConnectionHandler
from ...controllers.device_controller import (
    get_all_devices,
    get_devices_by_type,
    update_device_state,
)
from ...controllers.device_factory import create_device
from ...controllers.device_registry import add_device_to_storage
from ...controllers.message_coder import encode_state_change
from ...controllers.message_sender import register_device
from ...models.device import _CAPABILITIES_SCHEMA, _STATE_SCHEMA, Device
from ....common.config_loader import SERVER_HOST, SERVER_PORT
from .runtime import call_async, get_context

# Device types offered in the UI. ``ac``/``airconditioning`` share a schema, so
# only the canonical ``ac`` is surfaced.
_DEVICE_TYPES = ["lamp", "thermometer", "sensor", "ac"]


def _serialize_device(device: Device) -> dict:
    return {
        "device_id": device.device_id,
        "device_type": device.device_type,
        "capabilities": dict(device.capabilities or {}),
        "device_state": dict(device.device_state or {}),
        "state_fields": _STATE_SCHEMA.get(device.device_type.lower(), []),
    }


def _devices_serialized(filter_type: str = "") -> list[dict]:
    ctx = get_context()
    if filter_type:
        devices = get_devices_by_type(ctx.device_storage, filter_type)
    else:
        devices = get_all_devices(ctx.device_storage)
    devices = sorted(devices, key=lambda d: d.device_id or 0)
    return [_serialize_device(d) for d in devices]


async def _orchestrate_add(
    device_type: str,
    capabilities: dict[str, str],
    device_state: dict[str, str],
) -> tuple[Device | None, str]:
    """Async add flow mirroring ``device_service._add_device`` without prompts."""

    ctx = get_context()
    device = create_device(device_type, capabilities, device_state)

    reader, writer = await asyncio.open_connection(host=SERVER_HOST, port=SERVER_PORT)
    handler = ConnectionHandler(reader, writer, device_type)
    handler.event_callback = ctx.bus.put_event
    await handler.start()

    registered_id = await register_device(handler, device_type, capabilities, device_state)
    if registered_id is None:
        await handler.stop()
        return None, f"Failed to register device with type '{device_type}'."

    device.device_id = registered_id

    ok, msg = add_device_to_storage(ctx.device_storage, device)
    add_connection(ctx.connection_storage, registered_id, handler)

    ctx.logger.info(msg) if ok else ctx.logger.error(msg)
    return device, msg


async def _orchestrate_state_change(device: Device, new_state: dict[str, str]) -> None:
    """Send a state change to the server over the device's own connection."""

    ctx = get_context()
    handler = get_connection(ctx.connection_storage, device.device_id)
    if handler is None:
        ctx.logger.error(f"No active connection for device {device.device_id}.")
        return

    payload = encode_state_change(device.device_id, new_state, device.device_type)
    await handler.send_and_wait(payload)


def dashboard(request):
    filter_type = request.GET.get("type", "").strip().lower()
    ctx = get_context()

    if filter_type:
        devices = get_devices_by_type(ctx.device_storage, filter_type)
    else:
        devices = get_all_devices(ctx.device_storage)

    devices = sorted(devices, key=lambda d: d.device_id or 0)

    context = {
        "devices": [_serialize_device(d) for d in devices],
        "device_types": _DEVICE_TYPES,
        "filter_type": filter_type,
    }
    return render(request, "web/index.html", context)


@require_http_methods(["GET", "POST"])
def add_device(request):
    if request.method == "POST":
        device_type = request.POST.get("device_type", "").strip().lower()

        if device_type not in _CAPABILITIES_SCHEMA:
            return render(
                request,
                "web/add_device.html",
                _add_form_context(error=f"Unknown device type '{device_type}'."),
            )

        capabilities = _collect_fields(request.POST, _CAPABILITIES_SCHEMA.get(device_type, []), "cap_")
        device_state = _collect_fields(request.POST, _STATE_SCHEMA.get(device_type, []), "state_")

        try:
            device, msg = call_async(_orchestrate_add(device_type, capabilities, device_state))
        except Exception as exc:  # pragma: no cover - surfaced to the user
            return render(
                request,
                "web/add_device.html",
                _add_form_context(error=f"Could not add device: {exc}"),
            )

        if device is None:
            return render(request, "web/add_device.html", _add_form_context(error=msg))

        return redirect("dashboard")

    return render(request, "web/add_device.html", _add_form_context())


@require_http_methods(["POST"])
def update_device(request, device_id: int):
    ctx = get_context()
    device = next(
        (d for d in get_all_devices(ctx.device_storage) if d.device_id == device_id),
        None,
    )
    if device is None:
        return redirect("dashboard")

    fields = _STATE_SCHEMA.get(device.device_type.lower(), [])
    new_state = {
        key: request.POST[key].strip()
        for key in fields
        if request.POST.get(key, "").strip()
    }

    if new_state:
        success, message = update_device_state(ctx.device_storage, device_id, new_state)
        if success:
            try:
                call_async(_orchestrate_state_change(device, new_state))
                ctx.logger.info(f"State change sent: device={device_id} state={new_state}")
            except Exception as exc:  # pragma: no cover - surfaced to the user
                ctx.logger.error(f"Failed to send state change: {exc}")
        else:
            ctx.logger.error(message)

    return redirect("dashboard")


def api_devices(request):
    filter_type = request.GET.get("type", "").strip().lower()
    return JsonResponse({"devices": _devices_serialized(filter_type)})


def _collect_fields(post_data, fields: list[str], prefix: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in fields:
        value = post_data.get(f"{prefix}{key}", "").strip()
        if value:
            result[key] = value
    return result


def _add_form_context(error: str | None = None) -> dict:
    schema = {
        dtype: {
            "capabilities": _CAPABILITIES_SCHEMA.get(dtype, []),
            "state": _STATE_SCHEMA.get(dtype, []),
        }
        for dtype in _DEVICE_TYPES
    }
    return {
        "device_types": _DEVICE_TYPES,
        "schema_json": json.dumps(schema),
        "error": error,
    }
