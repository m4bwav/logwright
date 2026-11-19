#!/usr/bin/env python3
"""logwright CLI: local-first game and agent telemetry into findings.

Standard library only. Every verb prints one JSON object. Errors go inside
the JSON ("ok": false); exit 2 means a usage error, 1 a failed check.
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import re
import sys

VERSION = "0.1.0"
SCHEMA_KEYS = {"ts": str, "sid": str, "ev": str}
OPTIONAL_KEYS = {"iid": str, "build": str, "scene": str, "f": dict}
PII_KEYS = {"name", "email", "ip", "username", "address", "phone", "real_name"}


def out(obj, code=0):
    sys.stdout.write(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    return code


def lp(path):
    """Long-path-safe path on Windows (transcripts pass 260 chars)."""
    p = os.path.abspath(path)
    if os.name == "nt" and not p.startswith("\\\\?\\") and len(p) > 240:
        return "\\\\?\\" + p
    return p


def read_text(path):
    with open(lp(path), "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def iter_jsonl(path):
    with open(lp(path), "r", encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except ValueError:
                yield n, None


# ---------- schema ----------

def check_event(ev):
    probs = []
    if not isinstance(ev, dict):
        return ["not a JSON object"]
    for k, t in SCHEMA_KEYS.items():
        if not isinstance(ev.get(k), t):
            probs.append("missing or bad '%s'" % k)
    for k, t in OPTIONAL_KEYS.items():
        if k in ev and not isinstance(ev[k], t):
            probs.append("bad type for '%s'" % k)
    f = ev.get("f") if isinstance(ev.get("f"), dict) else {}
    for k in list(ev) + list(f):
        if k.lower() in PII_KEYS:
            probs.append("personal field '%s'" % k)
    return probs


def cmd_schema(a):
    spec = {"required": {k: "string" for k in SCHEMA_KEYS},
            "optional": {"iid": "string, random per install", "build": "string",
                         "scene": "string", "f": "object of event fields"},
            "forbidden_fields": sorted(PII_KEYS),
            "example": {"ts": "2026-11-19T10:00:00Z", "sid": "a1b2c3", "build": "0.4.2",
                        "scene": "Level2", "ev": "level.fail", "f": {"level": "2", "t": 41.5}}}
    if not a.file:
        return out({"ok": True, "schema": spec})
    bad, count = [], 0
    for n, ev in iter_jsonl(a.file):
        count += 1
        p = check_event(ev) if ev is not None else ["invalid JSON"]
        if p:
            bad.append({"line": n, "problems": p})
    return out({"ok": not bad, "events": count, "bad": bad[:50], "bad_count": len(bad)},
               0 if not bad else 1)


# ---------- readers ----------

EXC_RE = re.compile(r"^([A-Za-z_][\w.]*(?:Exception|Error)\b.*)$")
UNITY_AT = re.compile(r"^\s*(?:at |\S+:\S+\s*\().*")
JAVA_CRASH = re.compile(r"^---- Minecraft Crash Report ----")
LOGLEVEL = re.compile(r"\b(ERROR|FATAL|SEVERE|Exception)\b")


def detect_kind(path):
    base = os.path.basename(path).lower()
    if os.path.isdir(path):
        return "crashdir"
    if base.startswith("player") or base == "editor.log":
        return "unity"
    if base in ("latest.log", "debug.log") or base.startswith("crash-"):
        return "java"
    if base.endswith(".jsonl"):
        return "events"
    if "content_log" in base or "bedrock" in base:
        return "bedrock"
    return "text"


def signature(head, frames):
    norm = re.sub(r"\[0x[0-9a-f]+\]|0x[0-9a-f]+|\d+(?=\))", "", head + "|" + "|".join(frames[:3]))
    return hashlib.sha1(norm.encode()).hexdigest()[:10]


def read_log(path):
    """Engine log to events. Multi-line exceptions become one event with frames."""
    lines = read_text(path).splitlines()
    events, i = [], 0
    while i < len(lines):
        line = lines[i]
        m = EXC_RE.match(line.strip())
        if m or JAVA_CRASH.match(line):
            frames, j = [], i + 1
            while j < len(lines) and (UNITY_AT.match(lines[j]) or lines[j].startswith("\t")):
                frames.append(lines[j].strip())
                j += 1
            head = line.strip()
            kind = "crash" if JAVA_CRASH.match(line) else "log.error"
            loc = next((re.search(r"in (\S+:\d+)", fr) or re.search(r"\((\S+:\d+)\)", fr)
                        for fr in frames if re.search(r":\d+", fr)), None)
            events.append({"ev": kind, "line": i + 1, "msg": head[:300],
                           "where": loc.group(1) if loc else None,
                           "frames": frames[:8], "sig": signature(head, frames)})
            i = max(j, i + 1)
            continue
        if LOGLEVEL.search(line) and not line.strip().startswith("at "):
            events.append({"ev": "log.error", "line": i + 1, "msg": line.strip()[:300],
                           "where": None, "frames": [], "sig": signature(line.strip(), [])})
        i += 1
    return events


def read_any(path):
    kind = detect_kind(path)
    if kind == "crashdir":
        evs = []
        for root, _, files in os.walk(path):
            for fn in files:
                if fn.lower().endswith((".log", ".txt")):
                    for e in read_log(os.path.join(root, fn)):
                        e["file"] = os.path.join(root, fn)
                        evs.append(e)
                elif fn.lower().endswith(".dmp"):
                    evs.append({"ev": "crash", "msg": "minidump " + fn, "file": os.path.join(root, fn),
                                "sig": signature(fn, []), "frames": [], "where": None})
        return kind, evs
    if kind == "events":
        evs = []
        for n, e in iter_jsonl(path):
            if isinstance(e, dict):
                e.setdefault("line", n)
                evs.append(e)
        return kind, evs
    evs = read_log(path)
    for e in evs:
        e["file"] = path
    return kind, evs


def cmd_read(a):
    if not os.path.exists(a.path):
        return out({"ok": False, "error": "not found: " + a.path}, 1)
    kind, evs = read_any(a.path)
    return out({"ok": True, "kind": kind, "count": len(evs), "events": evs[: a.limit]})


# ---------- query ----------

def mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def newest_build(build):
    if not build or not os.path.exists(build):
        return None, None
    if os.path.isfile(build):
        return build, mtime(build)
    best = (None, 0)
    for root, _, files in os.walk(build):
        for fn in files:
            t = mtime(os.path.join(root, fn)) or 0
            if t > best[1]:
                best = (os.path.join(root, fn), t)
    return best


def gather(target):
    paths = []
    if os.path.isdir(target):
        for fn in sorted(os.listdir(target)):
            p = os.path.join(target, fn)
            if os.path.isfile(p) and fn.lower().endswith((".log", ".jsonl", ".txt")):
                paths.append(p)
            elif os.path.isdir(p) and fn.lower() in ("crashes", "crash-reports"):
                paths.append(p)
    else:
        paths.append(target)
    return paths


def iso(t):
    return dt.datetime.fromtimestamp(t).isoformat(timespec="seconds") if t else None


def cmd_query(a):
    if not os.path.exists(a.target):
        return out({"ok": False, "error": "not found: " + a.target}, 1)
    files = gather(a.target)
    groups = collections.OrderedDict()
    play = collections.Counter()
    last_scene, quit_at, per_file = None, None, {}
    by_level = collections.Counter()
    sids, finished = set(), set()
    for p in files:
        kind, evs = read_any(p)
        per_file[p] = {"kind": kind, "events": len(evs)}
        for e in evs:
            name = e.get("ev", "")
            if name in ("log.error", "crash"):
                g = groups.setdefault(e["sig"], {"sig": e["sig"], "ev": name, "msg": e["msg"],
                                                 "where": e.get("where"), "count": 0,
                                                 "first": "%s:%s" % (os.path.basename(p), e.get("line"))})
                g["count"] += 1
            else:
                play[name] += 1
                f = e.get("f") or {}
                if e.get("scene"):
                    last_scene = e["scene"]
                if e.get("sid"):
                    sids.add(e["sid"])
                if re.search(r"fail|death|die|retry|stuck", name):
                    by_level[(name, str(f.get("level") or e.get("scene") or "?"))] += 1
                if name in ("session.end", "quit"):
                    if f.get("finished"):
                        finished.add(e.get("sid"))
                    else:
                        quit_at = e.get("scene") or f.get("level")
    findings = sorted(groups.values(), key=lambda g: (g["ev"] != "crash", -g["count"]))
    warnings = []
    log_t = max([mtime(p) or 0 for p in files] or [0])
    bpath, bt = newest_build(a.build)
    if a.build and bt and log_t and log_t < bt:
        warnings.append("unplayed build: newest log %s is older than build file %s (%s); a clean log "
                        "does not prove this build" % (iso(log_t), os.path.basename(bpath), iso(bt)))
    if not findings and not play:
        warnings.append("no events found; check the log path and that the session ran")
    balance = [{"ev": k, "count": v} for k, v in play.most_common() if re.search(r"fail|death|die|retry|stuck", k)]
    res = {"ok": True, "files": per_file, "errors_distinct": len(findings),
           "errors_total": sum(g["count"] for g in findings), "errors": findings[: a.limit],
           "play": dict(play.most_common(30)), "balance_signals": balance,
           "balance_by_level": [{"ev": k[0], "level": k[1], "count": v} for k, v in by_level.most_common(a.limit)],
           "sessions": {"total": len(sids), "finished": len(finished)},
           "quit_point": quit_at or (last_scene if play and len(finished) < len(sids) else None),
           "warnings": warnings}
    if a.grind:
        res["proposals"] = [
            {"lane": "bug", "title": "%s at %s (x%d)" % (g["msg"].split(":")[0][:60], g["where"] or "?", g["count"]),
             "value": 5 if g["ev"] == "crash" or g["count"] > 100 else 3,
             "source": "%s %s" % (a.target, g["first"])} for g in findings]
        res["proposals"] += [{"lane": "balance", "title": "%s at %s happened %d times" % (b["ev"], b["level"], b["count"]),
                              "value": 3, "source": a.target} for b in res["balance_by_level"] if b["count"] > 1]
        res["note"] = ("proposals only: hand them to grindwright (grw.py add) or the owner; "
                       "logwright never writes a ledger")
    if a.md:
        md = ["# Findings: %s" % a.target, ""]
        for w in warnings:
            md.append("- WARNING: " + w)
        md.append("\n## Errors (deduped by stack signature)\n")
        md.append("| count | kind | message | where | first |\n|---|---|---|---|---|")
        for g in findings:
            md.append("| %d | %s | %s | %s | %s |" % (g["count"], g["ev"], g["msg"][:80].replace("|", "/"),
                                                     g["where"] or "", g["first"]))
        if play:
            md.append("\n## Play\n")
            md += ["- %s: %d" % kv for kv in play.most_common(30)]
            md.append("\n## Sessions\n\n- total %d, finished %d, quit point: %s" % (
                len(sids), len(finished), res["quit_point"] or "none (every session finished)"))
        if by_level:
            md.append("\n## Balance by level\n\n| count | event | level |\n|---|---|---|")
            md += ["| %d | %s | %s |" % (v, k[0], k[1].replace("|", "/")) for k, v in by_level.most_common(a.limit)]
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(md) + "\n")
        res["markdown"] = a.md
    return out(res)


# ---------- agent ----------

def transcript_files(path):
    """Main transcript plus every <id>/subagents/*.jsonl next to it."""
    files = [("main", path)]
    sub = os.path.join(os.path.splitext(path)[0], "subagents")
    if os.path.isdir(sub):
        for fn in sorted(os.listdir(sub)):
            if fn.endswith(".jsonl"):
                files.append(("subagent:" + fn[:-6], os.path.join(sub, fn)))
    return files


def scan_transcript(path, who, acc):
    seen = set()
    for _, row in iter_jsonl(path):
        if not isinstance(row, dict):
            continue
        msg = row.get("message") or {}
        if row.get("type") == "assistant" and isinstance(msg, dict):
            key = row.get("requestId") or msg.get("id") or id(row)
            u = msg.get("usage") or {}
            if key not in seen and u:
                seen.add(key)
                for k in ("input_tokens", "output_tokens", "cache_read_input_tokens",
                          "cache_creation_input_tokens"):
                    acc["tokens"][k] += int(u.get(k) or 0)
                    acc["by_who"][who][k] += int(u.get(k) or 0)
                acc["requests"] += 1
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    name = c.get("name", "?")
                    inp = c.get("input") or {}
                    if name == "Skill":
                        acc["skills"][inp.get("skill", "?")] += 1
                    if name in ("Agent", "Task"):
                        acc["subagent_calls"] += 1
                    acc["tools"][name] += 1
                    acc["by_who"][who]["tool_calls"] += 1
        if row.get("type") == "user" and isinstance(msg, dict):
            for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                    txt = json.dumps(c.get("content"))[:200]
                    kind = "refused" if re.search(r"denied|refus|not allowed|permission", txt, re.I) else "error"
                    acc["errors"][kind] += 1


def find_sessions(days, root):
    cutoff = dt.datetime.now().timestamp() - days * 86400
    found = []
    for proj in os.listdir(root) if os.path.isdir(root) else []:
        d = os.path.join(root, proj)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            p = os.path.join(d, fn)
            if fn.endswith(".jsonl") and (mtime(p) or 0) >= cutoff:
                found.append(p)
    return found


def cmd_agent(a):
    paths = a.transcripts or find_sessions(a.days, os.path.expanduser(a.root))
    if not paths:
        return out({"ok": False, "error": "no transcripts found"}, 1)
    acc = {"tokens": collections.Counter(), "tools": collections.Counter(), "skills": collections.Counter(),
           "errors": collections.Counter(), "requests": 0, "subagent_calls": 0,
           "by_who": collections.defaultdict(collections.Counter)}
    nfiles = 0
    for p in paths:
        for who, f in transcript_files(p):
            scan_transcript(f, "main" if who == "main" else "subagents", acc)
            nfiles += 1
    tot = sum(acc["tokens"].values()) or 1
    sub_share = sum(acc["by_who"]["subagents"][k] for k in acc["tokens"]) / tot
    return out({"ok": True, "sessions": len(paths), "files_read": nfiles, "requests": acc["requests"],
                "tokens": dict(acc["tokens"]), "tool_calls": sum(acc["tools"].values()),
                "tools": dict(acc["tools"].most_common(25)), "skills": dict(acc["skills"]),
                "subagent_calls": acc["subagent_calls"], "subagent_token_share": round(sub_share, 3),
                "by_who": {k: dict(v) for k, v in acc["by_who"].items()},
                "errors": dict(acc["errors"]),
                "note": "usage counted once per requestId; subagents/ included. Daily cost: npx ccusage daily. "
                        "Token sinks: tokenwright tw.py. Live context: context-health."})


# ---------- privacy ----------

NET = re.compile(r"UnityWebRequest|HttpClient|WebClient|fetch\(|XMLHttpRequest|navigator\.sendBeacon|"
                 r"HttpService|requests\.(?:get|post)|urllib\.request|sentry|firebase|gameanalytics|"
                 r"Analytics\.(?:CustomEvent|SendEvent)|AnalyticsService", re.I)
IDS = re.compile(r"SystemInfo\.deviceUniqueIdentifier|deviceId|advertisingId|GetMacAddress|localStorage\.setItem\(['\"]uid", re.I)
CODE_EXT = (".cs", ".js", ".ts", ".lua", ".luau", ".py", ".gd", ".java", ".html")


def cmd_privacy(a):
    hits = []
    for root, dirs, files in os.walk(a.repo):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "Library", "Temp", "obj", "bin")]
        for fn in files:
            if not fn.lower().endswith(CODE_EXT):
                continue
            p = os.path.join(root, fn)
            try:
                for n, line in enumerate(read_text(p).splitlines(), 1):
                    for kind, rx in (("network", NET), ("device_id", IDS)):
                        if rx.search(line):
                            hits.append({"kind": kind, "file": os.path.relpath(p, a.repo), "line": n,
                                         "text": line.strip()[:160]})
            except OSError:
                continue
    has_notice = any(os.path.exists(os.path.join(a.repo, n)) for n in ("PRIVACY.md", "privacy.md", "PRIVACY.txt"))
    fail = a.child and any(h["kind"] in ("network", "device_id") for h in hits)
    checks = ["opt-in before any recording leaves the device", "local-only storage by default",
              "no persistent IDs without a COPPA notice (players under 13)",
              "GDPR lawful basis named before any upload", "Steam store privacy-policy link if uploading"]
    return out({"ok": not fail, "child_mode": a.child, "hits": hits[:200], "privacy_notice": has_notice,
                "checklist": checks,
                "verdict": "FAIL: child mode game has a network send or device ID" if fail else
                ("review hits against the checklist" if hits else "no network sends or device IDs found")},
               1 if fail else 0)


def cmd_doctor(a):
    root = os.path.expanduser("~/.claude/projects")
    return out({"ok": True, "version": VERSION, "python": sys.version.split()[0],
                "transcripts_root": root, "transcripts_root_exists": os.path.isdir(root),
                "home": os.environ.get("LOGWRIGHT_HOME")})


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lgw.py", description=__doc__)
    ap.add_argument("--version", action="version", version=VERSION)
    sp = ap.add_subparsers(dest="cmd")
    s = sp.add_parser("schema", help="print the event schema or validate a JSONL file")
    s.add_argument("file", nargs="?")
    s = sp.add_parser("read", help="engine log or crash folder to events")
    s.add_argument("path")
    s.add_argument("--limit", type=int, default=200)
    s = sp.add_parser("query", help="session log(s) to findings")
    s.add_argument("target")
    s.add_argument("--build", help="build file or folder; warns when the log is older (unplayed build)")
    s.add_argument("--grind", action="store_true", help="add proposed grind items (never written)")
    s.add_argument("--md", help="also write findings markdown here")
    s.add_argument("--limit", type=int, default=50)
    s = sp.add_parser("agent", help="tool, skill and subagent cost from Claude Code transcripts")
    s.add_argument("transcripts", nargs="*")
    s.add_argument("--days", type=float, default=1)
    s.add_argument("--root", default="~/.claude/projects")
    s = sp.add_parser("privacy", help="scan a game repo for network sends and device IDs")
    s.add_argument("repo")
    s.add_argument("--child", action="store_true", help="fail on any send: game for children")
    sp.add_parser("doctor")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    fn = {"schema": cmd_schema, "read": cmd_read, "query": cmd_query, "agent": cmd_agent,
          "privacy": cmd_privacy, "doctor": cmd_doctor}.get(a.cmd)
    if not fn:
        ap.print_help()
        return 2
    try:
        return fn(a)
    except Exception as e:  # never raise: report inside the JSON
        return out({"ok": False, "error": "%s: %s" % (type(e).__name__, e)}, 1)


if __name__ == "__main__":
    sys.exit(main())
