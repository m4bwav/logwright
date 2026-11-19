# Tests

- Unit: `python -m unittest discover -s tests` (14 tests, fixtures in `evals/fixtures`). With `LOGWRIGHT_HOME` set to the private sidecar, `tests/test_leak.py` fails on any sidecar term in a tracked file; unset, it skips.
- Skill evals: `evals/evals.json` (8 cases). Bare baseline 2026-11-19: 4 of 8 fail without the skill (subagents, childmode, ledger, neighbours); see ai-docs/notes/baseline.md. With skill 2026-11-19: 8 of 8 pass (one run, self-graded by a subagent, fixtures untouched). 
- T-003 2026-11-19 trigger proxy (subagent routing judge, a proxy for the main loop since logwright is not installed yet): 8 prompts x3. Should-fire 4/5 prompts 3/3; tool-cost prompts split 2/3 with tokenwright, so the description now says logwright counts calls and tokenwright ranks token cost. Decoys (context size, repo traffic, Sentry setup) 9/9 correct.
- T-004 2026-11-19 bare reruns of unplayed and requestid: 6/6 pass bare (one context, biased toward passing). Those two cases stay as regression checks but carry no rule weight; the gain rests on subagents, childmode, ledger, neighbours.
- evergreen-worth lite 2026-11-19: listing ~149 tokens, body ~837 per use, case lint clean (value cases re-kinded to outcome, childmode got Edit and Bash). Ruling: KEEP on recorded A/B (8/8 with vs 4/8 bare, two of the bare passes are fragile); heavy A/B not run.
- tokenwright-skills 2026-11-19: only saving was the 830-char description, cut to ~610.
