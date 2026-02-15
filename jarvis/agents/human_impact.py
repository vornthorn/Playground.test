from .base import BaseAgent, AgentProposal


class HumanImpactAgent(BaseAgent):
    name = "HumanImpact"

    def propose(self, task: str, repo_context: str, memory_summary: str) -> AgentProposal:
        return AgentProposal(
            agent=self.name,
            rationale="Keep outputs understandable and include operational next steps.",
            actions=[{"type": "command", "name": "Emit operator notice", "command": "echo 'HumanImpact: include runbook updates in summary'"}],
        )
