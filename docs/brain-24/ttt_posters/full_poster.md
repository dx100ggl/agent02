# Brain‑24 Full Poster

This poster unifies all subsystems of the Brain‑24 architecture on a single page.  
It shows the cognitive layers (C1–C5), organs (Memory, Skills, Tools), and control plane (Router, Orchestrator).

---

## 1. Poster Diagram

```mermaid
flowchart TB

    %% ============================
    %% CONTROL PLANE
    %% ============================
    subgraph Control["Control Plane"]
        Router["Router<br/>Task Routing & Arbitration"]
        Orchestrator["Orchestrator<br/>Turn Loop & System Control"]
    end

    User((User)) --> Orchestrator
    Orchestrator --> Router

    %% ============================
    %% CORTEX (C1–C5)
    %% ============================
    subgraph Cortex["Cortex (Cognitive Layers C1–C5)"]
        C1["C1 — Immediate Reasoning"]
        C2["C2 — Meta‑Reasoning, Planning, Skill Learning (Ch7)"]
        C3["C3 — Self‑Directed Cognition"]
        C4["C4 — Tool‑Augmented Cognition"]
        C5["C5 — Reflective Cognition"]
    end

    Router --> C1
    Router --> C2
    Router --> C3
    Router --> C4
    Router --> C5

    %% ============================
    %% ORGANS (Non‑Cognitive)
    %% ============================
    subgraph Organs["Organs (Non‑Cognitive Systems)"]
        Memory["Memory Organ<br/>Episodic • Semantic • Procedural"]
        Skills["Skills Organ<br/>Learned Skills • Skill Policies"]
        Tools["Tools Organ<br/>External APIs • System Tools"]
    end

    %% Cortex to Organs
    C2 --> Memory
    C3 --> Memory
    C2 --> Skills
    C3 --> Skills
    C4 --> Tools

    %% Organs to Cortex
    Memory --> C2
    Memory --> C3
    Skills --> C2
    Skills --> C3
    Tools --> C4

    %% Output back to orchestrator
    C1 --> Orchestrator
    C2 --> Orchestrator
    C3 --> Orchestrator
    C4 --> Orchestrator
    C5 --> Orchestrator
```

---

## 2. Poster Overview

The Brain‑24 poster integrates three architectural views:

### **1. Cognitive Layers (Cortex)**
The five layers of cognition:
- **C1 — Immediate reasoning**
- **C2 — Meta‑reasoning, planning, skill learning (Ch7)**
- **C3 — Self‑directed cognition**
- **C4 — Tool‑augmented cognition**
- **C5 — Reflective cognition**

### **2. Organs (Non‑Cognitive Systems)**
Separate from the Cortex:
- **Memory** — episodic, semantic, procedural  
- **Skills** — learned skills, skill policies  
- **Tools** — external APIs, system tools  

### **3. Control Plane**
Coordinates cognition and organs:
- **Router** — task routing and arbitration  
- **Orchestrator** — turn loop and system control  

---

## 3. Purpose

This poster provides a unified view of Brain‑24:
- Shows how cognition (C1–C5) interacts with organs and control systems  
- Serves as the canonical reference for architecture discussions  
- Acts as the “front page” of the Brain‑24 documentation set  

---

## 4. Related Documents

- **Overview** — `00-overview/brain-24-overview.md`  
- **Director Tree** — `00-overview/brain-24-director-tree.md`  
- **Core Loop** — `01-runtime/brain-24-core-loop.md`  
- **Component Map** — `02-architecture/brain-24-component-map.md`  
- **Deployment Diagram** — `02-architecture/brain-24-deployment-diagram.md`  
- **Type System** — `03-types/brain-24-type-system.md`  
- **Skill Learning (Ch7)** — `docs/brain-24/Ch7/`  
- **Architecture Evolution** — `brain-24-architecture-evolution-A0-A4.md`
