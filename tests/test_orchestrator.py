import unittest

from jarvis.agents.base import BaseAgent, AgentProposal
from jarvis.orchestrator import Orchestrator


class StubAgent(BaseAgent):
    def __init__(self, name, proposal):
        self.name = name
        self._proposal = proposal

    def propose(self, task, repo_context, memory_summary):
        return self._proposal


class TestOrchestrator(unittest.TestCase):
    def test_merge_deduplicates_actions(self):
        a1 = StubAgent("Logic", AgentProposal(agent="Logic", actions=[{"type": "command", "name": "A", "command": "echo hi"}]))
        a2 = StubAgent("Pragmatic", AgentProposal(agent="Pragmatic", actions=[{"type": "command", "name": "A", "command": "echo hi"}, {"type": "run_tests", "name": "Tests"}]))
        a3 = StubAgent("Safeguard", AgentProposal(agent="Safeguard", vote="approve"))

        plan = Orchestrator([a1, a2, a3]).deliberate("task", "repo", "mem")
        self.assertFalse(plan.blocked)
        self.assertEqual(len(plan.actions), 2)

    def test_safeguard_veto_blocks_execution(self):
        blocker = StubAgent(
            "Safeguard",
            AgentProposal(
                agent="Safeguard",
                vote="block",
                rationale="danger",
                unblock_requirements=["need scope"],
            ),
        )
        plan = Orchestrator([blocker]).deliberate("drop database", "repo", "mem")
        self.assertTrue(plan.blocked)
        self.assertEqual(plan.reason, "danger")
        self.assertEqual(plan.unblock_requirements, ["need scope"])


if __name__ == "__main__":
    unittest.main()
