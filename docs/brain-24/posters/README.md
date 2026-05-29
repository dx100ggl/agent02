# Brain‑24 Posters Directory  
Master Index of All Architecture Posters (18 Total)

This directory contains the complete set of zoomed‑in, cross‑organ, and control‑plane posters for the Brain‑24 architecture.  
Each poster is a standalone subsystem reference, and together they form the full documentation of the Brain‑24 cognitive and learning stack.

---

## 1. Directory Structure

```mermaid
flowchart TB

subgraph Posters["Brain‑24 Posters Directory"]
end

subgraph Cortex["Cortex (C1–C5)"]
    C1["C1 — Immediate Cognition"]
    C2["C2 — Meta‑Cognition"]
    C3["C3 — Self‑Directed Cognition"]
    C4["C4 — Tool‑Augmented Cognition"]
    C5["C5 — Reflective Cognition"]
end

subgraph Memory["Memory Organ"]
    Episodic["Episodic Memory"]
    Semantic["Semantic Memory"]
    Procedural["Procedural Memory"]
    CrossMemory["Cross‑Memory"]
end

subgraph Skills["Skills Organ"]
    SkillsOrgan["Skills Organ"]
    SkillEval["Skill Evaluation & Confidence Updating"]
end

subgraph Consolidation["Consolidation Engine"]
    ConsolidationPoster["Consolidation Engine"]
end

subgraph ControlPlane["Control Plane"]
    Router["Router"]
    Orchestrator["Orchestrator"]
    UnifiedCP["Unified Control Plane"]
end

subgraph CrossOrgan["Cross‑Organ Learning"]
    C2SkillsMemory["C2 ↔ Skills ↔ Memory"]
    MemorySkillsC2Con["Memory ↔ Skills ↔ C2 ↔ Consolidation"]
    LearningStack["Unified Learning Stack (C2 ↔ Skills ↔ Memory ↔ Consolidation ↔ C5)"]
end

Posters --> Cortex
Posters --> Memory
Posters --> Skills
Posters --> Consolidation
Posters --> ControlPlane
Posters --> CrossOrgan
```

---

## 2. Poster Groups

### **Cortex (C1–C5)**
- C1 — Immediate Cognition  
- C2 — Meta‑Cognition + Skill Learning  
- C3 — Self‑Directed Cognition  
- C4 — Tool‑Augmented Cognition  
- C5 — Reflective Cognition  

### **Memory Organ**
- Episodic Memory  
- Semantic Memory  
- Procedural Memory  
- Cross‑Memory  

### **Skills Organ**
- Skills Organ  
- Skill Evaluation & Confidence Updating  

### **Consolidation**
- Consolidation Engine  

### **Control Plane**
- Router  
- Orchestrator  
- Unified Control Plane  

### **Cross‑Organ Learning**
- C2 ↔ Skills ↔ Memory  
- Memory ↔ Skills ↔ C2 ↔ Consolidation  
- Unified Learning Stack (C2 ↔ Skills ↔ Memory ↔ Consolidation ↔ C5)
