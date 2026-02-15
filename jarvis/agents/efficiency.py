from .base import BaseAgent, AgentProposal


class EfficiencyAgent(BaseAgent):
    name = "Efficiency"

    def propose(self, task: str, repo_context: str, memory_summary: str) -> AgentProposal:
        return AgentProposal(
            agent=self.name,
            rationale="Batch related checks and avoid redundant commands.",
            actions=[{"type": "command", "name": "Quick health check", "command": "python -m py_compile tools/memory/hybrid_search.py"}],
        )
