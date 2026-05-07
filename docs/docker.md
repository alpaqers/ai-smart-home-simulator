# Docker

The project includes a Dockerfile and Docker Compose setup for running the server
and a client container.

## Build

```bash
docker compose build
```

The image installs Python dependencies from `requirements.txt`, copies `config.toml`,
and copies the `src` tree.

## Run Server

Start the server in the background:

```bash
docker compose up -d server
```

Watch logs:

```bash
docker compose logs -f server
```

Stop services:

```bash
docker compose down
```

## Run Client

After the server is healthy, start an interactive client:

```bash
docker compose run --rm client
```

The Compose client command is:

```text
python src/main_client.py --device_type lamp
```

When the prompt appears, type:

```text
exit
```

to close the client.

## Docker Networking

Local development uses:

```toml
[server]
host = "127.0.0.1"

[client]
server_host = "localhost"
```

Inside Docker, those local defaults are overridden by environment variables:

- Server uses `SERVER_HOST=0.0.0.0` so it listens on the container network interface.
- Client uses `CLIENT_SERVER_HOST=server` so it connects to the Compose service name.

The server publishes container port `9999` to host port `9999`.

## Docker Compose Services

`server`:

- Builds `smart-home:latest`.
- Runs `python src/main_server.py`.
- Exposes port `9999`.
- Provides a TCP healthcheck.

`client`:

- Uses `smart-home:latest`.
- Depends on the server healthcheck.
- Runs `python src/main_client.py --device_type lamp`.
- Enables `stdin_open` and `tty` for interactive input.
