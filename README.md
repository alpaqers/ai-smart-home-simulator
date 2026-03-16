# AI Smart Home Simulator

Minimal TCP client/server simulator built with `asyncio`.

At this stage, the project supports basic TCP communication between client and server.
The server listens on port `9999`, and settings can be changed in `config.toml`.

---

# Requirements

- Python 3.11+
- Linux or Windows
- Docker (optional, for containerized run)

---

# Local Setup (venv)

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main_server.py
python src/main_client.py
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main_server.py
python src/main_client.py
```

Deactivate venv:

```bash
deactivate
```

---

# Docker: Start Server + Client

1. Start only the server in background:

```bash
docker compose up -d server
```

2. Start client session:

```bash
docker compose run --rm client
```

3. In the client prompt (`Client >`), type your message and press Enter.

4. (Optional) In another terminal, watch server logs:

```bash
docker compose logs -f server
```

5. Stop everything:

```bash
docker compose down
```