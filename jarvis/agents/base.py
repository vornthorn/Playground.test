"""Deterministic agent contracts for Jarvis proto v0."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class AgentProposal:
    agent: str
    vote: str = "approve"  # approve | block
    rationale: str = ""
    actions: List[Dict[str, str]] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    unblock_requirements: List[str] = field(default_factory=list)


class BaseAgent:
    name = "Base"

    def propose(self, task: str, repo_context: str, memory_summary: str) -> AgentProposal:
        raise NotImplementedError
