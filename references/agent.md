# Agent session telemetry

`lgw.py agent` reads Claude Code transcripts under `~/.claude/projects/<slug>/<session>.jsonl` and `<session>/subagents/*.jsonl`.

- One API response is split over several lines, one per content block, each carrying the same `usage`. Count it once per `requestId` (fall back to `message.id`).
- Subagent transcripts often hold a third or more of the cost. Always include them.
- Token counts from text length are estimates; use them to rank, not to bill.
- Split interactive sessions from headless `claude -p` eval runs by cwd before drawing conclusions.
- Windows transcript paths can pass 260 characters; the script opens them long-path safe.

## OpenTelemetry to a local file (no Docker)

Claude Code exports metrics and events when `CLAUDE_CODE_ENABLE_TELEMETRY=1` and an exporter is set. `OTEL_METRICS_EXPORTER=console` and `OTEL_LOGS_EXPORTER=console` print to the console; redirect a headless run's output to a file to keep them. A collector writing JSONL needs the OpenTelemetry Collector's file exporter. Setting these variables in a settings file is a setting outside a repository: the owner switches it on.

Neighbours: `npx ccusage daily` for spend per day, tokenwright `tw.py` for sinks, context-health for live context.
