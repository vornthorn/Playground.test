#!/usr/bin/env python3
"""Jarvis proto v0 CLI orchestrator."""

import argparse
import json
import subprocess
from pathlib import Path

from jarvis.orchestrator import Orchestrator
from jarvis.tools import ToolRunner, ScaffoldNextJS, RunTests


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    if start == -1:
        return {}
    return json.loads(stdout[start:])


def run_preflight(repo_root: Path) -> None:
    start_script = repo_root / "scripts" / "start.sh"
    if start_script.exists():
        subprocess.run(["bash", str(start_script)], cwd=repo_root, check=True)
    else:
        subprocess.run(["python", "tools/memory/memory_read.py", "--format", "summary"], cwd=repo_root, check=True)


def load_memory_summary(repo_root: Path) -> str:
    proc = subprocess.run(
        ["python", "tools/memory/memory_read.py", "--format", "summary"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    summary = _extract_json(proc.stdout)
    return json.dumps(summary)


def format_plan(plan) -> str:
    if plan.blocked:
        lines = [f"BLOCKED: {plan.reason}"]
        if plan.unblock_requirements:
            lines.append("Unblock requirements:")
            lines.extend([f"- {item}" for item in plan.unblock_requirements])
        return "\n".join(lines)

    lines = ["Execution Plan:"]
    for idx, action in enumerate(plan.actions, 1):
        lines.append(f"{idx}. {action.get('type')} - {action.get('name', '')}")
    return "\n".join(lines)


def execute_plan(plan, repo_root: Path) -> list[tuple[dict, int, str, str]]:
    runner = ToolRunner()
    test_tool = RunTests(runner)
    next_tool = ScaffoldNextJS(runner)
    results = []

    for action in plan.actions:
        kind = action.get("type")
        if kind == "command":
            result = runner.run(action["command"], cwd=str(repo_root))
        elif kind == "run_tests":
            result = test_tool.detect_and_run(str(repo_root))
        elif kind == "scaffold_nextjs":
            result = next_tool.run(str(repo_root), action.get("app_name", "jarvis-app"))
        else:
            continue

        results.append((action, result.returncode, result.stdout, result.stderr))
        if result.returncode != 0:
            break

    return results


def log_outcome(repo_root: Path, task: str, blocked: bool, execution_results: list[tuple[dict, int, str, str]]) -> None:
    if blocked:
        summary = f"Jarvis blocked task: {task}"
    elif execution_results and execution_results[-1][1] != 0:
        summary = f"Jarvis task failed: {task}"
    else:
        summary = f"Jarvis completed task: {task}"

    subprocess.run(
        [
            "python",
            "tools/memory/memory_write.py",
            "--content",
            summary,
            "--type",
            "event",
            "--importance",
            "6",
        ],
        cwd=repo_root,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis proto v0")
    parser.add_argument("task", help="Task prompt for Jarvis")
    parser.add_argument("--plan-only", action="store_true", help="Only print the merged plan")
    parser.add_argument("--repo", default=".", help="Repository path")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    run_preflight(repo_root)
    memory_summary = load_memory_summary(repo_root)
    repo_context = f"repo={repo_root}"

    orchestrator = Orchestrator()
    plan = orchestrator.deliberate(args.task, repo_context, memory_summary)

    print(format_plan(plan))

    if plan.blocked or args.plan_only:
        log_outcome(repo_root, args.task, plan.blocked, [])
        return 1 if plan.blocked else 0

    results = execute_plan(plan, repo_root)
    for action, code, stdout, stderr in results:
        print(f"\n[{action.get('type')}] {action.get('name','')} => rc={code}")
        if stdout.strip():
            print(stdout.strip())
        if stderr.strip():
            print(stderr.strip())

    log_outcome(repo_root, args.task, False, results)
    return 0 if not results or results[-1][1] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
