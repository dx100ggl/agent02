# Brain‑24 Documentation  
Architecture • Cognition • Memory • Skills • Control Plane

Brain‑24 is a modular, whole‑brain cognitive architecture designed around five major cortical subsystems (C1–C5), a multi‑organ memory system, a skills organ, a consolidation engine, and a unified control plane.  
This documentation directory contains the complete technical and conceptual reference for the Brain‑24 system.

---

# 1. What This Directory Contains

This folder (`docs/brain-24/`) is the **root** of all Brain‑24 documentation.  
It includes:

- **High‑level architecture overviews**
- **Subsystem posters (18 total)**
- **Cross‑organ learning diagrams**
- **Control plane documentation**
- **Memory, skills, and consolidation internals**
- **Navigation files (`SUMMARY.md`, poster index)**

If you are new to Brain‑24, start with the **Master Index Poster** and the **Unified Learning Stack**.

---

# 2. Navigation

## 📘 Summary (Table of Contents)
See:  
[`SUMMARY.md`](SUMMARY.md)

This file provides a GitBook‑style navigation tree for the entire Brain‑24 documentation set.

---

## 🖼 Posters (Subsystem Reference Sheets)
All subsystem posters live under:
```code
posters/
```

Each poster includes:
- Overview  
- Responsibilities  
- Internal components  
- Cross‑organ interactions  
- Mermaid diagram  

See the posters README for details:  
[`posters/README.md`](posters/README.md)

---

# 3. Poster Categories (18 Total)

### 🧠 Cortex (C1–C5)
- Immediate Cognition  
- Meta‑Cognition + Skill Learning  
- Self‑Directed Cognition  
- Tool‑Augmented Cognition  
- Reflective Cognition  

### 🧩 Memory Organ
- Episodic  
- Semantic  
- Procedural  
- Cross‑Memory  

### 🛠 Skills Organ
- Skills Organ  
- Skill Evaluation & Confidence Updating  

### 🔄 Consolidation Engine
- Consolidation Engine Poster  

### 🧭 Control Plane
- Router  
- Orchestrator  
- Unified Control Plane  

### 🔗 Cross‑Organ Learning
- C2 ↔ Skills ↔ Memory  
- Memory ↔ Skills ↔ C2 ↔ Consolidation  
- Unified Learning Stack (C2 ↔ Skills ↔ Memory ↔ Consolidation ↔ C5)

---

# 4. Recommended Reading Order

If you want to understand Brain‑24 from the ground up:

1. **Cortex:** C1 → C2 → C3 → C4 → C5  
2. **Memory Organ:** Episodic → Semantic → Procedural → Cross‑Memory  
3. **Skills Organ:** Skills Organ → Skill Evaluation  
4. **Consolidation Engine**  
5. **Control Plane:** Router → Orchestrator → Unified  
6. **Unified Learning Stack** (the full adaptive loop)

---

# 5. Master Index Poster

The complete visual map of all 18 posters is here:

[`posters/brain-24-master-index-poster.md`](posters/brain-24-master-index-poster.md)

This is the best starting point for navigating the entire architecture.

---

# 6. Contributing

To add new documentation:

1. Create a new folder under the appropriate subsystem  
2. Add a `*.md` file following the poster structure  
3. Update `SUMMARY.md` and the posters README if needed  

Brain‑24 documentation is designed to be modular, scalable, and easy to extend.

---

This directory is the authoritative reference for the Brain‑24 architecture.
