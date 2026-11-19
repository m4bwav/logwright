import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lgw  # noqa: E402

FIX = os.path.join(ROOT, "evals", "fixtures")


def run(*args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = lgw.main(list(args))
    return code, json.loads(buf.getvalue()) if buf.getvalue().strip().startswith("{") else None


class TestBeats(unittest.TestCase):
    F = os.path.join(FIX, "beats", "session.jsonl")

    def test_ranked_by_struggle_then_drop(self):
        code, d = run("query", self.F)
        self.assertEqual(code, 0)
        b = d["beats"]
        self.assertEqual([r["beat"] for r in b], ["wall-climb", "jump"])
        self.assertEqual((b[0]["struggled"], b[0]["dropped"], b[0]["drop_rate"]), (1, 1, 0.5))
        self.assertEqual(b[1]["struggled"], 1)  # the game's own flag wins over derived

    def test_thresholds_change_struggle(self):
        code, d = run("query", self.F, "--struggle-deaths", "1", "--struggle-secs", "999")
        jump = [r for r in d["beats"] if r["beat"] == "jump"][0]
        self.assertEqual(jump["struggled"], 2)

    def test_grind_and_md(self):
        tmp = tempfile.mkdtemp()
        try:
            md = os.path.join(tmp, "f.md")
            code, d = run("query", self.F, "--grind", "--md", md)
            self.assertTrue(any("teaching beat wall-climb" in p["title"] for p in d["proposals"]))
            with open(md, encoding="utf-8") as fh:
                self.assertIn("## Teaching beats", fh.read())
        finally:
            shutil.rmtree(tmp)

    def test_no_beats_key_without_beat_events(self):
        code, d = run("query", os.path.join(FIX, "flood", "Player.log"))
        self.assertNotIn("beats", d)


class TestQuery(unittest.TestCase):
    def test_dedupe_by_signature(self):
        code, d = run("query", os.path.join(FIX, "flood", "Player.log"))
        self.assertEqual(code, 0)
        self.assertEqual(d["errors_distinct"], 2)
        counts = sorted(g["count"] for g in d["errors"])
        self.assertEqual(counts, [1, 4000])

    def test_modded_folder_reads_player_log(self):
        code, d = run("query", os.path.join(FIX, "modded"))
        self.assertTrue(any("MissingMethodException" in g["msg"] for g in d["errors"]))

    def test_unplayed_build(self):
        # git checkout resets mtimes, so set them here
        tmp = tempfile.mkdtemp()
        try:
            log = os.path.join(tmp, "Player.log")
            shutil.copy(os.path.join(FIX, "stale", "Player.log"), log)
            os.mkdir(os.path.join(tmp, "Build"))
            exe = os.path.join(tmp, "Build", "Game.exe")
            open(exe, "w").close()
            os.utime(log, (1_000_000_000, 1_000_000_000))
            code, d = run("query", log, "--build", os.path.join(tmp, "Build"))
            self.assertTrue(any("unplayed build" in w for w in d["warnings"]))
        finally:
            shutil.rmtree(tmp)

    def test_grind_proposals_do_not_touch_ledger(self):
        ledger = os.path.join(FIX, "grind", "ledger.jsonl")
        before = open(ledger, "rb").read()
        code, d = run("query", os.path.join(FIX, "flood", "Player.log"), "--grind")
        self.assertEqual(len([p for p in d["proposals"] if p["lane"] == "bug"]), 2)
        self.assertEqual(open(ledger, "rb").read(), before)

    def test_md_output(self):
        tmp = tempfile.mkdtemp()
        try:
            md = os.path.join(tmp, "f.md")
            run("query", os.path.join(FIX, "flood", "Player.log"), "--md", md)
            self.assertIn("4000", open(md, encoding="utf-8").read())
        finally:
            shutil.rmtree(tmp)

    def test_play_events(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "s.jsonl")
            with open(p, "w") as fh:
                for i in range(3):
                    fh.write(json.dumps({"ts": "t", "sid": "a", "ev": "level.fail", "scene": "L2"}) + "\n")
                fh.write(json.dumps({"ts": "t", "sid": "a", "ev": "session.end", "scene": "L2"}) + "\n")
            code, d = run("query", p)
            self.assertEqual(d["play"]["level.fail"], 3)
            self.assertEqual(d["quit_point"], "L2")
            self.assertEqual(d["balance_signals"][0]["count"], 3)
            self.assertEqual(d["balance_by_level"][0], {"ev": "level.fail", "level": "L2", "count": 3})
        finally:
            shutil.rmtree(tmp)

    def test_finished_sessions_have_no_quit_point(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "s.jsonl")
            with open(p, "w") as fh:
                for lv in ("Genes", "Genes", "Steps"):
                    fh.write(json.dumps({"ts": "t", "sid": "a", "ev": "level.fail", "scene": "deck",
                                         "f": {"level": lv}}) + "\n")
                fh.write(json.dumps({"ts": "t", "sid": "a", "ev": "session.end", "scene": "deck",
                                     "f": {"finished": True}}) + "\n")
            code, d = run("query", p, "--grind")
            self.assertIsNone(d["quit_point"])
            self.assertEqual(d["sessions"], {"total": 1, "finished": 1})
            self.assertEqual(d["balance_by_level"][0]["level"], "Genes")
            self.assertEqual([x["title"] for x in d["proposals"]], ["level.fail at Genes happened 2 times"])
        finally:
            shutil.rmtree(tmp)

    def test_missing_path(self):
        code, d = run("query", "nope/nope.log")
        self.assertEqual(code, 1)
        self.assertFalse(d["ok"])


class TestAgent(unittest.TestCase):
    def test_requestid_once(self):
        code, d = run("agent", os.path.join(FIX, "split", "session.jsonl"))
        self.assertEqual(d["tokens"]["output_tokens"], 1500)

    def test_subagents_included(self):
        code, d = run("agent", os.path.join(FIX, "sub", "abc.jsonl"))
        self.assertEqual(d["tool_calls"], 41)
        self.assertGreater(d["subagent_token_share"], 0.5)


class TestSchemaPrivacy(unittest.TestCase):
    def test_schema_validate(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "e.jsonl")
            with open(p, "w") as fh:
                fh.write(json.dumps({"ts": "t", "sid": "a", "ev": "x"}) + "\n")
                fh.write(json.dumps({"ts": "t", "sid": "a", "ev": "x", "f": {"email": "e"}}) + "\n")
            code, d = run("schema", p)
            self.assertEqual(code, 1)
            self.assertEqual(d["bad_count"], 1)
        finally:
            shutil.rmtree(tmp)

    def test_child_mode_fails_on_send(self):
        tmp = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp, "a.js"), "w") as fh:
                fh.write("fetch('https://x.example/collect')\n")
            code, d = run("privacy", tmp, "--child")
            self.assertEqual(code, 1)
            code, d = run("privacy", tmp)
            self.assertEqual(code, 0)
        finally:
            shutil.rmtree(tmp)

    def test_usage_error_exit_2(self):
        code, _ = run("bogus")
        self.assertEqual(code, 2)

    def test_every_documented_form(self):
        for args in (["schema"], ["doctor"], ["read", os.path.join(FIX, "flood", "Player.log")]):
            code, d = run(*args)
            self.assertEqual(code, 0, args)


if __name__ == "__main__":
    unittest.main()
