# Team Formation Model

## Purpose

Built to explore Mesa's meta-agents module hands-on before writing the GSoC proposal. The goal was to exercise the full meta-agent lifecycle: formation, coordinated behavior, and dissolution.

## What the model does

Employees with similar skill levels dynamically form teams (meta-agents). Teams dissolve when their average productivity drops below a threshold. Members return to the free pool and can form new teams.

## What I learned

Three bugs in the current meta-agents module surfaced during development:

**Bug 1 — remove_constituting_agents raises KeyError**
Calling `team.remove_constituting_agents(members)` crashed because it tried to deregister employee agents from the model registry. Employees are still active model agents and should not be deregistered. Workaround: bypass the method entirely and manually clear `meta_agents` references.

**Bug 2 — create_meta_agent raises MRO error**
Passing `TeamAgent` as the `mesa_agent_type` argument raised `TypeError: Cannot create a consistent method resolution order`. Because `TeamAgent` already inherits `MetaAgent`, the function cannot create a new class inheriting from both. Workaround: instantiate `TeamAgent` directly instead.

**Bug 3 — meta_agents tracking unreliable after dissolution**
The `meta_agents` set on each agent is not initialized until the agent first joins a meta-agent, and is not reliably cleared after dissolution. Workaround: use a simple `agent.in_team` boolean flag managed directly by the model.

## API pain points discovered

- No default step propagation — must manually loop through members every time
- Checking free agent status requires `len(getattr(agent, "meta_agents", set())) == 0` — verbose and fragile
- Two attributes for the same thing: `agent.meta_agent` and `agent.meta_agents`
- No `model.meta_agents` property
- `create_meta_agent()` produces unpicklable classes (serialization broken)

## How to run
```bash
pip install mesa solara matplotlib
solara run app.py
```

## Connection to GSoC proposal

These findings directly informed the proposed fixes and new features in my GSoC 2026 proposal for the Meta Agents project.