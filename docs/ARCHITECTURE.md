# System Architecture & Multi-Agent Pipeline

CampusResolve AI implements a **Cooperative Multi-Agent Architecture** designed for automated student grievance intake, policy guidance, incident triage, and resolution execution.

```
                              [ Student / User ]
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        [ AI Support Chat ]                   [ Submit Grievance ]
                 │                                       │
                 ▼                                       ▼
     ┌──────────────────────┐               ┌────────────────────────┐
     │ Knowledge QA Agent   │               │   Classifier Agent     │
     │ (Module VI Ontology) │               │   (NLP + Entities)     │
     └──────────────────────┘               └───────────┬────────────┘
                                                        │
                                                        ▼
                                            ┌────────────────────────┐
                                            │ Forward Chaining Rules │
                                            │ (Module V & VI Logic)  │
                                            └───────────┬────────────┘
                                                        │
                                ┌───────────────────────┴───────────────────────┐
                                ▼                                               ▼
                    ┌────────────────────────┐                      ┌────────────────────────┐
                    │  Bayesian Uncertainty  │                      │   Duplicate Detector   │
                    │  (Module VIII Escal.)  │                      │   (TF-IDF Clustering)  │
                    └───────────┬────────────┘                      └───────────┬────────────┘
                                │                                               │
                                └───────────────────────┬───────────────────────┘
                                                        │
                                                        ▼
                                            ┌────────────────────────┐
                                            │   A* Planning Agent    │
                                            │ (Module III & VII Plan)│
                                            └───────────┬────────────┘
                                                        │
                                                        ▼
                                            ┌────────────────────────┐
                                            │  Communication Agent   │
                                            │  (Empathetic Response) │
                                            └───────────┬────────────┘
                                                        │
                                                        ▼
                                            ┌────────────────────────┐
                                            │ SQLite Persistence DB  │
                                            │ & Admin Triage Console │
                                            └────────────────────────┘
```

---

## 1. Agent Roles & Specifications

### A. Intake & Classifier Agent
- **Purpose**: Parses unstructured free-text complaints, identifies problem domain, extracts campus entities, and evaluates sentiment distress.
- **Methods**:
  - Regular expression tokenizers for Room Numbers, Hostel Blocks, Student Roll Numbers, Phone Numbers, and Payment UTR Codes.
  - TF-IDF Vector Space classification combined with category keyword density scoring.
  - Sentiment polarity lexicon scoring (range $[-1.0, +1.0]$).

### B. Knowledge Inference Engine
- **Purpose**: Acts as an institutional expert reasoning agent, firing rules encoded from college ordinances, UGC regulations, and academic manuals.
- **Methods**:
  - Pure Forward Chaining algorithm with Modus Ponens deduction.
  - Derives mandatory escalation flags (e.g., alert Chief Proctor within 2 hours for ragging, alert Health Inspector within 4 hours for mess hygiene).
  - Supplies verified campus policy references to students.

### C. Bayesian Urgency & Escalation Estimator
- **Purpose**: Handles uncertainty in student inputs by estimating the probabilistic risk of complaint escalation if left unattended.
- **Methods**:
  - Bayesian Network with conditional likelihoods for sentiment distress, urgent cues, time deadlines, and recurrence.
  - Computes posterior $P(\text{Escalation} \mid \text{Evidence})$.
  - Maps posterior score to institutional priorities: Low, Medium, High, Emergency.

### D. Duplicate Detection & Clustering Agent
- **Purpose**: Identifies systemic campus failures (e.g. WiFi outage in an entire hostel block, water line break) by grouping semantically related active tickets.
- **Methods**:
  - Cosine similarity over TF-IDF vectors of active tickets.
  - Groups tickets with similarity $\ge 0.58$ into a shared `cluster_id`.
  - Promotes the initial ticket as "Master Incident", linking child tickets to eliminate duplicate staff dispatches.

### E. A* State-Space Planning Agent
- **Purpose**: Synthesizes an optimal, step-by-step resolution workflow based on institutional action operators.
- **Methods**:
  - STRIPS-like operators (`VerifyGrievance`, `DispatchSpecialist`, `ProcureReplacementEquipment`, `ExecuteCorrectiveAction`, `ConductSupervisoryAudit`, `NotifyStudentAndCloseTicket`).
  - A* search using priority queue ordered by $f(n) = g(n) + h(n)$.
  - Admissible heuristic function $h(n)$ guaranteeing cost-optimal resolution plans.

### F. Communication Agent
- **Purpose**: Formulates clear, reassuring notifications to students and actionable task briefs to staff.
- **Methods**:
  - Transparent disclosure of AI triage decisions, assigned department, SLA timeline, and legal/policy citations.
  - Graceful fallback: Built-in deterministic generation engine ensures full functionality 100% offline without external API keys, with optional plug-and-play LLM hooks.

---

## 2. Database Schema

The SQLite persistence layer (`backend/database.py`) maintains:
- `tickets`: Complete state history, student details, classified category, Bayesian urgency score, A* resolution plan (stored as JSON), triggered rules, and student feedback.
- `agent_audit_logs`: Detailed step-by-step execution log of all agent decisions (sensors, inputs, inference, outputs) for academic inspection and administrative accountability.

---
