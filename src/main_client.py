import asyncio
import argparse

from smart_home.client.views.cli import parse_args

from smart_home.client.client import start_client

def main() -> None:
    args = parse_args()
    try:
        asyncio.run(start_client(args))
    except KeyboardInterrupt:
        print("\nClient stopped")


if __name__ == "__main__":
    main()