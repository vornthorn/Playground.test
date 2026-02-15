"""LLM adapter interfaces for future Jarvis model integrations."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMRequest:
    system_prompt: str
    user_prompt: str


class LLMAdapter(Protocol):
    """Pluggable interface for future OpenAI/Claude integrations."""

    def complete(self, request: LLMRequest) -> str:
        ...


class NoopLLMAdapter:
    """Deterministic placeholder implementation used in proto v0."""

    def complete(self, request: LLMRequest) -> str:
        return "LLM disabled in Jarvis proto v0"
