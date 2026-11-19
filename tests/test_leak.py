"""Leak test: no private sidecar term may appear in a tracked file.

Runs only when LOGWRIGHT_HOME points at the private sidecar holding leak-terms.txt.
"""
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_terms():
    home = os.environ.get("LOGWRIGHT_HOME")
    if not home:
        return None
    f = Path(home) / "leak-terms.txt"
    if not f.is_file():
        return None
    return [t.strip() for t in f.read_text(encoding="utf-8").splitlines()
            if t.strip() and not t.startswith("#")]


class LeakTest(unittest.TestCase):
    def test_no_sidecar_terms_in_tracked_files(self):
        terms = load_terms()
        if terms is None:
            self.skipTest("LOGWRIGHT_HOME unset or has no leak-terms.txt")
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                               text=True, check=True).stdout.splitlines()
        hits = []
        for name in files:
            try:
                text = (ROOT / name).read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            for t in terms:
                if t.lower() in text or t.lower() in name.lower():
                    hits.append(f"{name}: {t}")
        self.assertEqual(hits, [], "sidecar terms in public files")


if __name__ == "__main__":
    unittest.main()
