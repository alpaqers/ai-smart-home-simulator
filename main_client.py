import asyncio

from app.client.client import start_client


def main() -> None:
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print("\nClient stopped")


if __name__ == "__main__":
    main()