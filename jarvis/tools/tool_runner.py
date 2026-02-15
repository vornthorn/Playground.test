"""Deterministic shell tool runner."""

import subprocess
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ToolResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


class ToolRunner:
    def run(self, cmd: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> ToolResult:
        proc = subprocess.run(cmd, cwd=cwd, env=env, shell=True, text=True, capture_output=True)
        return ToolResult(command=cmd, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
