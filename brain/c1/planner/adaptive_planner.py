# brain/c1/planner/adaptive_planner.py

from typing import Dict, Any, Optional
from brain.c1.planner.plan import Plan
from brain.c1.planner.tool_schema import ToolSchema


class AdaptivePlanner:
    """
    Memory‑guided, tool‑aware planner.

    Backward compatible with:
        AdaptivePlanner()
    Forward compatible with:
        AdaptivePlanner(llm_callable=...)
    """

    def __init__(self, tools=None, llm_callable=None):
        self.tools = tools
        self.llm_callable = llm_callable  # <-- NEW but optional
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
        plan = Plan(user_input=user_input)

        mode = directive.mode.value
        schema = directive.schema

        plan.meta["mode"] = mode
        plan.meta["schema"] = schema

        if self.tools:
            tool_schemas = self.tools.list_schemas()
            plan.meta["available_tools"] = list(tool_schemas.keys())

        if memory_results:
            plan.meta["memory_hits"] = len(memory_results)
            self._inject_memory_context(plan, memory_results)

        if schema == "tool_call":
            self._build_tool_call_plan(plan, user_input)
        else:
            self._build_llm_plan(plan, user_input)

        return plan

    # ---------------------------------------------------------
    # Memory‑guided context
    # ---------------------------------------------------------
    def _inject_memory_context(self, plan: Plan, memory_results):
        # Legacy MemoryItem support
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

        # --- SPECIALIZED: research pipeline for tickers ---
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

                # These tool names must match your ToolRegistry keys
                # Adjust if your actual names differ.
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

        # --- FALLBACK: existing generic tool selection logic ---
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

        # -----------------------------------------
        # Cautious Mode: safer, more explicit plans
        # -----------------------------------------
        if self.cautious_mode:
            # 1. Add precondition checks before each step
            for step in plan.steps:
                step.preconditions = step.preconditions or []
                step.preconditions.append("memory_check")
                step.preconditions.append("input_available")

            # 2. Add a verification step after each tool call
            verified_steps = []
            for step in plan.steps:
                verified_steps.append(step)
                if step.tool:
                    verified_steps.append(
                        step.clone_with(
                            description=f"Verify result of {step.tool}",
                            tool="verify_tool",
                            args={"target": step.tool},
                        )
                    )
            plan.steps = verified_steps

            # 3. Avoid aggressive tool chaining
            plan.meta["max_chain_length"] = 1

            # 4. Prefer memory retrieval before tool calls
            plan.meta["prefer_memory"] = True


    # ---------------------------------------------------------
    # LLM‑only plan
    # ---------------------------------------------------------
    def _build_llm_plan(self, plan: Plan, user_input: str):
        plan.add_step(
            description="LLM reasoning",
            tool="llm",
            args={"prompt": user_input},
        )
