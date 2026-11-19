# logwright design (step C, 2026-11-19)

Inputs: harvest (private sidecar, `$LOGWRIGHT_HOME/notes/harvest.md`), [prior art](../notes/prior-art.md). Name kept: no clash found (confirm `npm view logwright` and pypi before release).

## What it holds

1. **Event schema** (one JSONL line per event): `ts, sid (random per session), iid (random per install, optional), build, scene, ev, f{...}`. No names, emails, IPs or free text typed by a player unless the game says so (a child's study game keeps typed answers local).
2. **Snippets** that write that schema to a local file, one per engine, short enough to paste: Unity C#, Roblox Luau (LogService + DataStore-free, server only), Bedrock Script API JS, browser JS (download or localStorage). The engine plugin places them; logwright never edits a game outside a worktree and PR.
3. **Readers** for logs engines already write: Unity Player.log / Player-prev.log and the crash folder, Bedrock content log and BDS stdout, Java `latest.log` and `crash-reports/`, Roblox `GetLogHistory` dumps. They emit the same events (`ev: "log.error"`, `"crash"`).
4. **query**: one session (or a folder of them) to findings markdown + JSON: crashes and exceptions deduped by stack signature (count, first seen), fails/deaths per level, stuck time, economy in/out, quit point, "unplayed build" warning (log older than deploy). Findings are phrased as grindwright `add` proposals (lane bug or balance, source = log path); logwright never writes a ledger.
5. **Agent lane, thin**: `agent` verb reads Claude Code transcripts (and subagents/) and reports per-tool, per-skill and per-subagent counts, errors, refusals and token share, counting usage once per requestId. Daily totals point to ccusage; sinks point to tokenwright; live context to context-health. Plus a recipe for OTel console/file export to JSONL with no Docker.
6. **Privacy method**: opt-in default, local-only storage, child mode that has no network code path, and a checklist (GDPR lawful basis, COPPA notice for persistent IDs, Steam privacy-policy link) that must pass before any upload is added. Remote endpoints are out of scope for the agent; a GlitchTip DSN is the documented self-host route, set up only by Mark.

## What stays with neighbours

tokenwright (sinks), context-health (live window), ccusage (daily cost), evergreen wrapup (session harvest), Sentry MCP / GlitchTip skill (hosted crash triage), unity-agent / roblox-agent / minewright (placing code, editor logs, BDS), ludowright (judging balance), grindwright (ledger), chartwright (charts from query JSON).

## Shape

One hub skill `logwright` plus references loaded on demand (`schema.md`, `snippets/<engine>.md`, `readers.md`, `privacy.md`, `agent.md`). Siblings are not justified yet: one skill until worth or a trigger clash proves a split. Script `scripts/lgw.py`, stdlib, one JSON object per command, never raises (errors inside the JSON, exit 2 for usage):

| Verb | Does |
|---|---|
| `schema` | print or validate a JSONL file against the schema |
| `read <log>` | engine log or crash folder to events (auto-detects kind) |
| `query <session or dir>` | findings JSON + markdown; `--grind` prints proposed `grw.py add` lines |
| `agent [--days N]` | per-tool/skill/subagent cost and errors from transcripts |
| `privacy <repo>` | scan a repo for network sends, IDs and missing notice; fails on a child-mode game with any send |

## Sidecar

Private overlay in the everlast vault read through `LOGWRIGHT_HOME`: Mark's game list and paths, which engine each uses, recorded sessions and findings reports. Leak test: with `LOGWRIGHT_HOME` set, fail on any sidecar term found in a tracked public file.

## Proof for each rule (step D cases)

| Rule | Case that must fail bare |
|---|---|
| dedupe by stack signature | a Player.log with one error thrown 4,000 times: bare answer quotes the flood |
| read Player.log and mods.log both | clean mods.log, throwing Player.log |
| unplayed build check | log older than the build: bare calls it a pass |
| usage once per requestId | transcript with split content blocks: bare doubles cost |
| include subagents/ | session whose cost is mostly in subagents |
| child mode never networks | "add analytics to my kid's game": bare suggests a cloud SDK |
| propose, don't write the ledger | "turn this log into grind items": bare edits ledger.jsonl |
| reuse neighbours | "what did I spend today": bare writes a parser instead of ccusage |
| Mark's setup facts | sidecar paths (fact, no case needed) |

Size budget: SKILL.md under 120 lines, lgw.py under ~800 lines, snippets under 60 lines each.
