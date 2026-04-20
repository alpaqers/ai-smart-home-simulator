---
marp: true
theme: default
paginate: true
style: |
  :root {
    --color-bg: #FAFBFC;
    --color-fg: #2D3142;
    --color-primary: #028090;
    --color-secondary: #00A896;
    --color-accent: #F0F4F8;
    --color-muted: #6B7280;
    font-family: 'Calibri', 'Segoe UI', sans-serif;
  }
  section {
    background: var(--color-bg);
    color: var(--color-fg);
    padding: 50px 60px;
  }
  section.title-slide {
    background: linear-gradient(135deg, #028090 0%, #00A896 100%);
    color: #FFFFFF;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  section.title-slide h1 {
    font-size: 64px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #FFFFFF;
  }
  section.title-slide h3 {
    font-size: 28px;
    font-weight: 400;
    color: rgba(255,255,255,0.85);
    margin-top: 0;
  }
  section.title-slide .names {
    position: absolute;
    bottom: 30px;
    right: 50px;
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    text-align: right;
  }
  section.section-divider {
    background: linear-gradient(135deg, #028090 0%, #00A896 100%);
    color: #FFFFFF;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  section.section-divider h1 {
    font-size: 64px;
    color: #FFFFFF;
  }
  section.section-divider p {
    font-size: 28px;
    color: rgba(255,255,255,0.8);
  }
  h1 {
    color: var(--color-primary);
    font-size: 40px;
    font-weight: 700;
    border-bottom: 3px solid var(--color-secondary);
    padding-bottom: 8px;
    margin-bottom: 24px;
  }
  h2 {
    color: var(--color-primary);
    font-size: 28px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 12px;
  }
  h3 {
    color: #374151;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  ul, ol {
    font-size: 22px;
    line-height: 1.6;
    color: #374151;
  }
  li {
    margin-bottom: 6px;
  }
  p {
    font-size: 22px;
    line-height: 1.6;
    color: #374151;
  }
  code {
    background: #E8F4F8;
    color: #028090;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 20px;
  }
  pre {
    background: #1E293B;
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 16px;
  }
  pre code {
    background: none;
    color: #E2E8F0;
    padding: 0;
  }
  .card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .highlight {
    background: linear-gradient(135deg, #E0F7FA, #E8F5E9);
    border-left: 4px solid var(--color-primary);
    padding: 12px 18px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
  }
  .two-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-top: 16px;
  }
  .tag {
    display: inline-block;
    background: #E0F7FA;
    color: #028090;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 18px;
    font-weight: 500;
    margin: 4px 5px;
  }
  .strikethrough {
    color: #9CA3AF;
    text-decoration: line-through;
  }
  .author-tag {
    position: absolute;
    bottom: 30px;
    left: 60px;
    font-size: 18px;
    color: #9CA3AF;
    font-style: italic;
  }
  table {
    font-size: 16px;
    border-collapse: collapse;
    width: 100%;
  }
  th {
    background: var(--color-primary);
    color: white;
    padding: 10px 16px;
    text-align: left;
  }
  td {
    padding: 10px 16px;
    border-bottom: 1px solid #E5E7EB;
  }
  tr:nth-child(even) {
    background: #F8FAFC;
  }
  .diagram {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    flex-wrap: nowrap;
    margin: 20px 0;
  }
  .diagram-box {
    background: #FFFFFF;
    border: 2px solid var(--color-secondary);
    border-radius: 10px;
    padding: 10px 18px;
    display: inline-block;
    font-weight: 600;
    color: var(--color-primary);
    font-size: 20px;
    white-space: nowrap;
  }
  .arrow {
    font-size: 24px;
    color: var(--color-secondary);
    white-space: nowrap;
  }
---

<!-- _class: title-slide -->
<!-- _paginate: false -->

# AI Smart Home Simulator

### Projekt zespołowy — Nokia
### 27 kwietnia 2026

---

# Temat

Środowisko symulujące system **smart home** z dwukierunkową komunikacją klient–serwer.

<div class="two-columns">
<div class="card">

### 🖥️ Klient
Symulator urządzeń domowych — generuje dane i wysyła je do serwera

</div>
<div class="card">

### ⚙️ Serwer
Odbiera dane, przetwarza je i podejmuje decyzje przy pomocy **AI**

</div>
</div>

<div class="highlight">

**Dlaczego symulator?** Fokus na aspekty projektowe, koncepcyjne i architektoniczne — bez potrzeby realnych urządzeń IoT czy chmury.

</div>

---

# Podejście

<div class="diagram">
<span class="diagram-box">Klient (MVC)</span>
<span class="arrow">⟵ TCP / Protobuf ⟶</span>
<span class="diagram-box">Serwer (Event Pipeline)</span>
</div>

<div class="two-columns">
<div>

### Klient — MVC
- **Model** — dane urządzenia, stan
- **View** — interfejs CLI
- **Controller** — logika, wysyłka wiadomości

</div>
<div>

### Serwer — Event Pipeline
- **EventBus** — publish / subscribe
- **Procesory** — niezależne moduły
- Procesory nie wiedzą o sobie nawzajem → **modularność**

</div>
</div>

---

# Narzędzia

<div class="two-columns" style="margin-top: 10px;">
<div>

<span class="tag">🐍 Python 3.10+ / asyncio</span>
<span class="tag">🔌 TCP (sockety)</span>
<span class="tag">📦 Protobuf</span>
<span class="tag">🐳 Docker + docker-compose</span>
<span class="tag">🧪 pytest</span>

</div>
<div>

<span class="tag">⌨️ argparse (CLI)</span>
<span class="tag">📄 TOML (konfiguracja)</span>
<span class="tag">🔀 Git</span>
<span class="tag">📋 Scrum</span>

</div>
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: false -->

# MVP

Minimal Viable Product

---

# MVP — Komunikacja

<div class="card">

- **Klient + serwer** — dwie osobne aplikacje
- **Dwukierunkowa komunikacja** przez TCP + Protobuf
- **Rejestracja** urządzenia w serwerze
- **Mapowanie** `device_id` → socket
- **Wysyłanie wiadomości** w obu kierunkach

</div>

<div class="diagram">
<span class="diagram-box">Klient</span>
<span class="arrow">— rejestracja →</span>
<span class="diagram-box">Serwer</span>
</div>
<div class="diagram">
<span class="diagram-box">Klient</span>
<span class="arrow">← aktualizacja —</span>
<span class="diagram-box">Serwer</span>
</div>

---

# MVP — Dane i logi

<div class="two-columns">
<div class="card">

### Serwer
- Stan urządzenia: **obecny + historia**
- Taski (automatyzacje)

</div>
<div class="card">

### Klient
- Stan urządzenia: **obecny**

</div>
</div>

<div class="card" style="margin-top: 16px;">

### Baza danych
**In-memory** — przechowywanie w pamięci aplikacji

</div>

<div class="card">

### Logi
Zmiany stanów · odebrane wiadomości · wysłane wiadomości

</div>

---

# MVP — Event Pipeline (serwer)

<div class="diagram">
<span class="diagram-box">TCP</span>
<span class="arrow">→</span>
<span class="diagram-box">EventBus</span>
<span class="arrow">→</span>
<span class="diagram-box">Procesory</span>
</div>

<div class="two-columns">
<div class="card">

### Mechanizm
- Definicje eventów
- Odbieranie i emitowanie
- Wzorzec **Observer** — subscribe na event

</div>
<div class="card">

### Procesory
- `RegisterReq` — rejestracja
- `StateChange` — zmiana stanu
- `Log` — logowanie

</div>
</div>

---

# MVP — Klient

<div class="card">

### Funkcjonalności
- Dodawanie i modyfikacja urządzeń **w runtime**
- Front interface — tworzenie kopert (wiadomości), modyfikacja
- `DeviceStateChange` — informowanie serwera o zmianach

</div>

<div class="card">

### Komponenty
- **EventHandler** + **SubHandlers** — obsługa zdarzeń
- **DeviceStorage** — lokalne przechowywanie stanu
- Odbiór `DeviceStateUpdate` i aktualizacja storage

</div>

---

# MVP — Podział tasków

<div class="two-columns">
<div class="card">

### Klient
- Interface (tworzenie, modyfikacja)
- `DeviceStateChange`
- EventHandler + SubHandlers
- DeviceStorage
- Odbiór `DeviceStateUpdate`

</div>
<div class="card">

### Serwer
- `RegisterReq` processor
- `DeviceStateChange` processor
- `Log` processor
- Wysyłanie wiadomości do klienta

</div>
</div>

<div style="margin-top: 16px; padding: 10px 18px; background: #F3F4F6; border-radius: 8px;">

<span class="strikethrough">Poza MVP: scheduler · taski · przechowywanie tasków</span>

</div>

---

<!-- _class: section-divider -->
<!-- _paginate: false -->

# Nasza implementacja

Co zrobiliśmy

---

# Konfiguracja i Docker

<div class="two-columns">
<div class="card">

### `config_loader` + `config.toml`
Konfiguracja serwera ładowana z pliku TOML:
- `host`, `port`, `buffer_size`
- Czytelny format, łatwy do edycji
- Oddzielenie konfiguracji od kodu

</div>
<div class="card">

### Docker + docker-compose
Konteneryzacja całego środowiska:
- `Dockerfile` — obraz `smart-home`
- Dwa serwisy: **server** i **client**

</div>
</div>

<div class="author-tag">Władek · serwer & klient</div>

---

# Event Bus & Device Management

<div class="author-tag">Łukasz · serwer</div>

---

# Event Bus

- Wprowadzono moduł `event_bus`
- Mechanizm:
  - publish / subscribe

## Cel w projekcie

- komunikacja po rejestracji urządzenia
- urządzenia publikują zdarzenia
- procesory subskrybują i obsługują eventy

<div class="author-tag">Łukasz · serwer</div>

---

# Integracja Event Bus

## connection_handler

- odbiera dane od urządzeń
- konwertuje dane do formatu eventu (envelope)
- publikuje eventy do Event Bus

## server.py

- inicjalizuje Event Bus
- rejestruje subskrypcje processorów

<div class="author-tag">Łukasz · serwer</div>

---

# Device Registry

- rejestracja urządzeń w systemie
- kontrola unikalności `device_id`

## Zmiany

- blokada duplikatów
- obsługa wyjątków przy rejestracji
- `response.success` zgodny z wynikiem operacji

<div class="author-tag">Łukasz · serwer</div>

---

# Procesory serwera

<div class="two-columns">
<div class="card">

### Osobne moduły
Każdy procesor w osobnym pliku — `RegisterProcessor`, `StateChangeProcessor`, `ResponseProcessor`

### `StateChangeProcessor`
1. Sprawdza czy urządzenie jest zarejestrowane
2. Tworzy `StateChangeRecord`
3. Zapisuje rekord do `DeviceStateHistory`

</div>
<div class="card">

### Testy
- Poprawne zachowanie dla **zarejestrowanych** urządzeń
- Ignorowanie eventów z **niezarejestrowanych** urządzeń

</div>
</div>

<div class="author-tag">Władek · serwer</div>

---

# Historia stanów urządzeń

<div class="card">

### `DeviceStateHistory`
- Async, thread-safe — `asyncio.Lock()`
- Przechowuje listę `StateChangeRecord` per `device_id`
- `append(record)` — dodaje nowy rekord
- `history_for(device_id)` — zwraca pełną historię zmian

</div>

<div class="diagram">
<span class="diagram-box">StateChangeEvent</span>
<span class="arrow">→</span>
<span class="diagram-box">Processor</span>
<span class="arrow">→</span>
<span class="diagram-box">rejestracja?</span>
<span class="arrow">→</span>
<span class="diagram-box">History</span>
</div>

<div class="author-tag">Władek · serwer</div>

---

# Klasa Device i kontenery

<div class="card">

### Inicjalizacja klasy Device
W folderze models zainicjalizowano klasę urządzenia z parametrami device_id, device_type, capabilities, device_state i parameters.

</div>

<div class="card">

### Inicjalizacja kontenerów na urządzenia
Utworzono przykładowe kontenery na urządzenia np. lampy, termometry, AC.

</div>

<div class="author-tag">Karolina · klient</div>

---

# Device Registry & State Change

## Device Registry
Utworzono funkcję, która po typie urządzenia, dodaje je do odpowiedniego kontenera.

## Device State Change

`encode_state_change` - funkcja przekształca dane o zmianie stanu urządzenia w ustandaryzowaną, zakodowaną binarnie paczkę (Base64), która jest gotowa do bezpiecznego przesłania przez sieć do serwera.

## State Handler
Zaimplementowano state handler, obsługujący zmianę stanu urządzenia. Ten plik to kontroler, który aktualizuje stan urządzenia w modelu, a następnie koordynuje proces jego kodowania i wysyłki do serwera.

<div class="author-tag">Karolina · klient</div>

---

# `main_client_v2.py`

- Punkt wejścia klienta
- Parsowanie argumentów z CLI (`--ip`, `--port`, `--device_type`)
- Uruchamia `start_client(args)` przez `asyncio.run()`

<div class="author-tag">Ania · klient</div>

---

# `device_factory.py`

- Funkcje pomocnicze do tworzenia urządzeń
- `create_lamp` → pyta o `brightness`
- `create_thermometer` → pyta o jednostkę temperatury
- `create_sensor` → pyta o `sensitivity`
- `create_ac` → pyta o docelową temperaturę
- Każda funkcja zwraca gotowy obiekt `Device`

<div class="author-tag">Ania · klient</div>

---

# `device_controller.py`

- Koordynator rejestracji urządzenia
- Na podstawie `device_type` wywołuje odpowiednią funkcję z factory
- Następnie wrzuca urządzenie do storage

<div class="author-tag">Ania · klient</div>

---

# `device_storage.py`

- Operacje na `DeviceStorage`
- `save_device` — zapisuje urządzenie do odpowiedniego kontenera
- `update_device_state` — aktualizuje stan urządzenia gdy serwer wyśle aktualizację

<div class="author-tag">Ania · klient</div>

---

# Mój wkład — Adrian (Klient)

**Skupiłem się na:** stabilnej komunikacji + obsłudze aktualizacji stanu urządzeń

**W skrócie:**
- `ConnectionHandler` (request/response, timeouty, równoległość)
- `ClientEventRouter` + `DeviceStorage` (aktualizacja stanu po eventach)
- Testy jednostkowe (żeby to było "pewne" i łatwe do rozwijania)

**Efekt:** klient obsługuje równoległe requesty bez mieszania odpowiedzi + bezpiecznie się zamyka.

<div class="author-tag">Adrian · klient</div>

---

# Problem, który rozwiązałem

W kliencie TCP pojawiają się 3 problemy:
- odpowiedzi mogą przychodzić w innej kolejności niż wysyłane requesty
- bez korelacji request→response robi się chaos
- bez testów rozwój klienta jest ryzykowny

**Cel:** uporządkować fundament klienta tak, żeby dało się go rozbudowywać.
**Konsekwencje** błędnej implementacji: błędne sterowanie urządzeniem, bo odpowiedź A trafia do requestu B

<div class="author-tag">Adrian · klient</div>

---

# ConnectionHandler — stabilny transport

Wprowadziłem `ConnectionHandler`, który:
- nadaje `request_id` do każdej wiadomości
- trzyma `_pending` → mapuje odpowiedź do właściwego requesta
- wspiera **timeouty** i bezpieczne zamykanie połączenia
- działa przy **wielu równoległych requestach**

```text
send_and_wait(payload):
  id = uuid()
  pending[id] = Future()
  write(id + "|" + payload)
  return await pending[id] with timeout

read_loop():
  id, resp = read().split("|")
  pending[id].set_result(resp)
```

<div class="author-tag">Adrian · klient</div>

---

# ClientEventRouter — aktualizacja stanu

Zaimplementowałem ClientEventRouter, który:

- przyjmuje surowy payload,
- próbuje rozpoznać jaki to typ zdarzenia,
- deleguje do dedykowanej metody \_handle\_\<event\>()
- zwraca True/False czy event był rozpoznany i obsłużony
  - jeśli dekodowanie się uda wykonuje zadane polecenie np. update stanu DeviceStorage
  - jeśli nie zwraca False, a event pozostaje nierozpoznany.

<div class="author-tag">Adrian · klient</div>

---

# Testy — co weryfikuję (1/2)

W `tests/` dodałem testy, które sprawdzają kluczowe elementy klienta:

- **ConnectionHandler (transport / request→response):**
  - poprawne mapowanie odpowiedzi po `request_id`
  - **timeouty** i poprawny błąd gdy brak odpowiedzi
  - zachowanie przy **rozłączeniu** (pending request kończy się błędem)
  - **równoległe requesty** + odpowiedzi w innej kolejności (bez pomieszania)

- **EventHandler (event bus):**
  - event trafia **raz** do każdego subskrybenta
  - działają subscriberzy sync i async
  - `stop()` kończy task w tle "czysto"

<div class="author-tag">Adrian · klient</div>

---

# Testy — co weryfikuję (2/2)

- **ClientEventRouter + DeviceStorage (aktualizacja stanu):**
  - event `DeviceStateUpdate` aktualizuje stan urządzenia w storage
  - błędny payload / nieznane urządzenie → event ignorowany (`False`)

<div class="author-tag">Adrian · klient</div>
