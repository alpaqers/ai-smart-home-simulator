// Polls the device state endpoint and live-updates the dashboard cards.
// The server pushes periodic state ticks into the client's in-memory storage;
// this keeps the displayed values fresh without a full page reload.
(function () {
    "use strict";

    const POLL_MS = 2000;
    const grid = document.getElementById("device-grid");
    if (!grid) {
        return;
    }

    function updateCard(card, device) {
        const stateList = card.querySelector(".state-list");
        if (!stateList) {
            return;
        }

        Object.keys(device.device_state).forEach(function (key) {
            const value = device.device_state[key];
            let row = stateList.querySelector('.kv-row[data-key="' + key + '"]');

            if (!row) {
                row = document.createElement("div");
                row.className = "kv-row";
                row.dataset.key = key;
                row.innerHTML = '<dt></dt><dd class="state-value"></dd>';
                row.querySelector("dt").textContent = key;
                stateList.appendChild(row);
            }

            const valueEl = row.querySelector(".state-value");
            if (valueEl && valueEl.textContent !== String(value)) {
                valueEl.textContent = value;
                valueEl.classList.remove("flash");
                // Force reflow so the animation can restart.
                void valueEl.offsetWidth;
                valueEl.classList.add("flash");
            }
        });
    }

    async function poll() {
        try {
            // Carry the dashboard's active type filter so the polled set matches
            // the rendered cards (otherwise the counts never align and the page
            // would reload endlessly while filtering).
            const url = "/api/devices/" + window.location.search;
            const response = await fetch(url, { headers: { "Accept": "application/json" } });
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            const byId = {};
            data.devices.forEach(function (d) { byId[d.device_id] = d; });

            grid.querySelectorAll(".card").forEach(function (card) {
                const id = card.dataset.deviceId;
                if (byId[id]) {
                    updateCard(card, byId[id]);
                }
            });

            // Reload when the set of devices changed (added elsewhere / first state).
            const renderedCount = grid.querySelectorAll(".card").length;
            if (data.devices.length !== renderedCount) {
                window.location.reload();
            }
        } catch (err) {
            // Network hiccup; try again on the next tick.
        }
    }

    setInterval(poll, POLL_MS);
    poll();
})();
