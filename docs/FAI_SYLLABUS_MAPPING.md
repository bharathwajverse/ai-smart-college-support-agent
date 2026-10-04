# Foundations of Artificial Intelligence (FAI) Syllabus Mapping

This document provides an explicit academic mapping between each module of the **FAI (Foundations of Artificial Intelligence)** course curriculum and the concrete algorithms, data structures, and code files implemented in **CampusResolve AI**.

---

## Curriculum vs. Implementation Matrix

| FAI Module | Course Topic | CampusResolve AI Implementation | Source File / Symbol |
| :--- | :--- | :--- | :--- |
| **Module I** | **Intelligent Agents** (PEAS, Agent Types, Ethics) | Formal PEAS specification, Reflex vs Model-Based vs Goal-Based vs Utility-Based Agents. | [`backend/agents/peas_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/peas_agent.py) (`PEASModel`, `calculate_agent_utility`) |
| **Module II** | **Uninformed Search Strategies** (Uniform Cost Search, BFS, Node Expansions) | Uniform Cost Search (UCS) minimizing cumulative step cost $f(n)=g(n)$ without heuristic bias. | [`backend/agents/planning_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/planning_agent.py) (`search_with_telemetry(..., search_mode="ucs")`) |
| **Module III** | **Informed Search Strategies** (Heuristics, A* Search, Pruning) | Admissible heuristic $h(n)$ evaluation, A* Graph Search finding provably optimal resolution sequence. | [`backend/agents/planning_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/planning_agent.py) (`StateSpacePlanningAgent`, `_heuristic`) |
| **Module IV** | **Optimal Decisions & Constraint Satisfaction (CSPs)** | Formal CSP Formulation, Backtracking Search, MRV (Minimum Remaining Values), Degree Heuristic, LCV, and Forward Checking for staff dispatch. | [`backend/agents/dispatch_csp.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/dispatch_csp.py) (`GrievanceCSP`, `solve`, `forward_check`) |
| **Module V** | **Inferences & Logic** (Propositional / FOL, Forward & Backward Chaining) | Forward chaining production rule engine (Modus Ponens) and Goal-Driven Backward Chaining proof tree. | [`backend/agents/inference_engine.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/inference_engine.py) (`forward_chain`, `backward_chain`) |
| **Module VI** | **Knowledge Representation & Reasoning** (Ontologies, Semantics, KB Agent) | Campus entity ontology (Departments, Facilities, Hostels, Regulations), Ontological FAQ Knowledge Base. | [`backend/knowledge_base/college_rules.json`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/knowledge_base/college_rules.json) |
| **Module VII** | **State Space Planning** (STRIPS-style Operators, Partial Order, Heuristics) | Institutional action operators with explicit Preconditions, Effects, and Step Costs ($g(n)$). | [`backend/agents/planning_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/planning_agent.py) (`PlanningAction`) |
| **Module VIII** | **Uncertainty in AI** (Bayesian Networks, Conditional Probability, Priors) | Bayesian Escalation Risk Estimator calculating posterior $P(\text{Escalation} \mid \text{Evidence})$ given sentiment distress, lexical cues, and recurrence. | [`backend/agents/bayesian_urgency.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/bayesian_urgency.py) (`BayesianUrgencyEstimator`) |
| **Module IX** | **Learning Agents** (Feedback Loops, Clustering, Instance-Based) | Semantic TF-IDF similarity clustering for recurring campus incidents; Post-resolution student satisfaction feedback loops. | [`backend/agents/duplicate_agent.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/agents/duplicate_agent.py), [`backend/main.py`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/backend/main.py) (`submit_student_feedback`) |
| **Module X** | **Applications of AI** (Healthcare, Governance & Administration) | Case study of AI in Campus Governance & Educational Administration: Automated triage, anti-ragging protection, food safety alerts. | Full application dashboard & telemetry at [`frontend/index.html`](file:///g:/Projects/AI-Based%20Smart%20College%20Support%20and%20Complaint%20Management%20Agent/frontend/index.html) |


---

## Detailed Academic Walkthroughs

### 1. Module I: Intelligent Agents & PEAS Specification
- **Performance Measure ($P$):**
  - SLA Compliance Rate: $\ge 95\%$
  - Escalation Risk Reduction: Proactive detection
  - Student Satisfaction: $\ge 4.2 / 5.0$
  - Routing Accuracy: $\ge 90\%$
- **Environment ($E$):**
  - Partially Observable: Student grievance text does not disclose all technical causes.
  - Stochastic: Unpredictable severity, equipment failures, variable student emotion.
  - Sequential: Triage decisions directly determine subsequent dispatch and escalation.
  - Dynamic: New complaints stream into the queue continuously.
  - Continuous: Priority scores and confidence values range continuously in $[0.0, 1.0]$.
  - Multi-Agent: Collaborating AI triage agents, administrative human supervisors, and students.
- **Actuators ($A$):**
  - Department routing, priority assignment, SLA allocation, emergency email/SMS dispatch, A* plan generation, student response generator.
- **Sensors ($S$):**
  - Student complaint narrative (NLP text stream), location/room regex, sentiment lexicon, student ID/anonymity flag, active ticket history, 1-5 star ratings.

### 2. Module II & III & VII: State-Space Planning (A* Informed vs UCS Uninformed)
The agent constructs a search graph where nodes represent institutional states and edges represent actions:
- **A* Search (Module III & VII):** $f(n) = g(n) + h(n)$
- **Uniform Cost Search (Module II):** $f(n) = g(n)$, $h(n) = 0$
- **$g(n)$ (Path Cost):** Cumulative hours elapsed across completed resolution steps.
- **$h(n)$ (Admissible Heuristic):** Underestimates remaining hours by multiplying unsatisfied goal fluents by their minimum possible operator duration.
- **Goal Condition:**
  $$\text{State} = \{\text{verified}: \text{True}, \text{work\_executed}: \text{True}, \text{audited}: \text{True}, \text{student\_notified}: \text{True}\}$$

### 3. Module IV: Constraint Satisfaction Problem (CSP) Staff Dispatch
The multi-agent system formulates specialist dispatch as a formal CSP $\langle X, D, C \rangle$:
- **Variables ($X$):** Active student tickets $\{T_1, T_2, \dots, T_k\}$.
- **Domains ($D$):** Qualified institutional officers $\{S_1, S_2, \dots, S_m\}$.
- **Constraints ($C$):**
  1. *Category Match:* Specialist qualification matches ticket category.
  2. *Capacity Limit:* Max concurrent assignments per specialist $\le \text{max\_capacity}$.
  3. *Emergency Duty Clearance:* Emergency tickets require Senior On-Call officers.
  4. *Spatial Jurisdiction:* Wardens must match hostel block jurisdiction.
- **Inference & Search Algorithm:**
  - Backtracking Search with **Minimum Remaining Values (MRV)** heuristic.
  - **Least Constraining Value (LCV)** domain value ordering.
  - **Forward Checking (Constraint Propagation)** pruning domains to detect early failure.

### 4. Module V & VI: Logic Reasoning, Forward & Backward Chaining

The system encodes campus regulations into first-order production rules:
$$\text{Antecedent}_1 \land \text{Antecedent}_2 \implies \text{Consequent}$$
- **Example:**
  $$\text{Category}(\text{Ticket}, \text{"Anti-Ragging"}) \lor \text{Contains}(\text{Text}, \text{"harassment"}) \implies \text{Priority}(\text{Ticket}, \text{"Emergency"}) \land \text{SLA}(\text{Ticket}, 2\,\text{hrs})$$
The inference engine executes Modus Ponens repeatedly over working memory until reaching a fixpoint.

### 4. Module VIII: Bayesian Uncertainty
Real student complaints have incomplete information. The system utilizes Bayes' Rule with conditional likelihood distributions:
$$P(\text{Escalation} \mid D, U, R) = \frac{P(\text{Escalation} \mid C) \cdot P(D \mid E) \cdot P(U \mid E) \cdot P(R \mid E)}{P(\text{Evidence})}$$
Where:
- $P(\text{Escalation} \mid C)$: Prior probability conditioned on Department Category.
- $P(D \mid E)$: Likelihood of distress sentiment given escalation ($0.85$ vs $0.20$).
- $P(U \mid E)$: Likelihood of urgent keywords ($0.80$ vs $0.25$).
- $P(R \mid E)$: Likelihood of recurring cluster incidents ($0.75$ vs $0.15$).

---
