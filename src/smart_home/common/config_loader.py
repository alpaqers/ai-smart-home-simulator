from pathlib import Path
import os
import tomllib


CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.toml"


def load_config() -> dict:
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


config = load_config()


SERVER_CONFIG = config["server"]
HOST = os.getenv("SERVER_HOST", SERVER_CONFIG["host"])
PORT = int(os.getenv("SERVER_PORT", SERVER_CONFIG["port"]))
BUFFER_SIZE = int(os.getenv("SERVER_BUFFER_SIZE", SERVER_CONFIG["buffer_size"]))
TICK_INTERVAL_SECONDS = float(
    os.getenv("SERVER_TICK_INTERVAL_SECONDS", SERVER_CONFIG["tick_interval_seconds"])
)

CLIENT_CONFIG = config["client"]
SERVER_HOST = os.getenv("CLIENT_SERVER_HOST", CLIENT_CONFIG["server_host"])
SERVER_PORT = int(os.getenv("CLIENT_SERVER_PORT", CLIENT_CONFIG["server_port"]))
