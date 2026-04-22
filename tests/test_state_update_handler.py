from pathlib import Path
import sys
import base64


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from smart_home.client.controllers.event_router import ClientEventRouter
from smart_home.client.models.containers import DeviceStorage
from smart_home.client.models.device import Device
from smart_home.client.models.device_storage import save_device
from smart_home.proto.v1 import message_pb2


def test_device_state_update_event_updates_storage():
    storage = DeviceStorage()
    router = ClientEventRouter(storage)
    device = Device(device_id=7, device_type="lamp", device_state={"power": "OFF"})
    ok, _ = save_device(storage, device)
    assert ok is True

    update = message_pb2.DeviceStateUpdate()
    update.device_id = 7
    update.timestamp = 1710000000
    update.command_type = 1
    update.parameters["power"] = "ON"

    payload_b64 = base64.b64encode(update.SerializeToString()).decode("utf-8")

    handled = router.handle(payload_b64)

    assert handled is True
    assert storage.lamps[7].device_state["power"] == "ON"


def test_non_update_payload_is_ignored():
    storage = DeviceStorage()
    router = ClientEventRouter(storage)

    handled = router.handle("not_base64_payload")

    assert handled is False


def test_update_for_unknown_device_returns_false():
    storage = DeviceStorage()
    router = ClientEventRouter(storage)

    update = message_pb2.DeviceStateUpdate()
    update.device_id = 404
    update.timestamp = 1710000000
    update.command_type = 1
    update.parameters["power"] = "ON"

    payload_b64 = base64.b64encode(update.SerializeToString()).decode("utf-8")

    handled = router.handle(payload_b64)

    assert handled is False
