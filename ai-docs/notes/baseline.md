# Step D baseline (bare, 2026-11-19, session 3)

Cases: [evals.json](../../evals/evals.json), fixtures in evals/fixtures. One bare run each, self-graded by the running agent (leniency likely).

| Case | Bare | Ruling |
|---|---|---|
| dedupe | PASS (uniq -c grouping) | drop as prose rule; `lgw.py query` still dedupes (script, not rule) |
| modlog | PASS | drop rule |
| unplayed | PASS, but only by incidental timestamped ls | keep as script check in `query`; re-run bare 3x at step F |
| requestid | PASS, by incidental printing | keep in `agent` verb; re-run bare 3x at step F |
| subagents | FAIL (counted 1, not 41) | rule enters |
| childmode | FAIL (cloud SDK, no COPPA) | rule enters |
| ledger | FAIL (appended to ledger.jsonl) | rule enters |
| neighbours | FAIL lean (writes own parser; ccusage not installed) | rule enters: point to `npx ccusage daily` |

Next: step E build with the four entering rules plus the script checks.
