# logwright prior art and overlap survey

Checked 2026-11-19. Rows marked (unverified) come from memory, not from a source read today.

## Sources

| Topic | Source | What it says |
|---|---|---|
| Claude Code OTel | https://code.claude.com/docs/en/monitoring-usage | Off until `CLAUDE_CODE_ENABLE_TELEMETRY=1`; `OTEL_METRICS_EXPORTER` / `OTEL_LOGS_EXPORTER` (console, otlp, prometheus, none); metrics for sessions, tokens, cost; events for prompts, tool calls, API errors; traces beta behind `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` + `OTEL_TRACES_EXPORTER`; can be pushed by managed settings |
| OTel caveat | https://betterstack.com/docs/logs/claude-code/ | OTEL_* vars are not passed to child processes (Bash tool, hooks, MCP servers) |
| OTel stack | https://github.com/ColeMurray/claude-code-otel | Collector -> Prometheus (metrics) + Loki (events) + Grafana. Needs Docker; not local-first JSONL |
| OTel walkthrough | https://www.freecodecamp.org/news/claude-code-observability-with-opentelemetry | Tutorial for the same setup |
| ccusage | https://github.com/ryoppippi/ccusage , https://www.npmjs.com/package/ccusage | Reads local `~/.claude/projects/**/*.jsonl`; daily/monthly/session/blocks --live reports, per-model cost. Leaves out server tools (web search etc.); no per-tool cost |
| ccusage skill | https://skills.sh/jeasonstudio/ccusage-skill/ccusage | A skill wrapper around ccusage already exists |
| cc-token-usage | https://docs.rs/crate/cc-token-usage | Rust CLI, cost per project and session |
| Sentry MCP | https://github.com/getsentry/sentry-mcp , https://docs.sentry.io/product/sentry-mcp | Official; ships a Claude Code plugin (marketplace getsentry/sentry-mcp, subagent sentry-mcp); remote `https://mcp.sentry.dev/mcp` with OAuth; self-hosted host flag |
| GlitchTip | https://github.com/rh-cssre/glitchtip-backend , https://railway.com/deploy/glitchtip-sentry-alternative | Sentry-SDK compatible, switch by DSN; ~30 GB per 1M events/month at 90-day retention; no session replay; no artifact-bundle/debug-ID upload |
| GlitchTip skill | https://skills.sh/lu1sdv/skillsmd/glitchtip | A GlitchTip skill exists |
| Unity logs | https://docs.unity3d.com/Manual/LogFiles.html | Windows player log `%USERPROFILE%\AppData\LocalLow\<Company>\<Product>\Player.log` (Player-prev.log kept); `Application.consoleLogPath`; crash folder via `CrashReporting.crashReportFolder`, `-crash-report-folder`; `-logFile` overrides |
| Unity services | (unverified) | Unity Cloud Diagnostics crash/exception reporting and Unity Analytics (UGS) are cloud, need a Unity project ID; Unity Analytics needs consent flow for GDPR/COPPA |
| Roblox analytics | https://create.roblox.com/docs/reference/engine/classes/AnalyticsService | `LogCustomEvent`, `LogProgressionEvent` (`Enum.AnalyticsProgressionType`), economy/funnel events; data only in Creator Hub dashboards, no raw export |
| Roblox logs | (unverified) https://create.roblox.com/docs/reference/engine/classes/LogService | `LogService.MessageOut` and `GetLogHistory` let server code capture output; Open Cloud Luau Execution returns task logs (roblox-agent-cloud uses this) |
| Minecraft | (unverified) | Java mods: SLF4J/log4j2 to `logs/latest.log` and `crash-reports/`. Bedrock add-ons (minewright's scope): Script API `console.log`/`console.warn` go to the content log and BDS stdout |
| COPPA 2025 | https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule , https://www.loeb.com/en/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule | Amended rule published 2025-04-22 (effective and compliance dates unverified: likely 2025-06-23 and 2026-04-22); persistent ID for internal operations needs no parental consent but needs a specific notice; separate consent to share with third parties |
| COPPA and games | https://gamesbeat.com/understanding-the-updated-coppa-rules-and-their-impact-on-child-safety/ | Third-party analytics SDKs are the hard part; child-appealing games are covered even with mostly adult players |
| Steam | https://store.steampowered.com/privacy_agreement/ | Valve's own policy; no developer-SDK rule found. (unverified) Steamworks asks for a privacy policy link if the game collects personal data |
| GDPR | (unverified) | Device/player IDs are personal data; analytics needs a lawful basis, consent is safest; crash reports with no ID and local-only storage are lowest risk |
| Name clash | web search "logwright" github/npm/pypi | No project named logwright found; nearest: log-right (npm, stale), logwrangler, logwell, logly |

## Neighbours (one line each, from their SKILL.md descriptions)

| Plugin | Owns |
|---|---|
| tokenwright | Spending fewer tokens: habits, tw.py diff and session token-sink ranking; -catalog for skill-catalog cost |
| context-health | Context size vs model degradation in the current session; startup context; hooks |
| repo-traffic | GitHub traffic and package download stats with a local dashboard |
| chartwright | Rendering charts from data in the target medium (about 80 types) |
| grindwright | Picking the next most valuable work across lanes of a game/film project; ledger and selector |
| ludowright | Game design: pitches, ranked improvements, design flaw reviews (balance in theory) |
| unity-agent | Driving Unity from the terminal: CLI, headless batchmode/tests with log proof, MCP, packages, workflow |
| roblox-agent | Roblox on disk (Rojo), checks, Open Cloud Luau execution and logs, Studio MCP |
| minewright | Minecraft Bedrock add-ons: project, checks, HUD, BDS live test server, workflow |
| sitewright | Personal website redesign: direction, DESIGN.md, build, audit |

## Overlap table

| logwright idea | Already covered by | Verdict |
|---|---|---|
| Daily/monthly token cost from transcripts | ccusage, cc-token-usage | Do not rebuild; call or point to ccusage |
| Session token sinks | tokenwright tw.py | Do not rebuild; link to it |
| Context size now | context-health | Out of scope |
| Claude Code OTel to Grafana | claude-code-otel, Better Stack | Do not rebuild the stack |
| Per-tool and per-skill cost, failed/refused calls, cost per plugin across sessions | none found (ccusage is per day/session/model) | Left for logwright lane 2, small |
| OTel console/file export into local JSONL with no Docker | none found | Left for logwright lane 2 |
| Crash triage in Sentry | Sentry MCP plugin, GlitchTip skill | Do not rebuild; recommend GlitchTip DSN for self-host |
| Unity Player.log reading in tests | unity-agent-headless (Editor/batch logs) | Share; logwright reads shipped player logs and crash folders |
| Roblox server log capture | roblox-agent-cloud (task logs) | Share; logwright adds an in-game event schema and LogService sink |
| Bedrock content log | minewright-server (BDS stdout) | Share; logwright parses it into events |
| Balance judgement | ludowright | logwright produces numbers; ludowright judges |
| What to work on next | grindwright | logwright findings feed its bug/balance lanes |
| Charts of findings | chartwright | Hand off rendering |

## What is left for logwright

1. One small event schema (JSONL line: ts, session, build, scene, event, fields) shared by Unity C#, Luau, Bedrock JS and web JS snippets, written to local files or SQLite, no cloud.
2. A query script that turns one play session into findings: crashes and exceptions grouped by stack, deaths/fails per level, stuck time, economy flows, outliers; output as a markdown report grindwright and ludowright can read.
3. Log readers for the places engines already write: Unity Player.log and crash folder, Bedrock content log / BDS stdout, Java `latest.log`/`crash-reports`, Roblox LogService history.
4. A privacy default: opt-in, no personal data, random per-install ID, local only; a child-player mode with no network send at all; a short checklist for GDPR, COPPA notice and the Steam privacy-policy link before any upload is added.
5. Lane 2, thin: per-tool, per-skill and per-subagent cost and error counts from transcripts, plus an OTel file/console capture recipe; defer daily totals to ccusage.

## Name-clash verdict

Clear. No GitHub repo, npm or PyPI package named logwright turned up on 2026-11-19 (search engine only; confirm with `npm view logwright` and pypi.org/project/logwright before the first release). Nearest names (log-right, logwell, logwrangler) differ enough.
