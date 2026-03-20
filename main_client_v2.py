import asyncio
import argparse

from app.client.client import start_client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart Home Device Client")
    parser.add_argument("--ip", type=str, default=None, help="Server IP address")
    parser.add_argument("--port", type=int, default=None, help="Server port")
    parser.add_argument("--device_type", type=str, required=True, help="Device type (e.g. lampka)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(start_client(args))
    except KeyboardInterrupt:
        print("\nClient stopped")


if __name__ == "__main__":
    main()