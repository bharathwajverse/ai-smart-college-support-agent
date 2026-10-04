# Project Presentation & Viva Defense Guide

Use this script and guide to deliver a 5-minute presentation of **CampusResolve AI** for your academic evaluation.

---

## 5-Minute Presentation Script

### Minute 1: The Problem & Real-World Motivation
> *"Good morning, respected professors. In traditional university grievance portals, complaints are processed manually by busy administrative staff. When a student reports an emergency like ragging, or 50 students report a hostel water outage, tickets sit in generic queues, duplicate workers are dispatched, and urgent crises get lost.*
> 
> *Our project, **CampusResolve AI**, solves this with a **Multi-Agent Artificial Intelligence System** that doesn't just chat—it autonomously triages grievances, calculates escalation risks under uncertainty, verifies college ordinances using logic, and plans optimal resolution workflows using A\* search."*

### Minute 2: Multi-Agent Architecture & Syllabus Alignment
> *"Our project directly demonstrates key concepts from our FAI curriculum:*
> 1. *In **Module I (Intelligent Agents)**, we implemented a formal PEAS model and utility-based agent optimizing SLA speed, student satisfaction, and escalation avoidance.*
> 2. *In **Modules V & VI (Inference & Knowledge Representation)**, we built a Forward Chaining inference engine that enforces campus ordinances and UGC safety policies using Modus Ponens.*
> 3. *In **Module VIII (Uncertainty in AI)**, we implemented a Bayesian Network that calculates the exact posterior probability of grievance escalation given student sentiment and urgency markers.*
> 4. *In **Modules III & VII (Informed Search & State Space Planning)**, we developed an A\* search planner with STRIPS-like operators that computes the optimal sequence of actions to resolve each complaint.*
> 5. *In **Module IX (Learning Agents)**, our duplicate detection agent clusters related campus incidents using TF-IDF similarity, and learns from post-resolution student ratings."*

### Minute 3 & 4: Live Demonstration Walkthrough
1. **Open the browser at `http://localhost:8000`**.
2. **Show Tab 1 (AI Support Chat)**:
   - Click the prompt: *"What is the minimum attendance required for semester exams?"*
   - Show how the agent references the Academic Ordinance (75% mandatory, 65% with medical condonation).
3. **Show Tab 2 (Submit Grievance)**:
   - Click the Examiner Quick Test button: **"🚨 Anti-Ragging Emergency"**.
   - Notice the anonymous switch is automatically toggled.
   - Click **"Submit to AI Agent Pipeline"**.
   - Highlight the modal that appears:
     - Priority promoted to **Emergency** (Rule `RULE_RAGGING_ZERO_TOLERANCE` fired!).
     - Bayesian escalation risk: **> 85%**.
     - SLA compressed to **2 hours**.
     - Notice the **7-step A\* resolution plan** generated dynamically.
4. **Show Tab 4 (Admin Triage Hub)**:
   - Point out the Bayesian risk bar and status filter.
   - Click **"Inspect & Act"** on any ticket. Show how the supervisor can transition status to `Resolved` and see the student submit a 5-star rating (Module IX feedback loop).
5. **Show Tab 5 (FAI Agent Inspector)**:
   - Show examiners the live interactive inspection of PEAS definitions, A\* operators, and Bayesian distributions.

### Minute 5: Conclusion & Viva Anticipation
> *"In conclusion, CampusResolve AI demonstrates that AI agents are far more than LLM chatbots: they combine symbolic logic, probabilistic reasoning, and graph search planning to solve critical institutional challenges."*

---

## Likely Viva Questions & Answers

**Q1: Why did you use A\* search for complaint planning instead of just hardcoded steps?**  
**Ans:** Different tickets have different conditions. For example, an electrical fault requires equipment procurement ($+3.5$ hours), whereas a ragging complaint requires confidential Dean alerts ($+0.2$ hours) and skips equipment requisition. The A\* planner searches the state space using an admissible heuristic $h(n)$ to dynamically find the shortest, lowest-cost sequence of actions tailored to that specific grievance.

**Q2: How does the Bayesian Urgency estimator handle uncertainty?**  
**Ans:** Students rarely provide complete or objective data when stressed. The Bayesian Network combines prior category risk with conditional likelihoods for sentiment distress, urgent keywords, and incident recurrence using Bayes' rule:
$$P(\text{Escalation} \mid \text{Evidence}) = \frac{P(\text{Escalation}) \cdot \prod P(e_i \mid \text{Escalation})}{P(\text{Evidence})}$$
This gives an objective, mathematical escalation probability rather than a subjective guess.

**Q3: Can your system run without external internet or paid API keys?**  
**Ans:** Yes, 100%! All AI components—the TF-IDF classifier, forward-chaining rule engine, Bayesian inference engine, and A\* planning agent—are completely self-contained in Python. It can also connect to Groq/Ollama/OpenAI if an API key is provided, but operates fully offline out-of-the-box.

---
