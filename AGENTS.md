# AGENTS.md

Rules for any AI agent working in this repository. `CLAUDE.md` imports this file; `.github/copilot-instructions.md` points here.

## What this is

logwright: one hub skill, `skills/logwright/`. `scripts/lgw.py` is the CLI (standard library only), `references/` holds the schema, snippets, readers, privacy method and neighbours (load one when a step needs it), `ai-docs/` the notes, plans, log and handoff (start with `ai-docs/HANDOFF.md`). Map: `CODEMAP.md`.

## Rules

- Python 3.9+, standard library only. UTF-8, LF. Every verb prints one JSON object and never raises; exit 2 is a usage error, 1 a failed check.
- Every change gets a test: `python -m unittest discover -s tests`. Test every documented call form.
- Recorded player data never enters this repository. Personal names, game paths and recordings belong in the private sidecar read through `LOGWRIGHT_HOME`.
- Snippets stay local-first and opt-in, with no network code. A remote endpoint is the owner's decision.
- Evergreen unit at the root: read `evergreen.json` before editing; changes go in CHANGELOG with the reason, lessons in LEARNINGS.
- A release bumps `.claude-plugin/plugin.json`, `plugin.json`, `VERSION` in `lgw.py`, `metadata.version` in SKILL.md and CHANGELOG together.
- Plain short sentences, no em dashes, relative links. No AI attribution anywhere.

## Commands

- Tests: `python -m unittest discover -s tests`
- Doctor: `python scripts/lgw.py doctor`
- Findings: `python scripts/lgw.py query <log or folder> [--build B] [--grind] [--md out.md]`
