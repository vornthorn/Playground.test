"""Tool for running project tests based on repository type."""

from pathlib import Path
from .tool_runner import ToolRunner, ToolResult


class RunTests:
    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner()

    def detect_and_run(self, repo_root: str) -> ToolResult:
        root = Path(repo_root)
        if (root / "package.json").exists():
            return self.runner.run("npm test", cwd=repo_root)
        if list(root.glob("*.csproj")) or list(root.rglob("*.sln")):
            return self.runner.run("dotnet test", cwd=repo_root)
        if (root / "tests").exists():
            return self.runner.run("python -m unittest", cwd=repo_root)
        return ToolResult(command="noop", returncode=0, stdout="No tests detected", stderr="")
