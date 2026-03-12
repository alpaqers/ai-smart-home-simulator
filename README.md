# AI Smart Home Simulator – Server

Minimalny serwer TCP z `asyncio`.
Na obecnym etapie umożliwia podstawową komunikację klient ↔ serwer przez TCP na localhost.
Serwer nasłuchuje na localhost, port 9999. Można łatwo zmienić w /server/app/config.py

---

# Wymagania

- Python 3.10+
- system Linux / Windows

---

# Setup środowiska (venv)

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main_server.py
python main_client.py

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main_server.py
python main_client.py

### Deaktywacja venv

```bash
deactivate