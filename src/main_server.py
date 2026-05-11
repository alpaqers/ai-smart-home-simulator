import asyncio

from smart_home.server.server import start_server


def main() -> None:
    asyncio.run(start_server())


if __name__ == "__main__":
    main()