---
marp: true

paginate: true
---

# Mój wkład (Adrian) (Client) 
**Skupiłem się na:** stabilnej komunikacji + obsłudze aktualizacji stanu urządzeń  
**W skrócie:**
- `ConnectionHandler` (request/response, timeouty, równoległość)
- `ClientEventRouter` + `DeviceStorage` (aktualizacja stanu po eventach)
- Testy jednostkowe (żeby to było “pewne” i łatwe do rozwijania)
**Efekt:** klient obsługuje równoległe requesty bez mieszania odpowiedzi + bezpiecznie się zamyka.
---

## 1) Problem, który rozwiązałem
W kliencie TCP pojawiają się 3 problemy:
- odpowiedzi mogą przychodzić w innej kolejności niż wysyłane requesty
- bez korelacji request→response robi się chaos
- bez testów rozwój klienta jest ryzykowny

**Cel:** uporządkować fundament klienta tak, żeby dało się go rozbudowywać.
**Konsekwecnje** błędnej implementacji: błędne sterowanie urządzeniem, bo odpowiedź A trafia do requestu B

---

## 2) ConnectionHandler — stabilny transport
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
---

## 3) ClientEventRouter - aktualizacja stanu
Zaimplementowałem ClientEventRouter, który:

- przyjmuje surowy payload,
- próbuje rozpoznać jaki to typ zdarzenia,
- deleguje do dedykowanej metody \_handle\_<event>()
- zwraca True/False czy event był rozpoznany i obsłużony
  - jeśli dekodowanie się uda wykonuje zadane polecenie np. update stanu DeviceStorage
  - jeśli nie zwraca False, a event pozostaje nierozpoznany.

---


## 4) Testy — co weryfikuję (branch `client`)
W `tests/` dodałem testy, które sprawdzają kluczowe elementy klienta:

- **ConnectionHandler (transport / request→response):**
  - poprawne mapowanie odpowiedzi po `request_id`
  - **timeouty** i poprawny błąd gdy brak odpowiedzi
  - zachowanie przy **rozłączeniu** (pending request kończy się błędem)
  - **równoległe requesty** + odpowiedzi w innej kolejności (bez pomieszania)

- **EventHandler (event bus):**
  - event trafia **raz** do każdego subskrybenta
  - działają subscriberzy sync i async
  - `stop()` kończy task w tle “czysto”
---
- **ClientEventRouter + DeviceStorage (aktualizacja stanu):**
  - event `DeviceStateUpdate` aktualizuje stan urządzenia w storage
  - błędny payload / nieznane urządzenie → event ignorowany (`False`)