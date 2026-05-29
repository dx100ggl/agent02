# Brain‑24 Master Index Poster  
(Visual Map of All 18 Posters)

This master index shows the full poster set for the Brain‑24 architecture.  
It organizes all 18 posters into five major groups:

- **Cortex (C1–C5)**  
- **Memory Organ (Episodic, Semantic, Procedural, Cross‑Memory)**  
- **Skills Organ (Skills + Skill Evaluation)**  
- **Consolidation Engine**  
- **Control Plane (Router + Orchestrator + Unified)**  
- **Cross‑Organ Posters (Learning Loop)**  

This index is the top‑level map for navigating the entire documentation set.

---

## 1. Master Index Diagram

```mermaid
flowchart TB

%% ============================
%% MASTER INDEX ROOT
%% ============================
subgraph Brain24["Brain‑24 Poster Index"]
end

%% ============================
%% CORTEX
%% ============================
subgraph Cortex["Cortex (C1–C5)"]
    C1["C1 — Immediate Cognition"]
    C2["C2 — Meta‑Cognition + Skill Learning"]
    C3["C3 — Self‑Directed Cognition"]
    C4["C4 — Tool‑Augmented Cognition"]
    C5["C5 — Reflective Cognition"]
end

%% ============================
%% MEMORY ORGAN
%% ============================
subgraph Memory["Memory Organ"]
    Episodic["Episodic Memory"]
    Semantic["Semantic Memory"]
    Procedural["Procedural Memory"]
    CrossMemory["Cross‑Memory Poster"]
end

%% ============================
%% SKILLS ORGAN
%% ============================
subgraph Skills["Skills Organ"]
    SkillsOrgan["Skills Organ"]
    SkillEval["Skill Evaluation & Confidence Updating"]
end

%% ============================
%% CONSOLIDATION
%% ============================
subgraph Consolidation["Consolidation Engine"]
    ConsolidationPoster["Consolidation Engine Poster"]
end

%% ============================
%% CONTROL PLANE
%% ============================
subgraph ControlPlane["Control Plane"]
    Router["Router"]
    Orchestrator["Orchestrator"]
    UnifiedCP["Unified Control Plane"]
end

%% ============================
%% CROSS-ORGAN LEARNING
%% ============================
subgraph CrossOrgan["Cross‑Organ Learning Posters"]
    C2SkillsMemory["C2 ↔ Skills ↔ Memory"]
    MemorySkillsC2Con["Memory ↔ Skills ↔ C2 ↔ Consolidation"]
    LearningStack["Unified Learning Stack (C2 ↔ Skills ↔ Memory ↔ Consolidation ↔ C5)"]
end

%% ============================
%% CONNECTIONS
%% ============================

Brain24 --> Cortex
Brain24 --> Memory
Brain24 --> Skills
Brain24 --> Consolidation
Brain24 --> ControlPlane
Brain24 --> CrossOrgan

%% Cortex relationships
C2 --> C5
C2 --> SkillsOrgan
C2 --> Memory

%% Memory relationships
Episodic --> Semantic
Semantic --> Procedural
Procedural --> Episodic

%% Skills relationships
SkillsOrgan --> SkillEval
SkillEval --> Procedural

%% Consolidation relationships
ConsolidationPoster --> Episodic
ConsolidationPoster --> Semantic
ConsolidationPoster --> Procedural
ConsolidationPoster --> SkillEval

%% Control Plane relationships
Router --> Orchestrator
Orchestrator --> C2
Orchestrator --> SkillsOrgan
Orchestrator --> Memory

%% Cross-organ relationships
C2SkillsMemory --> C2
C2SkillsMemory --> SkillsOrgan
C2SkillsMemory --> Memory

MemorySkillsC2Con --> ConsolidationPoster
MemorySkillsC2Con --> C2SkillsMemory

LearningStack --> C5
LearningStack --> MemorySkillsC2Con
```

---

## 2. Poster Groups

### **A. Cortex Posters**
1. C1 — Immediate Cognition  
2. C2 — Meta‑Cognition + Skill Learning  
3. C3 — Self‑Directed Cognition  
4. C4 — Tool‑Augmented Cognition  
5. C5 — Reflective Cognition  

---

### **B. Memory Organ Posters**
6. Episodic Memory  
7. Semantic Memory  
8. Procedural Memory  
9. Cross‑Memory (Episodic ↔ Semantic ↔ Procedural)  

---

### **C. Skills Organ Posters**
10. Skills Organ  
11. Skill Evaluation & Confidence Updating  

---

### **D. Consolidation Posters**
12. Consolidation Engine  

---

### **E. Control Plane Posters**
13. Router  
14. Orchestrator  
15. Unified Control Plane (Router + Orchestrator)  

---

### **F. Cross‑Organ Learning Posters**
16. C2 ↔ Skills ↔ Memory  
17. Memory ↔ Skills ↔ C2 ↔ Consolidation  
18. Unified Learning Stack (C2 ↔ Skills ↔ Memory ↔ Consolidation ↔ C5)  

---

## 3. Purpose of This Poster

This master index helps you:

- Navigate the entire Brain‑24 poster library  
- Understand how each subsystem fits into the architecture  
- Maintain a clean, scalable documentation structure  
- Quickly locate any zoomed‑in or cross‑organ poster  

---

## 4. Related Documents

- `brain-24-learning-stack-unified-poster.md`  
- `brain-24-cross-memory-poster.md`  
- `brain-24-consolidation-engine-poster.md`  
- `brain-24-C2-subsystem-poster.md`  
- `brain-24-C5-reflective-cognition-poster.md`  
