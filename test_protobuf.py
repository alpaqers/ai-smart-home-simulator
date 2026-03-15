from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from smart_home.proto.v1 import message_pb2


msg = message_pb2.DeviceStateChange()
msg.device_id = 1
msg.device_type = 2
msg.parameters["temperature"] = "24.6"

data = msg.SerializeToString()
print(data)

received = message_pb2.DeviceStateChange()
received.ParseFromString(data)

print(received.device_id)
print(received.device_type)
print(received.parameters["temperature"])