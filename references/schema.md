# Event schema

One JSON object per line (JSONL), appended to a local file.

| Key | Type | Required | Meaning |
|---|---|---|---|
| `ts` | string | yes | ISO 8601 UTC time |
| `sid` | string | yes | random per play session, made at start |
| `ev` | string | yes | event name, dotted: `level.fail`, `session.end`, `crash` |
| `iid` | string | no | random per install; leave out for child games |
| `build` | string | no | build or version string |
| `scene` | string | no | level or scene name |
| `f` | object | no | event fields: numbers and short codes |

Forbidden in any key: `name`, `email`, `ip`, `username`, `address`, `phone`, `real_name`. Free text a player types stays out unless the game's owner asks for it, and it never leaves the machine.

Starter set: `session.start`, `session.end`, `level.start`, `level.complete`, `level.fail` (f: level, t, cause), `death`, `retry`, `stuck` (no progress for N seconds), `economy.in` and `economy.out` (f: item, n), `setting.change`, `error` (f: msg, where).

`query` reads `*fail*`, `*death*`, `*retry*` and `*stuck*` events as balance signals, counted per `f.level` (else `scene`), and the scene of `session.end` as the quit point. A run that reached its end sends `session.end` with `f.finished: true`; finished sessions are not quits.

## Teaching beats (onboarding funnel)

Plan one event pair per tutorial beat, with a small fixed field set and nothing else:

- `beat.start` (f: `beat`) when the beat begins.
- `beat.complete` (f: `beat`, `deaths`, `t` seconds, `device` as a short code such as `desktop`, `touch` or `pad`, optional `struggled`).
- `pause` (f: `cta_shown` true or false) if a pause screen shows a store or wishlist prompt, so its reach can be counted.

`struggled` is derived: deaths or seconds at or past a threshold (`query` defaults 3 deaths or 120 s; change with `--struggle-deaths` and `--struggle-secs`). A game may send its own boolean `struggled`, and that wins. `query` adds `beats`: per beat the sessions started and completed, struggle rate, drop-off (started, never completed) and median time, worst first. With `--grind` a beat at 30% struggle or 20% drop-off becomes a balance proposal. No player names or device IDs; `device` is a class, never a model or serial. For a kids game keep the store prompt fields out entirely.
