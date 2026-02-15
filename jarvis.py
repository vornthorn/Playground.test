#!/usr/bin/env python3
"""Jarvis proto v0 CLI orchestrator."""

import argparse
from pathlib import Path

from jarvis.runtime import run_preflight, run_task


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis proto v0")
    parser.add_argument("task", help="Task prompt for Jarvis")
    parser.add_argument("--plan-only", action="store_true", help="Only print the merged plan")
    parser.add_argument("--repo", default=".", help="Repository path")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    run_preflight(repo_root)

    code, text = run_task(args.task, repo_root, plan_only=args.plan_only)
    print(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
