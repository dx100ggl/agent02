# brain/c1/planner/adaptive_planner.py

from typing import Dict, Any, Optional
from brain.c1.planner.plan import Plan, PlanStep, PlanStepKind
from brain.c1.planner.tool_schema import ToolSchema


class AdaptivePlanner:
    """
    Memory‑guided, tool‑aware planner with optional C5 belief heuristics.
    """

    def __init__(self, tools=None, llm_callable=None):
        self.tools = tools
        self.llm_callable = llm_callable
        self.meta_mode = "default"
        self.flags = {}
        self.preferences = {}
        self.cautious_mode = False
        self.enforce_preconditions = False
        self.avoid_redundancy = False

    # ---------------------------------------------------------
    # Reflection / meta hooks
    # ---------------------------------------------------------
    def set_flag(self, key: str, value: bool):
        self.flags[key] = value

    def set_preference(self, key: str, weight: float):
        self.preferences[key] = weight

    def set_cautious(self, value: bool):
        self.cautious_mode = value

    # ---------------------------------------------------------
    # Main planning entry point
    # ---------------------------------------------------------
    def create_plan(self, user_input: str, directive, memory_results=None) -> Plan:
        plan = Plan(steps=[])

        mode = directive.mode.value if directive else "default"
        schema = directive.schema if directive else None

        plan.meta["mode"] = mode
        plan.meta["schema"] = schema

        # ---------------------------------------------------------
        # NEW: Belief integration (C5 → C1)
        # ---------------------------------------------------------
        beliefs = []
        if isinstance(directive, dict) and "beliefs" in directive:
            beliefs = directive["beliefs"]
        elif hasattr(directive, "beliefs"):
            beliefs = directive.beliefs

        plan.meta["beliefs"] = beliefs or []

        # Apply belief‑driven heuristics
        self._apply_belief_heuristics(plan)

        # ---------------------------------------------------------
        # Existing metadata logic
        # ---------------------------------------------------------
        if self.tools:
            tool_schemas = self.tools.list_schemas()
            plan.meta["available_tools"] = list(tool_schemas.keys())

        if memory_results:
            plan.meta["memory_hits"] = len(memory_results)
            self._inject_memory_context(plan, memory_results)

        # ---------------------------------------------------------
        # Existing plan construction logic
        # ---------------------------------------------------------
        if schema == "tool_call":
            self._build_tool_call_plan(plan, user_input)
        else:
            self._build_llm_plan(plan, user_input)

        # ---------------------------------------------------------
        # Cautious mode: insert verification steps after each tool
        # ---------------------------------------------------------
        if self.cautious_mode:
            new_steps = []
            for step in plan.steps:
                new_steps.append(step)

                if step.tool:
                    verify_step = PlanStep(
                        kind=PlanStepKind.TOOL,
                        tool_name="verify_tool",
                        params={"target": step.tool},
                        description=f"Verify result of {step.tool}",
                        tool="verify_tool",
                    )
                    new_steps.append(verify_step)

            plan.steps = new_steps

        return plan

    # ---------------------------------------------------------
    # Belief‑driven heuristics (C5)
    # ---------------------------------------------------------
    def _apply_belief_heuristics(self, plan: Plan):
        beliefs = plan.meta.get("beliefs", [])
        if not beliefs:
            return

        # 1. Preferences → verbosity
        if any(b.kind == "preference" and "concise" in b.metadata.get("tags", []) for b in beliefs):
            plan.meta["verbosity"] = "low"

        if any(b.kind == "preference" and "detailed" in b.metadata.get("tags", []) for b in beliefs):
            plan.meta["verbosity"] = "high"

        # 2. Skills → explanation depth
        if any(b.kind == "skill" for b in beliefs):
            plan.meta["explanation_level"] = "expert"

        # 3. Constraints → restricted tools
        constraints = [b for b in beliefs if b.kind == "constraint"]
        if constraints:
            restricted = []
            for b in constraints:
                restricted.extend(b.metadata.get("tags", []))
            plan.meta["restricted_tools"] = restricted

        # 4. Habits → ordering bias
        if any(b.kind == "habit" for b in beliefs):
            plan.meta["ordering_bias"] = "habit_first"

        # 5. Strong beliefs → shallow reasoning
        strong = [b for b in beliefs if b.strength >= 0.8]
        plan.meta["reasoning_depth"] = "shallow" if strong else "normal"

    # ---------------------------------------------------------
    # Memory‑guided context
    # ---------------------------------------------------------
    def _inject_memory_context(self, plan: Plan, memory_results):
        snippets = []
        for item in memory_results[:5]:
            if hasattr(item, "text"):
                snippets.append(item.text)
            elif hasattr(item, "record"):
                snippets.append(item.record.content)

        plan.meta["memory_context"] = snippets

        if any("instruction" in s.lower() for s in snippets):
            plan.meta["memory_bias"] = "llm_reasoning"
            plan.add_step(
                description="Use memory context",
                tool="llm",
                args={"prompt": "\n".join(snippets)},
            )

    # ---------------------------------------------------------
    # Tool‑aware plan construction
    # ---------------------------------------------------------
    def _build_tool_call_plan(self, plan: Plan, user_input: str):
        text = user_input.lower()

        # Specialized research pipeline
        if "research" in text:
            tokens = user_input.replace(",", " ").split()
            ticker = None
            for t in tokens:
                if t.isalpha() and t.isupper() and 1 <= len(t) <= 5:
                    ticker = t
                    break

            if ticker:
                plan.meta["mode"] = "research"
                plan.meta["ticker"] = ticker

                plan.add_step(
                    description=f"Fetch technical/market data for {ticker}",
                    tool="use_tool",
                    args={"tool": "market_data", "args": {"ticker": ticker}},
                )
                plan.add_step(
                    description=f"Fetch options and volatility data for {ticker}",
                    tool="use_tool",
                    args={"tool": "options_data", "args": {"ticker": ticker}},
                )
                plan.add_step(
                    description=f"Fetch sentiment and narrative for {ticker}",
                    tool="use_tool",
                    args={"tool": "sentiment_data", "args": {"ticker": ticker}},
                )
                plan.add_step(
                    description=f"Fetch macro/sector context for {ticker}",
                    tool="use_tool",
                    args={"tool": "macro_data", "args": {"ticker": ticker}},
                )
                plan.add_step(
                    description=f"Fetch historical analogs for {ticker}",
                    tool="use_tool",
                    args={"tool": "analogs_data", "args": {"ticker": ticker}},
                )
                return

        # Generic tool selection
        chosen_tool = None
        chosen_schema: Optional[ToolSchema] = None

        if not self.tools:
            self._build_llm_plan(plan, user_input)
            return

        for name, schema in self.tools.list_schemas().items():
            if any(word in user_input.lower() for word in schema.description.lower().split()):
                chosen_tool = name
                chosen_schema = schema
                break

        if not chosen_tool or not chosen_schema:
            self._build_llm_plan(plan, user_input)
            return

        args = {k: f"<{k}>" for k in chosen_schema.args.keys()}

        if not chosen_schema.validate_args(args):
            self._build_llm_plan(plan, user_input)
            return

        plan.add_step(
            description=f"Call tool {chosen_tool}",
            tool="use_tool",
            args={"tool": chosen_tool, "args": args},
        )

    # ---------------------------------------------------------
    # LLM‑only plan
    # ---------------------------------------------------------
    def _build_llm_plan(self, plan: Plan, user_input: str):
        plan.add_step(
            description="LLM reasoning",
            tool="llm",
            args={"prompt": user_input},
        )
