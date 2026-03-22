import asyncio

from smart_home.server.server import start_server


def main() -> None:
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()