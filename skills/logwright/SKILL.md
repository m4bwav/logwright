---
name: logwright
description: "Local-first logs, crash reports and play telemetry for games and tools, turned into findings: read Unity, Minecraft or Roblox logs, dedupe errors by stack, catch an unplayed build, find where players fail or quit, propose bug and balance items; plan events with a paste-ready snippet; count a Claude Code session's tool, skill and subagent calls. Use on 'read this Player.log', 'what went wrong in this play session', 'add analytics or a crash reporter to my game', 'is this telemetry safe for a kids game'. Not for daily spend (ccusage), ranking token cost (tokenwright) or hosted crash triage (Sentry)."
license: MIT
metadata:
  version: 0.1.0
---

# logwright

Outcome: a findings report built from what a game or agent recorded, never from memory, and telemetry that stays on the player's machine unless the owner sets up more.

`LGW` means `python scripts/lgw.py` from the plugin root (run it, do not read it). Every verb prints one JSON object; `ok: false` carries the error.

## Read a play session

1. `LGW query <log or folder> [--build <build file or folder>] [--md findings.md]`. A folder reads every `.log`, `.jsonl` and crash folder in it, so a modded game's Player.log is read next to mods.log. Errors come grouped by stack signature with count and first line; quote the groups, never the flood.
2. Pass `--build` whenever a build is named: a log older than the build means the build was never played. Say so; a clean old log is not a pass.
3. Report: crashes first, then error groups by count, then play signals (fails, deaths, retries, quit point). Rare errors stay in the report.

## Turn findings into work

`LGW query <target> --grind` adds `proposals` (lane, title, value, source). Never write or append to a grind ledger or tracker yourself, even when asked to "turn this into items": show the proposals and hand them to grindwright (`grw.py add`) or the owner. Balance judgement belongs to ludowright.

Onboarding funnel: plan `beat.start`/`beat.complete` per teaching beat (schema has the fixed fields); `query` then adds `beats`, ranked by struggle rate and drop-off.

## Add telemetry to a game

1. Plan the events first: 5 to 12 named events (`level.start`, `level.fail`, `session.end`...), each line `{ts, sid, ev, f}` per [references/schema.md](../../references/schema.md). `LGW schema <file.jsonl>` validates a recording.
2. Give the snippet for the engine from `references/snippets/` (unity, roblox, bedrock, web). The engine plugin (unity-agent, roblox-agent, minewright) or the owner places it, in a worktree and PR.
3. Default: opt-in, written to a local file, no network code. A crash reporter is opt-in too.
4. A game for children (under 13, or "my son's game"): no cloud SDK, no upload, no device or advertising ID, no account; local file only. Name COPPA and say any upload would need verifiable parental consent. Run `LGW privacy <repo> --child`; it fails on any network send or device ID. Details: [references/privacy.md](../../references/privacy.md).
5. Remote endpoints (Sentry, GlitchTip, analytics services) are the owner's call; describe the route, never create an account or DSN.

## Agent session cost

`LGW agent <transcript.jsonl>...` or `LGW agent --days N`. It counts usage once per requestId and always reads `<session>/subagents/*.jsonl` next to a transcript, where much of the cost hides. It reports tool, skill and subagent counts, tool errors and refusals, and the subagent token share.

Do not write your own transcript parser. Daily or monthly spend: `npx ccusage daily`. Ranked token sinks: tokenwright's `tw.py`. Live context size: context-health. OpenTelemetry export to a local file: [references/agent.md](../../references/agent.md).

## Readers

Which file each engine writes and where: [references/readers.md](../../references/readers.md). Neighbours and what they own: [references/neighbours.md](../../references/neighbours.md).

## Maintenance

Evergreen unit at the plugin root (`evergreen.json`, RESEARCH.md, LEARNINGS.md, CHANGELOG.md, TESTS.md). On 'refresh logwright', re-check the volatile claims in `evergreen.json` and `harvest.json` targets, log changes in CHANGELOG, lessons in LEARNINGS.
