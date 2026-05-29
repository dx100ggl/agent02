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

    # ---------------------------------------------------------
    # Reflection / meta hooks
    # ---------------------------------------------------------
    def set_flag(self, key: str, value: bool):
        self.flags[key] = value

    def set_preference(self, key: str, weight: float):
        self.preferences[key] = weight

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
