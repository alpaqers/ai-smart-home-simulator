from pathlib import Path
import os
import tomllib


CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.toml"
ENV_PATH = CONFIG_PATH.parent / ".env"


def load_dotenv() -> None:
    if not ENV_PATH.exists():
        return

    with ENV_PATH.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def load_config() -> dict:
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


load_dotenv()
config = load_config()


SERVER_CONFIG = config["server"]
HOST = os.getenv("SERVER_HOST", SERVER_CONFIG["host"])
PORT = int(os.getenv("SERVER_PORT", SERVER_CONFIG["port"]))
BUFFER_SIZE = int(os.getenv("SERVER_BUFFER_SIZE", SERVER_CONFIG["buffer_size"]))
TICK_INTERVAL_SECONDS = float(
    os.getenv("SERVER_TICK_INTERVAL_SECONDS", SERVER_CONFIG["tick_interval_seconds"])
)
AI_TICK_INTERVAL_SECONDS = float(
    os.getenv(
        "SERVER_AI_TICK_INTERVAL_SECONDS",
        SERVER_CONFIG["ai_tick_interval_seconds"],
    )
)

CLIENT_CONFIG = config["client"]
SERVER_HOST = os.getenv("CLIENT_SERVER_HOST", CLIENT_CONFIG["server_host"])
SERVER_PORT = int(os.getenv("CLIENT_SERVER_PORT", CLIENT_CONFIG["server_port"]))

AI_CONFIG = config.get("ai", {})
AI_PROVIDER = os.getenv("AI_PROVIDER", AI_CONFIG.get("provider", ""))
AI_ENDPOINT = os.getenv("AI_ENDPOINT", AI_CONFIG.get("endpoint", ""))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", AI_CONFIG.get("gemini_api_key", ""))
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    AI_CONFIG.get("gemini_model", "gemini-3.5-flash"),
)
