from brain.c1.planner.plan import Plan
from brain.c2.plan_visualizer import PlanVisualizer


def visualize_plan(plan: Plan) -> str:
    return PlanVisualizer.visualize(plan)
