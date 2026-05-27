# Introduction

This is the **CANONICAL** architecture diagram for Brain-24 (C1-C5 + Memory + Skills)

# The Architecture Diagram

```Mermaid
flowchart TB

    User((User)) --> Orchestrator

    subgraph Cortex["Cortex (Cognitive Layers C1–C5)"]
        C1["C1 — Immediate Cognition"]
        C2["C2 — Meta‑Cognition"]
        C3["C3 — Self‑Directed Cognition"]
        C4["C4 — Tool‑Augmented Cognition"]
        C5["C5 — Reflective Cognition"]
    end

    subgraph Organs["Organs (Non‑Cognitive Systems)"]
        Memory["Memory Organ<br/>Episodic • Semantic • Procedural"]
        Skills["Skills Organ<br/>Learned Skills • Skill Policies"]
        Tools["Tools Organ<br/>External APIs • System Tools"]
    end

    subgraph Control["Control Plane"]
        Router["Router<br/>Task Routing & Arbitration"]
        Orchestrator["Orchestrator<br/>Turn Loop & System Control"]
    end

    %% Control plane connections
    Orchestrator --> Router
    Router --> C1
    Router --> C2
    Router --> C3
    Router --> C4
    Router --> C5

    %% Cortex to Organs
    C2 --> Memory
    C3 --> Memory
    C4 --> Tools
    C2 --> Skills
    C3 --> Skills

    %% Organs to Cortex
    Memory --> C2
    Memory --> C3
    Skills --> C2
    Skills --> C3
    Tools --> C4

    %% Output
    C1 --> Orchestrator
    C2 --> Orchestrator
    C3 --> Orchestrator
    C4 --> Orchestrator
    C5 --> Orchestrator
```
# Interpretation (Concise and Canonical)

## Cortex (C1–C5)
These are the *only* cognitive layers:

- **C1 — immediate reasoning**
- **C2 — meta‑reasoning, planning, skill learning (Ch7)**
- **C3 — self‑directed cognition**
- **C4 — tool‑augmented cognition**
- **C5 — reflective cognition**

## Organs (Non‑Cognitive)
These are *not* C‑layers:

- **Memory — episodic, semantic, procedural**
- **Skills — learned skills, skill policies**
- **Tools — external APIs, system tools**

## Control Plane
- Router — routes tasks between Cortex and Organs
- Orchestrator — manages the turn loop and system control

# One Insight You’ll Appreciate
This diagram makes the architecture modular in the way your whole‑brain OS model demands:

- Cortex = cognition
- Organs = capabilities
- Control plane = coordination