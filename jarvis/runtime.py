"""Shared runtime helpers for Jarvis CLI and gateway."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import List, Tuple

from jarvis.orchestrator import Orchestrator
from jarvis.tools import ToolRunner, ScaffoldNextJS, RunTests

ActionResult = Tuple[dict, int, str, str]


def extract_json(stdout: str) -> dict:
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
    summary = extract_json(proc.stdout)
    return json.dumps(summary)


def build_plan(task: str, repo_root: Path, memory_summary: str | None = None):
    summary = memory_summary if memory_summary is not None else load_memory_summary(repo_root)
    repo_context = f"repo={repo_root}"
    orchestrator = Orchestrator()
    return orchestrator.deliberate(task, repo_context, summary)


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


def execute_plan(plan, repo_root: Path) -> List[ActionResult]:
    runner = ToolRunner()
    test_tool = RunTests(runner)
    next_tool = ScaffoldNextJS(runner)
    results: List[ActionResult] = []

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


def log_outcome(repo_root: Path, task: str, blocked: bool, execution_results: List[ActionResult]) -> None:
    if os.getenv("JARVIS_DRY_RUN") == "1":
        return

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


def run_task(task: str, repo_root: Path, plan_only: bool = False, dry_run: bool = False) -> tuple[int, str]:
    memory_summary = load_memory_summary(repo_root)
    plan = build_plan(task, repo_root, memory_summary)
    plan_text = format_plan(plan)

    if plan.blocked:
        log_outcome(repo_root, task, True, [])
        return 1, plan_text

    if plan_only:
        return 0, plan_text

    previous = os.getenv("JARVIS_DRY_RUN")
    if dry_run:
        os.environ["JARVIS_DRY_RUN"] = "1"

    try:
        results = execute_plan(plan, repo_root)
        output_lines = [plan_text]
        for action, code, stdout, stderr in results:
            output_lines.append(f"\n[{action.get('type')}] {action.get('name','')} => rc={code}")
            if stdout.strip():
                output_lines.append(stdout.strip())
            if stderr.strip():
                output_lines.append(stderr.strip())

        log_outcome(repo_root, task, False, results)
        code = 0 if not results or results[-1][1] == 0 else 1
        return code, "\n".join(output_lines)
    finally:
        if dry_run:
            if previous is None:
                os.environ.pop("JARVIS_DRY_RUN", None)
            else:
                os.environ["JARVIS_DRY_RUN"] = previous
