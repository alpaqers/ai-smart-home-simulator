from pathlib import Path
import tomllib


CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.toml"


def load_config() -> dict:
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


config = load_config()


SERVER_CONFIG = config["server"]
HOST = SERVER_CONFIG["host"]
PORT = SERVER_CONFIG["port"]
BUFFER_SIZE = SERVER_CONFIG["buffer_size"]


CLIENT_CONFIG = config["client"]
SERVER_HOST = CLIENT_CONFIG["server_host"]
SERVER_PORT = CLIENT_CONFIG["server_port"]