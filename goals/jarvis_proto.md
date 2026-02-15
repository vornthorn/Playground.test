# Jarvis Proto v0

## What Jarvis is

Jarvis proto v0 is a CLI orchestration layer for this GOTCHA repo. It performs deterministic multi-agent deliberation, builds an execution plan, runs shell/tools in sequence, and logs outcomes to persistent memory.

## How to run

```bash
python jarvis.py "your task"
python jarvis.py "your task" --plan-only
python jarvis.py "your task" --repo /path/to/repo
```

Behavior:
1. Runs preflight startup (`scripts/start.sh` when available)
2. Loads memory summary via `tools/memory/memory_read.py --format summary`
3. Deliberates with agents (Logic, Pragmatic, Safeguard, Efficiency, HumanImpact)
4. If `--plan-only`, prints merged plan and exits
5. Else executes plan via tool interfaces and logs final event with `tools/memory/memory_write.py`

## How to add agents

1. Create a new class in `jarvis/agents/` implementing `BaseAgent.propose(...)`.
2. Return an `AgentProposal` with `vote`, `rationale`, and `actions`.
3. Register the agent in `jarvis/agents/__init__.py` and `Orchestrator` default list.

## How to add tools

1. Add a new tool class in `jarvis/tools/`.
2. Keep tool behavior deterministic and side-effect scoped.
3. Extend `jarvis.py::execute_plan` to map a plan action `type` to the tool method.

## Memory usage

Jarvis reads memory at start (`memory_read.py`) and logs outcomes as event entries (`memory_write.py`). This keeps a session history in both markdown daily logs and SQLite memory entries.
