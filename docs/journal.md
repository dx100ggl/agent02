# Introduction

This is a new start for C4 of the Brain, which is the ultimate of a single agent.

## Stage views
### Stage 0 — Cortex‑only (LLM wrapper)

A simple loop: user → LLM → reply.
No planning, no tools, no memory, no meta‑cognition.

### Stage 1 — C1 Skeleton (router → planner → executor)

The brain can structure a turn, but still behaves like a single LLM.
Tools exist but aren’t used.
Planner and executor are wired but not yet “alive”.

### Stage 2 — C2‑P0/P1/P2 (meta‑cognition over the loop)

The brain can:
- monitor
- evaluate
- warn
- halt
- annotate
- adjust

But it still doesn’t act in the world.
It’s a self‑aware LLM loop.

### Stage 3 — C1‑Tools (actual planning + tool execution)

The brain can:
- decide to use a tool
- generate tool steps
- execute tools deterministically
- integrate tool results into reasoning
- produce multi‑step plans

This is where the system becomes an agent, not a chatbot.

### Stage 4 — Memory (episodic + semantic + vector)

The brain can:
- store experiences
- retrieve relevant past info
- update long‑term knowledge
- use memory in planning

This is where the system becomes stateful and learning.

### Stage 5 — Multi‑agent coordination

Planner can spawn sub‑agents.
Agents can collaborate, delegate, and coordinate.
This is the “whole‑brain OS” fully realized.
Examples: Hermes, Karpathy, skills, personas.

## Coginition (C) view


| Level | Description | Key Capabilities | Outputs |
|-------|-------------|------------------|---------|
| **C0** | LLM Engine | talk to LM Studio | NA |
| **C1** | Direct LLM Mode |  | |
| **C2** | Router → Planner → Executor → Synthesizer|  |  |
| **C3** | Memory, short-n-long term|  |  |
| **C4** | Tools| File ops, web search, code execution, etc.  |  |
| **C5** | Multi-agent| Planner can spawn subagents  |  |
---


## P Level

It is about the capabilitis of a C layer (C2 development).

| Level | Description | Key Capabilities | Outputs |
|-------|-------------|------------------|---------|
| **P0** | Reactive | Observe, log | Observation, basic evaluation |
| **P1** | Adaptive | Evaluate, intervene, update memory | Directive, memory update, basic strategy |
| **P2** | Strategic | Predict, optimize, enforce alignment | Full C2Turn, advanced strategy |

# Development tracker

## Adaptive Planner v2 (branching, retries, escalation)

3 steps to take

| Step | File | Why |
| --- | --- | --- |
| 1 | ``brain/planner/adaptive_planner.py`` | Planner v2 logic |
| **2** | ``brain/orchestrator.py`` | Record retries + errors |
| 3 | (optional) tests | Validate retry/escalation |

- a dynamic router
- an adaptive planner with retries + escalation
- a working orchestrator
- a functioning tool system
- a memory subsystem
- and a full test suite proving all of it

## Dynamic Router v2 (confidence‑based)
🧠 Orchestrator v2 — Multi‑Step Cognitive Loop (Depth, Success, Termination)




2.  Memory Retrieval v2 (vector search)
3.  Tool System v2 (real tools)
4.  Integration tests for all of the above