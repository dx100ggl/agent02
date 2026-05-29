# Unified Control Plane — Router + Orchestrator  
Zoomed‑In Subsystem Poster

The Control Plane coordinates **all cognitive activity** in Brain‑24.  
It consists of:

- **Router** — decides *where* a task goes  
- **Orchestrator** — decides *how* a task unfolds over time  

Together, they form the execution backbone of the Cortex.

---

## 1. Unified Control Plane Diagram

```mermaid
flowchart TB

subgraph Router["Router"]
    Classifier["Task Classifier"]
    Core["Routing Core"]
    Escalations["Escalation Handler"]
end

subgraph Orch["Orchestrator"]
    Engine["Workflow Engine"]
    State["State Manager"]
    Resolver["Dependency Resolver"]
end

C1["C1"]
C2["C2"]
C3["C3"]
C4["C4"]
Skills["Skills Organ"]
Memory["Memory Organ"]

Classifier --> Core
Core --> C1
Core --> C2
Core --> C3
Core --> C4
Core --> Orch

Engine --> C2
Engine --> C4
Engine --> Skills
Engine --> Memory
```

---

## 2. Responsibilities

### **Router**
- Task classification  
- Routing to C1/C2/C3/C4  
- Escalation handling  

### **Orchestrator**
- Multi‑step workflow execution  
- State tracking  
- Skill + tool orchestration  
- Error recovery  

---

## 3. Interactions

### **Router → Orchestrator**
- Sends tasks requiring multi‑step execution  

### **Orchestrator → Cortex**
- Executes plans across C1–C5  

### **Control Plane → Memory**
- Logs traces  

### **Control Plane → Skills**
- Executes skill steps  

### **Control Plane → C4**
- Executes tool steps  

---

## 4. Related Documents
- Router Poster  
- Orchestrator Poster  
- C1/C2/C3/C4 Posters  
