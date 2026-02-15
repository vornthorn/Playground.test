"""Jarvis multi-agent orchestrator for proto v0."""

from dataclasses import dataclass, field
from typing import List

from jarvis.agents import (
    BaseAgent,
    LogicAgent,
    PragmaticAgent,
    SafeguardAgent,
    EfficiencyAgent,
    HumanImpactAgent,
    AgentProposal,
)


@dataclass
class ExecutionPlan:
    task: str
    blocked: bool
    reason: str = ""
    unblock_requirements: List[str] = field(default_factory=list)
    actions: List[dict] = field(default_factory=list)
    proposals: List[AgentProposal] = field(default_factory=list)


class Orchestrator:
    def __init__(self, agents: List[BaseAgent] | None = None) -> None:
        self.agents = agents or [
            LogicAgent(),
            PragmaticAgent(),
            SafeguardAgent(),
            EfficiencyAgent(),
            HumanImpactAgent(),
        ]

    def deliberate(self, task: str, repo_context: str, memory_summary: str) -> ExecutionPlan:
        proposals = [a.propose(task, repo_context, memory_summary) for a in self.agents]

        safeguard = next((p for p in proposals if p.agent == "Safeguard"), None)
        if safeguard and safeguard.vote == "block":
            return ExecutionPlan(
                task=task,
                blocked=True,
                reason=safeguard.rationale,
                unblock_requirements=safeguard.unblock_requirements,
                proposals=proposals,
            )

        actions: List[dict] = []
        seen = set()
        for proposal in proposals:
            for action in proposal.actions:
                key = (action.get("type"), action.get("command"), action.get("app_name"), action.get("name"))
                if key not in seen:
                    seen.add(key)
                    actions.append(action)

        return ExecutionPlan(task=task, blocked=False, actions=actions, proposals=proposals)
