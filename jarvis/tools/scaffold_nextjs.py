"""Tool for scaffolding Next.js apps."""

from pathlib import Path
from .tool_runner import ToolRunner, ToolResult


class ScaffoldNextJS:
    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner()

    def run(self, repo_root: str, app_name: str) -> ToolResult:
        apps_dir = Path(repo_root) / "apps"
        apps_dir.mkdir(parents=True, exist_ok=True)
        cmd = f"npx create-next-app@latest {app_name} --yes"
        return self.runner.run(cmd, cwd=str(apps_dir))
