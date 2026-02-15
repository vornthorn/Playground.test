from .base import BaseAgent, AgentProposal


class PragmaticAgent(BaseAgent):
    name = "Pragmatic"

    def propose(self, task: str, repo_context: str, memory_summary: str) -> AgentProposal:
        actions = []
        if "next" in task.lower():
            actions.append({
                "type": "scaffold_nextjs",
                "name": "Scaffold Next.js app",
                "app_name": "jarvis-app",
            })
        actions.append({"type": "command", "name": "Show concise summary", "command": "echo 'Pragmatic pass complete'"})
        return AgentProposal(
            agent=self.name,
            rationale="Prefer smallest set of changes needed to satisfy the task.",
            actions=actions,
        )
