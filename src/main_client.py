import argparse
import asyncio

from smart_home.client.client import start_client


def _select_frontend() -> str:
    parser = argparse.ArgumentParser(description="Smart Home Client")
    parser.add_argument(
        "--frontend",
        choices=["cli", "web"],
        default="cli",
        help="Which frontend to launch (cli or web).",
    )
    args, _ = parser.parse_known_args()
    return args.frontend


def main() -> None:
    frontend = _select_frontend()
    try:
        asyncio.run(start_client(frontend=frontend))
    except KeyboardInterrupt:
        print("\nClient stopped")


if __name__ == "__main__":
    main()
