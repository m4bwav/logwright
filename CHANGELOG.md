# Changelog

## Unreleased

- `query` reads teaching-beat events (`beat.start`, `beat.complete`) and ranks beats by struggle rate, then drop-off, with a derived `struggled` flag and `--struggle-deaths`/`--struggle-secs`. Schema documents the beat event plan. Reason: onboarding funnels show where new players get stuck, a gap the level-based balance signals did not cover.

## 0.1.0 (2026-11-19)

- First build: hub skill, `lgw.py` (schema, read, query, agent, privacy, doctor), references (schema, four engine snippets, readers, privacy, agent, neighbours), 13 unit tests, eval cases with a bare baseline. Rules enter only where the baseline failed: include subagents, child mode never networks, propose and never write a ledger, reuse neighbours.
