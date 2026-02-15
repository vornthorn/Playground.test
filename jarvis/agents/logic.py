from .base import BaseAgent, AgentProposal


class LogicAgent(BaseAgent):
    name = "Logic"

    def propose(self, task: str, repo_context: str, memory_summary: str) -> AgentProposal:
        actions = [
            {"type": "command", "name": "Inspect repository", "command": "git status --short"},
            {"type": "command", "name": "Locate relevant files", "command": "rg --files"},
        ]
        if "test" in task.lower() or "verify" in task.lower():
            actions.append({"type": "run_tests", "name": "Run project tests"})
        return AgentProposal(
            agent=self.name,
            rationale="Break down request into deterministic inspect/build/verify steps.",
            actions=actions,
        )
