import json
import subprocess
import sys
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _extract_json(mixed_output: str) -> dict:
    start = mixed_output.find('{')
    if start == -1:
        raise AssertionError(f"No JSON object in output: {mixed_output}")
    return json.loads(mixed_output[start:])


class TestHybridSearchKeywordOnly(unittest.TestCase):
    def test_keyword_only_returns_result_for_known_term(self):
        token = f"bootstrapped-regression-{int(time.time())}"

        add_cmd = [
            sys.executable,
            "tools/memory/memory_db.py",
            "--action",
            "add",
            "--type",
            "event",
            "--content",
            token,
            "--importance",
            "6",
        ]
        added = subprocess.run(
            add_cmd,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        add_json = _extract_json(added.stdout)
        self.assertTrue(add_json.get("success"), added.stdout)

        search_cmd = [
            sys.executable,
            "tools/memory/hybrid_search.py",
            "--query",
            token,
            "--keyword-only",
            "--limit",
            "5",
        ]
        search = subprocess.run(
            search_cmd,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        search_json = _extract_json(search.stdout)
        self.assertTrue(search_json.get("success"), search.stdout)
        self.assertGreaterEqual(len(search_json.get("results", [])), 1, search.stdout)


if __name__ == "__main__":
    unittest.main()
