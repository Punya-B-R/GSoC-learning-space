"""
Team Formation Model (Meta-Agent Example)
==========================================

Demonstrates Mesa's meta-agent capability through a simple organization
simulation. Employees with similar skills form teams (meta-agents). Teams
dissolve when their average productivity drops below a threshold.

Pain points discovered while building this model:
1. create_meta_agent raises MRO error when passed a MetaAgent subclass
2. remove_constituting_agents incorrectly deregisters sub-agents (KeyError bug)
3. meta_agents set on sub-agents is not reliably cleared on dissolution
4. Step propagation must be handled entirely by the user
5. Checking if an agent is free requires ugly: len(getattr(a, "meta_agents", set())) == 0
"""

from mesa import Model
from mesa.datacollection import DataCollector

from agents import EmployeeAgent, TeamAgent


class TeamFormationModel(Model):
    """Organization model where employees form and dissolve teams."""

    def __init__(
        self,
        num_employees=20,
        skill_threshold=0.2,
        dissolve_threshold=0.3,
        rng=None,
    ):
        super().__init__(rng=rng)

        self.num_employees = num_employees
        self.skill_threshold = skill_threshold
        self.dissolve_threshold = dissolve_threshold
        self.teams_to_dissolve = []

        for _ in range(num_employees):
            skill = self.random.random()
            productivity = self.random.random()
            EmployeeAgent(self, skill, productivity)

        self.datacollector = DataCollector(
            model_reporters={
                "Teams": lambda m: len([a for a in m.agents if isinstance(a, TeamAgent)]),
                "Unassigned Employees": lambda m: self._count_free_employees(),
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def _count_free_employees(self):
        return len(self._get_free_employees())

    def _get_free_employees(self):
        """Return employees not currently in any team."""
        return [
            a for a in self.agents
            if isinstance(a, EmployeeAgent)
            and not getattr(a, "in_team", False)
        ]

    def dissolve_team(self, team):
        """Queue a team for dissolution."""
        if team not in self.teams_to_dissolve:
            self.teams_to_dissolve.append(team)

    def _process_dissolutions(self):
        """Process all pending team dissolutions."""
        for team in self.teams_to_dissolve:
            # Release all members back to free pool
            for agent in list(team.agents):
                agent.in_team = False
                if hasattr(agent, "meta_agents"):
                    agent.meta_agents.discard(team)
                if hasattr(agent, "meta_agent") and agent.meta_agent is team:
                    agent.meta_agent = None
            team.remove()
        self.teams_to_dissolve.clear()

    def _form_teams(self):
        """Try to form new teams from free employees."""
        free = self._get_free_employees()
        self.random.shuffle(free)
        paired = set()

        for i, emp1 in enumerate(free):
            if emp1.unique_id in paired:
                continue
            for emp2 in free[i + 1:]:
                if emp2.unique_id in paired:
                    continue
                if abs(emp1.skill - emp2.skill) < self.skill_threshold:
                    team = TeamAgent(self, [emp1, emp2])
                    emp1.in_team = True
                    emp2.in_team = True
                    paired.add(emp1.unique_id)
                    paired.add(emp2.unique_id)
                    break

    def step(self):
        # Step all teams
        for agent in list(self.agents):
            if isinstance(agent, TeamAgent):
                agent.step()

        # Step free employees
        for agent in list(self.agents):
            if isinstance(agent, EmployeeAgent) and not getattr(agent, "in_team", False):
                agent.step()

        self._process_dissolutions()
        self._form_teams()
        self.datacollector.collect(self)


if __name__ == "__main__":
    model = TeamFormationModel()
    for _ in range(20):
        model.step()
    data = model.datacollector.get_model_vars_dataframe()
    print(data)