# CODEMAP

- `skills/logwright/SKILL.md`: the hub skill.
- `scripts/lgw.py`: CLI. Verbs `schema`, `read`, `query`, `agent`, `privacy`, `doctor`. Readers turn engine logs into events (`read_log`, `read_any`); `cmd_query` groups errors by `signature()` and checks build age; `cmd_agent` counts usage once per requestId and walks `subagents/`.
- `references/`: schema, `snippets/<engine>.md`, readers, privacy, agent, neighbours.
- `tests/test_lgw.py`: unit tests over `evals/fixtures`.
- `evals/evals.json`: skill eval cases with baseline (fixtures in `evals/fixtures`).
- `ai-docs/`: harvest, prior art, design, baseline, handoff, log.
