#!/usr/bin/env bash
# Runs every wiki example against lgw.py 0.1.0 on fixtures in a scratch folder.
set -u
LGW="python $(cd "$(dirname "$0")/../.." && pwd)/scripts/lgw.py"
W=$(mktemp -d); cd "$W"
mkdir -p session game/src
cat > session/Player.log <<'L'
Initialize engine version: 6000.0.30f1
NullReferenceException: Object reference not set to an instance of an object
  at Enemy.Update () [0x00000] in Enemy.cs:42
NullReferenceException: Object reference not set to an instance of an object
  at Enemy.Update () [0x00000] in Enemy.cs:42
L
cat > session/events.jsonl <<'L'
{"ts":"2026-11-19T10:00:00Z","sid":"a1","ev":"session.start"}
{"ts":"2026-11-19T10:01:00Z","sid":"a1","ev":"level.fail","scene":"Level2","f":{"level":"2","t":41.5}}
{"ts":"2026-11-19T10:02:00Z","sid":"a1","ev":"level.fail","scene":"Level2","f":{"level":"2","t":38.0}}
{"ts":"2026-11-19T10:03:00Z","sid":"a1","ev":"session.end","scene":"Level2"}
L
echo '{"ts":"2026-11-19T10:00:00Z","ev":"level.start"}' > bad.jsonl
echo 'fetch("https://example.com/collect", {method:"POST"});' > game/src/stats.js
echo "== version"; $LGW --version
echo "== schema events"; $LGW schema session/events.jsonl
echo "== schema bad"; $LGW schema bad.jsonl; echo "exit $?"
echo "== query"; $LGW query session --md findings.md; echo "exit $?"
echo "== findings.md"; cat findings.md
echo "== query grind"; $LGW query session --grind
echo "== privacy"; $LGW privacy game; echo "exit $?"
echo "== privacy child"; $LGW privacy game --child; echo "exit $?"
echo "== doctor"; $LGW doctor
