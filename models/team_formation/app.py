import solara
from matplotlib.figure import Figure

from mesa.visualization import SolaraViz, make_plot_component
from model import TeamFormationModel, TeamAgent, EmployeeAgent


def make_org_chart(model):
    """Visualize employees and teams."""
    fig = Figure(figsize=(6, 4))
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    ax = fig.add_subplot(111)

    # Plot unassigned employees
    free = [
        a for a in model.agents
        if isinstance(a, EmployeeAgent)
        and len(getattr(a, "meta_agents", set())) == 0
    ]
    if free:
        ax.scatter(
            [a.skill for a in free],
            [a.productivity for a in free],
            c="#a8dadc", s=80, label="Unassigned", zorder=3
        )

    # Plot teams
    teams = [a for a in model.agents if isinstance(a, TeamAgent)]
    colors = ["#e63946", "#457b9d", "#f4a261", "#2a9d8f", "#e9c46a"]
    for i, team in enumerate(teams):
        members = list(team.agents)
        color = colors[i % len(colors)]
        ax.scatter(
            [a.skill for a in members],
            [a.productivity for a in members],
            c=color, s=80, label=f"Team {i + 1}", zorder=3
        )
        # Draw circle around team
        cx = sum(a.skill for a in members) / len(members)
        cy = sum(a.productivity for a in members) / len(members)
        circle = __import__("matplotlib.patches", fromlist=["Circle"]).Circle(
            (cx, cy), 0.08, fill=False, color=color, linewidth=1.5
        )
        ax.add_patch(circle)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("Skill", fontsize=10)
    ax.set_ylabel("Productivity", fontsize=10)
    ax.set_title(
        f"Employees: {len(free)} free, {len(teams)} teams", fontsize=11
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if free or teams:
        ax.legend(fontsize=8, loc="upper left")

    return solara.FigureMatplotlib(fig)


TeamsPlot = make_plot_component({"Teams": "#e63946", "Unassigned Employees": "#a8dadc"})

model_params = {
    "rng": {
        "type": "SliderInt",
        "value": 42,
        "label": "Random Seed",
        "min": 0,
        "max": 1000,
        "step": 1,
    },
    "num_employees": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of employees",
        "min": 5,
        "max": 50,
        "step": 5,
    },
    "skill_threshold": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Skill threshold (team formation)",
        "min": 0.05,
        "max": 0.5,
        "step": 0.05,
    },
    "dissolve_threshold": {
        "type": "SliderFloat",
        "value": 0.3,
        "label": "Dissolve threshold (min productivity)",
        "min": 0.1,
        "max": 0.7,
        "step": 0.05,
    },
}

model = TeamFormationModel()

page = SolaraViz(
    model,
    components=[make_org_chart, TeamsPlot],
    model_params=model_params,
    name="Team Formation Model",
)
page  # noqa: B018