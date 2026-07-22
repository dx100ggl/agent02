# brain/c2/executor/executor.py

from __future__ import annotations
import json
from typing import Any, Dict

from brain.c1.planner.plan import ResearchPlan, PlanStep, PlanStepKind
from brain.c2.process_model import (
    ProcessModel,
    ProcessNode,
    NodeKind,
    ProcessRunner,
)

# NEW: master section normalizer
from brain.c4.normalizers.section_normalizer import SectionNormalizer


class Executor:
    """
    Stabilized C2 executor.
    Now collects raw tool outputs → normalizes → calls Synthesizer.synthesize_from_sections().
    """

    def __init__(self, tools=None, synthesizer=None, llm=None, memory=None, repair_planner=None):
        self._tools = tools
        self._synth = synthesizer
        self._llm = llm
        self.memory = memory
        self.repair_planner = repair_planner

        # OFF by default — DynamicRouter tests rely on this
        self.enable_argument_validation = False

        # Optional: max repair attempts
        self.max_repair_attempts = 1

        self._debug_override_model = None

        # NEW: master normalizer
        self._section_normalizer = SectionNormalizer()


    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def execute(self, plan: ResearchPlan, ctx: Dict[str, Any]) -> Dict[str, Any]:
        exec_ctx = {"steps": [], "final": None}

        # ---------------------------------------------------------
        # Belief‑aware execution context (C5 → C2)
        # ---------------------------------------------------------
        beliefs = ctx.get("beliefs", [])
        belief_score = ctx.get("belief_score")  # from DynamicRouter

        # Restricted tools (constraints)
        restricted = []
        for b in beliefs:
            if getattr(b, "kind", None) == "constraint":
                restricted.extend(b.metadata.get("tags", []))

        # Verbosity
        verbosity = None
        if any(b.kind == "preference" and "concise" in b.metadata.get("tags", []) for b in beliefs):
            verbosity = "concise"
        if any(b.kind == "preference" and "detailed" in b.metadata.get("tags", []) for b in beliefs):
            verbosity = "detailed"

        # Reasoning depth
        strong_beliefs = [b for b in beliefs if getattr(b, "strength", 0) >= 0.8]
        reasoning_depth = "shallow" if strong_beliefs else "normal"

        exec_ctx["beliefs"] = beliefs
        exec_ctx["verbosity"] = verbosity
        exec_ctx["reasoning_depth"] = reasoning_depth

        return self._execute_with_process_model(plan, exec_ctx)


    # ------------------------------------------------------------------
    # Step execution
    # ------------------------------------------------------------------
    def _execute_step(self, step: PlanStep, exec_ctx: Dict[str, Any]) -> Dict[str, Any]:
        kind = step.kind

        # FUNDAMENTALS
        if kind == PlanStepKind.FUNDAMENTALS:
            out = self._execute_fundamentals(step)
            exec_ctx["fundamentals_data"] = out["result"]
            return out

        # SYNTHESIZE (UPDATED)
        if kind == PlanStepKind.SYNTHESIZE:
            return self._execute_synthesis_stabilized(step, exec_ctx)

        # GENERIC TOOL STEPS
        if kind == PlanStepKind.TOOL:
            out = self._execute_tool(step)
            return out

        # MARKET / TECHNICALS / OPTIONS / SENTIMENT / MACRO / ANALOGS
        if kind == PlanStepKind.MARKET_DATA:
            out = self._execute_tool(step)
            exec_ctx["market_data"] = out["result"]
            return out

        if kind == PlanStepKind.TECHNICALS:
            out = self._execute_tool(step)
            exec_ctx["technicals_data"] = out["result"]
            return out

        if kind == PlanStepKind.OPTIONS:
            out = self._execute_tool(step)
            exec_ctx["options_data"] = out["result"]
            return out

        if kind == PlanStepKind.SENTIMENT:
            out = self._execute_tool(step)
            exec_ctx["sentiment_data"] = out["result"]
            return out

        if kind == PlanStepKind.MACRO:
            out = self._execute_tool(step)
            exec_ctx["macro_data"] = out["result"]
            return out

        if kind == PlanStepKind.ANALOGS:
            out = self._execute_tool(step)
            exec_ctx["analogs_data"] = out["result"]
            return out

        return {"step": step, "error": True, "message": f"Unknown step kind: {kind}"}


    # ------------------------------------------------------------------
    # NEW: Stabilized synthesis step
    # ------------------------------------------------------------------
    def _execute_synthesis_stabilized(self, step: PlanStep, exec_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stabilized synthesis:
        - Collect raw tool outputs from exec_ctx
        - Normalize via SectionNormalizer
        - Call Synthesizer.synthesize_from_sections()
        """

        # 1. Normalize all sections
        sections = self._section_normalizer.normalize(exec_ctx)

        # 2. Extract ticker + intent from step params
        ticker = step.params.get("ticker", "UNKNOWN")
        intent = step.params.get("intent", "")

        # 3. Beliefs already stored in exec_ctx
        beliefs = exec_ctx.get("beliefs", [])

        # 4. Call the new stabilized synthesizer
        result = self._synth.synthesize_from_sections(
            ticker=ticker,
            intent=intent,
            sections=sections,
            beliefs=beliefs,
        )

        return {"step": step, "result": result, "repaired": False}


    # ------------------------------------------------------------------
    # Fundamentals step
    # ------------------------------------------------------------------
    def _execute_fundamentals(self, step: PlanStep) -> Dict[str, Any]:
        tool = self._tools.get(step.tool_name)
        args = step.params

        result = self._safe_tool_call(tool, args)

        # Success
        if not self._is_failure(result):
            return {"step": step, "result": result, "repaired": False}

        # Failure — but repair disabled → return failure immediately
        if not self.enable_argument_validation:
            return {"step": step, "result": result, "repaired": False}

        # Failure — repair enabled
        repaired_args = self._repair_args(step, args, result)
        result2 = self._safe_tool_call(tool, repaired_args)

        return {
            "step": step,
            "result": result2,
            "repaired": True,
            "repair_args": repaired_args,
        }


    # ------------------------------------------------------------------
    # Generic tool step
    # ------------------------------------------------------------------
    def _execute_tool(self, step: PlanStep) -> Dict[str, Any]:
        tool = self._tools.get(step.tool_name)
        args = step.params

        result = self._safe_tool_call(tool, args)

        # Success
        if not self._is_failure(result):
            return {"step": step, "result": result, "repaired": False}

        # Failure — but repair disabled → return failure immediately
        if not self.enable_argument_validation:
            return {"step": step, "result": result, "repaired": False}

        # Failure — repair enabled
        repaired_args = self._repair_args(step, args, result)
        result2 = self._safe_tool_call(tool, repaired_args)

        return {
            "step": step,
            "result": result2,
            "repaired": True,
            "repair_args": repaired_args,
        }


    # ------------------------------------------------------------------
    # Search step (optional)
    # ------------------------------------------------------------------
    def _execute_search(self, step: PlanStep) -> Dict[str, Any]:
        return {"step": step, "result": {"search": "not implemented"}, "repaired": False}


    # ------------------------------------------------------------------
    # Tool call wrapper
    # ------------------------------------------------------------------
    def _safe_tool_call(self, tool, args: Dict[str, Any]) -> Any:
        try:
            # Tools may or may not implement normalize_args
            if hasattr(tool, "normalize_args"):
                normalized = tool.normalize_args(args)
            else:
                normalized = args

            if self.enable_argument_validation:
                self._validate_args(tool, normalized)

            return tool.run(normalized)

        except Exception as e:
            return {"error": True, "message": str(e)}

    def _is_failure(self, result: Any) -> bool:
        return isinstance(result, dict) and result.get("error")


    # ------------------------------------------------------------------
    # LLM-based argument repair
    # ------------------------------------------------------------------
    def _repair_args(self, step: PlanStep, args: Dict[str, Any], failure: Any) -> Dict[str, Any]:
        prompt = f"""
A tool call failed.

Tool: {step.tool_name}
Original arguments: {args}
Failure: {failure}

Task:
Suggest corrected arguments as a JSON dict.
Only return the JSON. No commentary.
"""

        raw = self._llm.complete(prompt)

        try:
            repaired = json.loads(raw)
            if isinstance(repaired, dict):
                return repaired
        except Exception:
            pass

        return args


    # ------------------------------------------------------------------
    # Argument validation
    # ------------------------------------------------------------------
    def _validate_args(self, tool, args):
        schema = getattr(tool, "schema", None)
        if not schema:
            return True

        required = schema.get("required", [])
        for field in required:
            if field not in args:
                raise ValueError(f"Missing required argument '{field}' for tool '{tool.name}'")

        properties = schema.get("properties", {})
        for key, expected in properties.items():
            if key in args:
                if expected == "string" and not isinstance(args[key], str):
                    raise TypeError(f"Argument '{key}' must be a string for tool '{tool.name}'")
                if expected == "number" and not isinstance(args[key], (int, float)):
                    raise TypeError(f"Argument '{key}' must be a number for tool '{tool.name}'")
                if expected == "boolean" and not isinstance(args[key], bool):
                    raise TypeError(f"Argument '{key}' must be a boolean for tool '{tool.name}'")

        return True


    # ------------------------------------------------------------------
    # Build a ProcessModel from a ResearchPlan
    # ------------------------------------------------------------------
    def _build_model_from_plan(self, plan: ResearchPlan) -> ProcessModel:
        model = ProcessModel(id="executor-process")

        # Start node
        model.add_node(ProcessNode(id="start", kind=NodeKind.START), is_start=True)

        # Create nodes for each step
        for step in plan.steps:
            def make_handler(s: PlanStep):
                def handler(ctx: Dict[str, Any]):
                    result = self._execute_step(s, ctx)
                    ctx["steps"].append(result)
                return handler

            model.add_node(
                ProcessNode(
                    id=step.id,
                    kind=NodeKind.TASK,
                    handler=make_handler(step),
                )
            )

        # End node
        model.add_node(ProcessNode(id="end", kind=NodeKind.END))

        # Edges: start → first step
        if plan.steps:
            model.add_edge("start", plan.steps[0].id)

        # Edges: step[i] → step[i+1]
        for i in range(len(plan.steps) - 1):
            model.add_edge(plan.steps[i].id, plan.steps[i + 1].id)

        # Last step → end
        if plan.steps:
            model.add_edge(plan.steps[-1].id, "end")
        else:
            model.add_edge("start", "end")

        return model


    # ------------------------------------------------------------------
    # ProcessModel-based execution
    # ------------------------------------------------------------------
    def _execute_with_process_model(self, plan: ResearchPlan, exec_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wraps the existing step execution logic inside a ProcessModel.
        If _debug_override_model is set, use it directly (for tests).
        Adds:
        - Debug trace logging for each step and transition
        - Optional DOT graph dump of the ProcessModel
        """

        import logging
        logger = logging.getLogger(__name__)

        # -----------------------------------------
        # TEST HOOK: allow injecting a custom model
        # -----------------------------------------
        if self._debug_override_model is not None:
            model = self._debug_override_model
            logger.debug("[DEBUG] Using debug override ProcessModel")
        else:
            model = self._build_model_from_plan(plan)
            logger.debug(f"[MODEL] Built ProcessModel: {model.name}")

        # -----------------------------------------
        # OPTIONAL: dump DOT graph for debugging
        # -----------------------------------------
        try:
            dot = model.to_dot()
            exec_ctx.setdefault("_debug", {})["process_model_dot"] = dot
            logger.debug("[MODEL] DOT graph generated for ProcessModel")
        except Exception as e:
            logger.warning(f"[MODEL] Failed to generate DOT graph: {e}")

        # -----------------------------
        # Repair-aware execution loop
        # -----------------------------
        attempts = 0
        while True:
            try:
                logger.debug("[RUNNER] Starting ProcessRunner")
                runner = ProcessRunner(model)

                # Add debug trace hook: ProcessRunner should emit step-level logs
                runner.run(exec_ctx)

                logger.debug("[RUNNER] ProcessRunner completed successfully")
                break

            except Exception as e:
                logger.exception(f"[ERROR] ProcessRunner failed: {e}")

                # No repair planner → re-raise immediately
                if self.repair_planner is None:
                    logger.debug("[REPAIR] No repair planner available → rethrowing")
                    raise

                attempts += 1
                max_attempts = getattr(self, "max_repair_attempts", 1)

                if attempts > max_attempts:
                    logger.debug(f"[REPAIR] Exceeded max repair attempts ({max_attempts}) → rethrowing")
                    raise

                failing_node_id = getattr(e, "node_id", "unknown")
                logger.debug(
                    f"[REPAIR] Attempt {attempts}/{max_attempts} repairing failing node: {failing_node_id}"
                )

                model = self.repair_planner.repair_process_model(
                    model=model,
                    failing_node_id=failing_node_id,
                    ctx=exec_ctx,
                    error=e,
                )

                logger.debug("[REPAIR] Repair planner produced updated ProcessModel")

        # -----------------------------------------
        # Finalize execution context
        # -----------------------------------------
        exec_ctx["final"] = exec_ctx["steps"][-1] if exec_ctx["steps"] else None
        logger.debug(f"[FINAL] Final step output: {exec_ctx['final']}")

        return exec_ctx
