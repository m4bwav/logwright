# Where engines write logs

| Engine | File | Notes |
|---|---|---|
| Unity player (Windows) | `AppData/LocalLow/<Company>/<Product>/Player.log`, `Player-prev.log` | crash folder under `%TEMP%/<Company>/<Product>/Crashes` |
| Unity player (macOS) | `~/Library/Logs/<Company>/<Product>/Player.log` | |
| Unity editor (6) | `<project>/Logs/Editor.log` | global log only with `-useGlobalLog` |
| Unity batchmode tests | exit 0 pass, 8 tests failed, 6 did not finish | classify on the code first |
| Minecraft Java | `logs/latest.log`, `crash-reports/crash-*.txt` | |
| Minecraft Bedrock | content log; BDS stdout | behavior packs only on BDS |
| Roblox | Studio Output, `LogService:GetLogHistory()` | client logs in `%LOCALAPPDATA%/Roblox/logs` |
| Mod loaders | the loader's own log (for example `BepInEx/LogOutput.log`, `mods.log`) | read it with Player.log, never instead of it |

Where a machine's owner restricts walking AppData, ask for the file path instead of searching.

`lgw.py read` auto-detects: `player*` and `editor.log` as Unity, `latest.log` and `crash-*` as Java, `*.jsonl` as events, a folder as a crash folder (`.log`, `.txt`, `.dmp`). Git checkouts reset file times, so the unplayed-build check needs the real files, not a fresh clone.
