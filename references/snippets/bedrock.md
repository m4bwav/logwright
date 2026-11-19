# Minecraft Bedrock (Script API, behavior pack)

The Script API has no file access; print to the content log, which BDS writes to stdout.

```js
import { world } from "@minecraft/server";
const sid = Math.random().toString(36).slice(2, 14);
export function log(ev, f = {}) {
  console.warn("TELEMETRY " + JSON.stringify({ ts: new Date().toISOString(), sid, ev, f }));
}
world.afterEvents.entityDie.subscribe((e) => {
  if (e.deadEntity.typeId === "minecraft:player") log("death", { cause: e.damageSource.cause });
});
```

Collect from BDS stdout or the content log; keep `TELEMETRY ` lines into a `.jsonl`. BDS runs behavior packs only, so client UI events cannot be logged there. Java mods: read `logs/latest.log` and `crash-reports/` directly.
