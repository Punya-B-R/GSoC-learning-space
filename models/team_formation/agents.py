import mesa
from mesa.experimental.meta_agents.meta_agent import MetaAgent


class EmployeeAgent(mesa.Agent):
    """An employee with a skill level and productivity.

    Attributes:
        skill (float): Skill level in [0, 1]
        productivity (float): Current productivity in [0, 1]
    """

    def __init__(self, model, skill, productivity):
        super().__init__(model)
        self.skill = skill
        self.productivity = productivity

    def step(self):
        # Productivity fluctuates slightly each step
        delta = self.random.uniform(-0.05, 0.05)
        self.productivity = max(0.0, min(1.0, self.productivity + delta))


class TeamAgent(MetaAgent):
    """A team composed of EmployeeAgents.

    Formed when employees have similar skill levels.
    Dissolves when average team productivity drops below a threshold.

    Attributes:
        avg_skill (float): Average skill of team members
        avg_productivity (float): Average productivity of team members
    """

    def __init__(self, model, agents):
        super().__init__(model, agents)
        self.avg_skill = self._compute_avg_skill()
        self.avg_productivity = self._compute_avg_productivity()

    def _compute_avg_skill(self):
        members = list(self.agents)
        if not members:
            return 0.0
        return sum(a.skill for a in members) / len(members)

    def _compute_avg_productivity(self):
        members = list(self.agents)
        if not members:
            return 0.0
        return sum(a.productivity for a in members) / len(members)

    def step(self):
        """Update team stats and dissolve if productivity is too low."""
        # Step all members
        for agent in self.agents:
            agent.step()

        self.avg_skill = self._compute_avg_skill()
        self.avg_productivity = self._compute_avg_productivity()

        # Dissolve team if average productivity drops below threshold
        if self.avg_productivity < self.model.dissolve_threshold:
            self.model.dissolve_team(self)