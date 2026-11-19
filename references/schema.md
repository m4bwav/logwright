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
