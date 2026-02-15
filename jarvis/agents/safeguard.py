from .base import BaseAgent, AgentProposal


class SafeguardAgent(BaseAgent):
    name = "Safeguard"
    BLOCK_PATTERNS = [
        "rm -rf /",
        "delete production",
        "drop database",
        "exfiltrate",
        "malware",
    ]

    def propose(self, task: str, repo_context: str, memory_summary: str) -> AgentProposal:
        lowered = task.lower()
        for pattern in self.BLOCK_PATTERNS:
            if pattern in lowered:
                return AgentProposal(
                    agent=self.name,
                    vote="block",
                    rationale=f"Blocked due to dangerous instruction pattern: '{pattern}'.",
                    unblock_requirements=[
                        "Clarify safe environment and target scope.",
                        "Provide explicit approval for destructive operations.",
                        "Provide rollback/backup strategy.",
                    ],
                )
        return AgentProposal(
            agent=self.name,
            rationale="No critical safety violations detected.",
            risks=["Always validate command scope before execution."],
        )
