# Learnings

Seeded from the harvest (kept in the private sidecar) on 2026-11-19.

- L-001 `requestid-once`: transcripts split one response over several lines by content block; count usage once per requestId or cost doubles. Source: tokenwright L-001.
- L-002 `subagents-hold-a-third`: subagent transcripts held 33.9% of cost-weighted spend over 30 days; always read `<id>/subagents/`.
- L-003 `dedupe-by-signature`: an error thrown every frame floods the log; group by stack signature with count and first line.
- L-004 `read-player-log-with-mods-log`: a mod loader's log can stay clean while Player.log throws.
- L-005 `unplayed-build`: compare log time with the build time before calling a clean log a pass.
- L-006 `git-resets-mtime`: a fresh checkout gives fixtures new times; tests set them with os.utime.
- L-007 `never-raise-json`: report errors inside the JSON with exit 2 for usage; agents consume that reliably.
- L-008 `coppa-online-only`: COPPA turns on with online collection; a local file is clear, any upload or persistent ID is not.
- L-009 `long-paths`: Windows transcript paths pass 260 characters; open them long-path safe.
- L-010 `bash-heredoc-quote`: one large Bash heredoc batch with quotes failed to parse on Windows Git Bash; write files with the file tool instead.
