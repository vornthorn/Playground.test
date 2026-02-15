"""Routing layer between gateway requests and Jarvis orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from jarvis.runtime import build_plan, execute_plan, format_plan


class GatewayRouter:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)

    @staticmethod
    def _extract_json(stdout: str) -> dict:
        start = stdout.find("{")
        if start == -1:
            return {}
        return json.loads(stdout[start:])

    def load_memory_summary(self) -> str:
        proc = subprocess.run(
            ["python", "tools/memory/memory_read.py", "--format", "summary"],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.dumps(self._extract_json(proc.stdout))

    def handle(self, workspace: str, text: str, mode: str) -> str:
        memory_summary = self.load_memory_summary()
        plan = build_plan(text, self.repo_root, memory_summary=memory_summary)

        if mode == "plan":
            # strict side-effect free path: no execution, no memory writes
            return format_plan(plan)

        if plan.blocked:
            return format_plan(plan)

        results = execute_plan(plan, self.repo_root)
        lines = [format_plan(plan)]
        for action, code, stdout, stderr in results:
            lines.append(f"\n[{action.get('type')}] {action.get('name','')} => rc={code}")
            if stdout.strip():
                lines.append(stdout.strip())
            if stderr.strip():
                lines.append(stderr.strip())
        return "\n".join(lines)
