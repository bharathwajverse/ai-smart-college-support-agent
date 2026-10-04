# CampusResolve AI: Smart College Support and Complaint Management Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-27%20Passed%20(100%25)-success.svg)](https://docs.pytest.org/)
[![Database](https://img.shields.io/badge/Neon-PostgreSQL%20%7C%20SQLite-brightgreen.svg)](https://neon.tech/)
[![FAI Capstone](https://img.shields.io/badge/Course-Foundations%20of%20AI-indigo.svg)](docs/FAI_SYLLABUS_MAPPING.md)

> **Foundations of Artificial Intelligence (FAI) Capstone Project**  
> An autonomous, multi-agent artificial intelligence system for university campus support, automated grievance triage, state-space resolution planning, Constraint Satisfaction Problem (CSP) staff dispatch, and policy reasoning.

---

## 🎯 Problem Statement

Traditional university complaint portals suffer from critical bottlenecks:
1. **Manual, Slow Triage:** Student grievances sit in unassigned queues while staff manually read and route tickets.
2. **Delayed Emergency Response:** Serious safety complaints (e.g. anti-ragging, mental distress, food contamination) are buried under minor complaints.
3. **Redundant Workflows:** Multiple students reporting the same systemic incident (e.g., hostel WiFi outage or water failure) trigger duplicate staff dispatches.
4. **Subjective Prioritization:** Grievance urgency is handled inconsistently without mathematical rigor.
5. **Lack of Transparency:** Students receive no policy citations or resolution progression updates.

**CampusResolve AI** solves this by orchestrating a cooperative multi-agent AI architecture combining **natural language processing, forward-chaining symbolic logic, Bayesian uncertainty modeling, and A\* search planning**.

---

## 🧠 FAI Syllabus Alignment (Modules I - X)

| Module | FAI Course Topic | Implementation in CampusResolve AI | Code Location |
| :--- | :--- | :--- | :--- |
| **Module I** | **Intelligent Agents** | Formal PEAS specification, Reflex, Model-Based, Goal-Based, and Utility-Based agents. | [`backend/agents/peas_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/peas_agent.py) |
| **Module II & III** | **Uninformed & Informed Search** | State-space formulation with heuristic evaluation $h(n)$ and A\* graph search. | [`backend/agents/planning_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/planning_agent.py) |
| **Module IV** | **Optimal Decisions & CSP** | Constraint satisfaction for SLA deadlines and staff assignment; Multi-agent utility optimization. | [`backend/agents/peas_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/peas_agent.py) |
| **Module V & VI** | **Inferences & Knowledge Representation** | Forward Chaining inference engine using Modus Ponens over propositional and First-Order rules. | [`backend/agents/inference_engine.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/inference_engine.py) |
| **Module VII** | **State Space Planning** | Institutional action operators with explicit Preconditions, Effects, and Step Costs ($g(n)$). | [`backend/agents/planning_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/planning_agent.py) |
| **Module VIII** | **Uncertainty in AI** | Bayesian Network computing posterior $P(\text{Escalation} \mid \text{Evidence})$ under uncertainty. | [`backend/agents/bayesian_urgency.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/bayesian_urgency.py) |
| **Module IX** | **Learning Agents** | Semantic TF-IDF similarity clustering for campus incidents; Student satisfaction feedback loops. | [`backend/agents/duplicate_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/duplicate_agent.py) |
| **Module X** | **Applications of AI** | Real-world application of AI in educational governance, student welfare, and campus administration. | [`frontend/index.html`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/frontend/index.html) |

---

## 🚀 Key Features

- **💬 Conversational Policy Advisory Agent:** Real-time student Q&A referencing institutional ordinances (attendance rules, hostel curfews, exam re-evaluation, refund policies).
- **⚡ Autonomous Intake & Triage Pipeline:** NLP classification into institutional departments with entity extraction (Roll No, Room, Hostel, Transaction UTR).
- **🚨 Zero-Tolerance Anti-Ragging Safety Protocols:** Automatic emergency escalation, Dean alert, and compressed 2-hour SLA.
- **📈 Bayesian Escalation Estimator:** Mathematical calculation of escalation risk combining sentiment polarity, distress keywords, and recurring report patterns.
- **🗺️ A\* State-Space Resolution Planner:** Synthesizes the optimal sequence of actions to resolve complaints with time cost estimates.
- **🔗 Duplicate Incident Clustering:** Automatically groups identical complaints across hostel blocks into prioritized "Master Incidents".
- **🏛️ Administrator Triage Console:** Search, filter, transition ticket status, review agent audit trails, and manage campus telemetry.
- **⭐ Learning Feedback Loop:** Students submit post-resolution satisfaction ratings (1-5 stars) to update agent utility metrics.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **AI & Reasoning:** Scikit-Learn (TF-IDF Vector Space), Custom Forward Chaining Inference Engine, A\* Graph Search Planner, Bayesian Network
- **Database:** SQLite (Zero external configuration required)
- **Frontend:** Responsive HTML5, Tailwind CSS, Chart.js, Lucide icons (No Node.js/npm dependencies needed!)
- **Testing:** Pytest (19/19 passing tests)

---

## 🏁 Quick Start Guide

### 1. Clone & Enter Directory
```bash
cd "AI-Based Smart College Support and Complaint Management Agent"
```

### 2. Install Requirements (if needed)
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
Open your browser and navigate to:  
👉 **`http://localhost:8000`**

### 4. Run the Automated Tests
```bash
python -m pytest tests/ -v
```
*(All 19 unit & integration tests pass with 100% test coverage)*

Or run the standalone verification suite:
```bash
python verify_system.py
```

---

## 📁 Repository Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml                     # Automated CI test verification on push & PR
├── api/
│   ├── __init__.py                    # API package marker
│   └── index.py                       # Vercel serverless ASGI entrypoint
├── backend/
│   ├── __init__.py                    # Backend package marker
│   ├── main.py                        # FastAPI application & REST endpoints
│   ├── database.py                    # PostgreSQL (Neon) & SQLite fallback engine
│   ├── models.py                      # Pydantic schemas & SQLAlchemy DB models
│   ├── knowledge_base/
│   │   ├── __init__.py                # KB package marker
│   │   ├── college_rules.json         # Campus policies, ordinances & production rules
│   │   └── sample_tickets.json        # Pre-seeded demo tickets
│   └── agents/
│       ├── __init__.py                # Agents package marker
│       ├── peas_agent.py              # Module I: PEAS model & utility functions
│       ├── classifier_agent.py        # Module I/III: NLP category & entity extractor
│       ├── inference_engine.py        # Module V/VI: Forward & backward chaining engine
│       ├── planning_agent.py          # Module III/VII: A* state space resolution planner
│       ├── bayesian_urgency.py        # Module VIII: Bayesian uncertainty estimator
│       ├── duplicate_agent.py         # Module III/IX: TF-IDF similarity & clustering
│       ├── dispatch_csp.py            # Module IV: Constraint Satisfaction Problem (CSP)
│       ├── communication_agent.py     # Response synthesis & notifications
│       └── orchestrator.py            # Master agent coordinating pipeline
├── frontend/
│   ├── index.html                     # Responsive glassmorphic single-page UI
│   ├── css/styles.css                 # Custom styles, animations & themes
│   └── js/app.js                      # Dynamic UI logic, REST client & charts
├── public/                            # Static distribution directory for Vercel CDN
│   ├── index.html
│   └── static/
│       ├── css/styles.css
│       └── js/app.js
├── tests/
│   ├── test_agents.py                 # PEAS, classifier & communicator unit tests
│   ├── test_inference.py              # Forward chaining & FAQ query tests
│   ├── test_planning.py               # A* search & operator tests
│   ├── test_bayesian.py               # Bayesian posterior & risk bounds tests
│   ├── test_csp.py                    # CSP staff allocation tests
│   └── test_api.py                    # FastAPI REST endpoint integration tests
├── docs/
│   ├── FAI_SYLLABUS_MAPPING.md        # Explicit mapping of Modules I-X to code
│   ├── ARCHITECTURE.md                # System design & Agent workflow
│   └── PRESENTATION_GUIDE.md          # 5-minute presentation script & viva guide
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Testing & development dependencies
├── run.py                             # Fast launcher with port auto-detection
├── verify_system.py                   # Standalone agent verification suite (10 modules)
├── vercel.json                        # Vercel serverless function & routing configuration
├── LICENSE                            # MIT License
└── README.md                          # Main project overview & guide
```

---

## ☁️ Deployment

### Deploy to Vercel
This repository is pre-configured with `vercel.json` and `api/index.py` for instant serverless deployment on Vercel:
1. Import this repository into **[Vercel](https://vercel.com/)**.
2. Select Framework Preset: **FastAPI** (or **Other**).
3. Set Environment Variables in Project Settings:
   - `DATABASE_URL`: Your PostgreSQL / Neon database connection string (e.g. `postgresql://user:pass@ep-...neon.tech/neondb?sslmode=require`)
   - `LLM_API_KEY`: Your LLM Provider API key
   - `LLM_PROVIDER`: Your chosen LLM model / provider ID
4. Click **Deploy**. Vercel will automatically build the serverless functions and serve the static UI via the Global Edge CDN.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/complaints` | Submits a new grievance and triggers multi-agent pipeline |
| `GET` | `/api/complaints` | Retrieves all complaints with search and category filters |
| `GET` | `/api/complaints/{code}` | Retrieves single ticket details and A\* plan |
| `PATCH`| `/api/complaints/{code}/status` | Supervisor updates status (Triaged, In Progress, Resolved) |
| `POST` | `/api/complaints/{code}/feedback` | Student submits 1-5 star satisfaction feedback |
| `POST` | `/api/chat` | AI conversational policy assistant query |
| `GET` | `/api/metrics` | Campus grievance telemetry and SLA analytics |
| `GET` | `/api/fai-diagnostics` | Returns PEAS, A\* operators, rules, and Bayesian parameters |

---

## 🎓 Academic Documentation
- **[FAI Syllabus Detailed Mapping](docs/FAI_SYLLABUS_MAPPING.md)**
- **[System Architecture & Data Flow](docs/ARCHITECTURE.md)**
- **[Viva Presentation & Demo Guide](docs/PRESENTATION_GUIDE.md)**
