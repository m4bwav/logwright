# Browser game (JS)

Keeps events in localStorage and offers a download. No fetch, no beacon.

```js
const KEY = "telemetry", sid = crypto.randomUUID().slice(0, 12);
export const telemetry = {
  enabled: () => localStorage.getItem("telemetry_opt_in") === "1",
  log(ev, f = {}) {
    if (!this.enabled()) return;
    const rows = JSON.parse(localStorage.getItem(KEY) || "[]");
    rows.push({ ts: new Date().toISOString(), sid, ev, f });
    localStorage.setItem(KEY, JSON.stringify(rows.slice(-5000)));
  },
  download() {
    const rows = JSON.parse(localStorage.getItem(KEY) || "[]");
    const blob = new Blob([rows.map((r) => JSON.stringify(r)).join("\n") + "\n"], { type: "application/jsonl" });
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: `play-${sid}.jsonl` });
    a.click();
  },
};
window.addEventListener("error", (e) => telemetry.log("error", { msg: String(e.message), where: `${e.filename}:${e.lineno}` }));
```

Give the player (or parent) a visible "download play log" button; that file is what `lgw.py query` reads.
