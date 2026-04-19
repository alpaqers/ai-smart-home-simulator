---
marp: true
title: "AI Smart Home Simulator — mój wkład (client)"
author: "Adrian Zienkiewicz (Zienek12)"
paginate: true
---

# Mój wkład (Client) — 3 min
**Skupiłem się na:** stabilnej komunikacji + kontrakcie danych + obsłudze aktualizacji stanu urządzeń  
**W skrócie:**
- `ConnectionHandler` (request/response, timeouty, równoległość)
- Protobuf + `message_coder` (enkodowanie/dekodowanie, walidacja)
- `ClientEventRouter` + `DeviceStorage` (aktualizacja stanu po eventach)
- Testy jednostkowe (żeby to było “pewne” i łatwe do rozwijania)

---

## 1) Problem, który rozwiązałem
W kliencie TCP pojawiają się 4 szybkie problemy:
- odpowiedzi mogą przychodzić w innej kolejności niż wysyłane requesty
- bez korelacji request→response robi się chaos
- brak kontraktu danych utrudnia rozwój (stringi, brak walidacji)
- bez testów rozwój klienta jest ryzykowny

**Cel:** uporządkować fundament klienta tak, żeby dało się go rozbudowywać bez regresji.

---

## 2) ConnectionHandler — stabilny transport
Wprowadziłem/rozwinąłem `ConnectionHandler`, który:
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

## 3) EventRouter