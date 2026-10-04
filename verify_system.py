"""
Standalone verification script to test all core AI agent components,
Inference engine, A* planning, Bayesian estimation, and database storage.
Can be executed directly with: python verify_system.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, SessionLocal
from backend.models import TicketDB
from backend.agents.peas_agent import PEASModel, calculate_agent_utility
from backend.agents.classifier_agent import ClassifierAgent
from backend.agents.inference_engine import KnowledgeInferenceEngine
from backend.agents.planning_agent import StateSpacePlanningAgent
from backend.agents.bayesian_urgency import BayesianUrgencyEstimator
from backend.agents.duplicate_agent import DuplicateDetectionAgent
from backend.agents.orchestrator import CampusResolveOrchestrator


def run_all_verifications():
    print("=" * 60)
    print("[TEST] CAMPUSRESOLVE AI - SYSTEM VERIFICATION SUITE")
    print("=" * 60)

    # 1. PEAS Model Test
    print("\n[1/10] Testing Module I: PEAS Specification...")
    peas = PEASModel()
    p_dict = peas.to_dict()
    assert len(p_dict["performance_measures"]) >= 4
    assert len(p_dict["actuators"]) >= 4
    assert len(p_dict["sensors"]) >= 4
    u = calculate_agent_utility(5.0, 24.0, 0.1, 5.0)
    assert u > 0.5
    print("  [PASS] PEAS model and utility function verified! Utility:", u)

    # 2. Classifier Agent Test
    print("\n[2/10] Testing NLP Classifier & Entity Extraction...")
    clf = ClassifierAgent()
    cat, conf, diag = clf.classify(
        subject="Hostel WiFi disconnected",
        description="The campus router in Shivalik Block C is not connecting to the internet."
    )
    assert cat == "IT & Infrastructure"
    assert "detected_locations" in diag["entities"]
    print(f"  [PASS] Classified as '{cat}' (Confidence: {conf})")
    print(f"  [PASS] Extracted Entities: {diag['entities']}")

    # 3. Knowledge Base & Forward Chaining Test
    print("\n[3/10] Testing Module V & VI: Forward Chaining Inference...")
    engine = KnowledgeInferenceEngine()
    facts = {
        "category": "Anti-Ragging & Safety",
        "subject": "Ragging incident reported",
        "description": "Junior students forced to perform chores by seniors.",
        "sentiment": -0.8
    }
    infer_res = engine.forward_chain(facts)
    assert infer_res["fired_rules_count"] >= 1
    assert infer_res["derived_facts"]["priority_override"] == "Emergency"
    print(f"  [PASS] Fired {infer_res['fired_rules_count']} rules!")
    print(f"  [PASS] Priority Override: {infer_res['derived_facts']['priority_override']}")
    print(f"  [PASS] Mandatory Alert: {infer_res['derived_facts']['mandatory_alerts']}")

    # 4. State-Space A* Planning Test
    print("\n[4/10] Testing Module III & VII: A* Search Planning Agent...")
    planner = StateSpacePlanningAgent()
    plan = planner.generate_plan(
        category="Hostel",
        priority="Emergency",
        requires_parts=True,
        requires_dean_alert=True
    )
    assert len(plan) >= 4
    print(f"  [PASS] Synthesized A* plan with {len(plan)} optimal steps:")
    for step in plan:
        print(f"     Step {step['step_number']}: {step['action']} by {step['actor']} ({step['cumulative_hours']}h cumulative)")

    # 5. Bayesian Uncertainty Test
    print("\n[5/10] Testing Module VIII: Bayesian Escalation Estimator...")
    bayes = BayesianUrgencyEstimator()
    post_e, urgency, pri, breakdown = bayes.infer_escalation_risk(
        category="Anti-Ragging & Safety",
        sentiment_score=-0.7,
        urgency_cues_count=2,
        is_cluster_or_recurring=False
    )
    assert post_e > 0.8
    print(f"  [PASS] Posterior P(Escalation|Evidence): {post_e}")
    print(f"  [PASS] Composite Urgency Score: {urgency}")
    print(f"  [PASS] Bayesian Inferred Priority: {pri}")

    # 6. Duplicate Detection Test
    print("\n[6/10] Testing Module III & IX: Incident Clustering...")
    dup = DuplicateDetectionAgent(similarity_threshold=0.50)
    existing = [
        {"ticket_code": "TCK-001", "subject": "WiFi down in Shivalik Block C", "description": "No internet in room 301", "category": "IT & Infrastructure", "cluster_id": None, "status": "In Progress"}
    ]
    best_match, sim, _ = dup.find_similar_tickets(
        new_subject="Hostel Shivalik C WiFi dead",
        new_description="Internet not working in room 302",
        new_category="IT & Infrastructure",
        existing_tickets=existing
    )
    assert best_match is not None
    assert sim >= 0.50
    print(f"  [PASS] Successfully matched duplicate! Similarity: {sim} with ticket {best_match['ticket_code']}")


    # 7. End-to-End Orchestrator Pipeline Test with Database
    print("\n[7/10] Testing Full Orchestrator Multi-Agent Pipeline & SQLite DB...")
    init_db()
    db = SessionLocal()
    orchestrator = CampusResolveOrchestrator()
    ticket = orchestrator.process_new_complaint(
        db=db,
        subject="Water supply completely stopped in Nilgiri Hostel 1st floor",
        description="No water in washrooms since 6 AM today morning. Over 50 students affected.",
        student_name="Karan Verma",
        student_id="22ME101",
        email="karan.22me@apex.edu",
        location="Nilgiri Hostel, 1st Floor",
        user_category="Hostel"
    )
    db.close()

    assert ticket.id is not None
    assert ticket.ticket_code.startswith("TCK-")
    assert len(ticket.resolution_plan) > 0
    print(f"  [PASS] Ticket created: {ticket.ticket_code}")
    print(f"  [PASS] Assigned Department: {ticket.assigned_department}")
    print(f"  [PASS] Priority: {ticket.priority} | SLA: {ticket.sla_hours}h")
    print(f"  [PASS] AI Response preview: {ticket.ai_generated_response[:60]}...")

    # 8. Constraint Satisfaction Problem (CSP) Test (Module IV)
    print("\n[8/10] Testing Module IV: Constraint Satisfaction Problem (CSP) Staff Dispatch...")
    from backend.agents.dispatch_csp import GrievanceCSP
    csp_tickets = [
        {"ticket_code": "TCK-TEST-01", "category": "IT & Infrastructure", "priority": "High", "location": "Shivalik Hostel"},
        {"ticket_code": "TCK-TEST-02", "category": "Anti-Ragging & Safety", "priority": "Emergency", "location": "Nilgiri Hostel"},
        {"ticket_code": "TCK-TEST-03", "category": "Mess & Canteen", "priority": "Medium", "location": "Central Mess"}
    ]
    csp_solver = GrievanceCSP(tickets=csp_tickets)
    csp_sol, csp_tel = csp_solver.solve()
    assert csp_sol is not None
    assert csp_tel["solved"] is True
    assert len(csp_sol) == 3
    print(f"  [PASS] CSP solved with {csp_tel['constraint_checks']} constraint checks and {csp_tel['backtracks']} backtracks!")
    for t_id, alloc in csp_sol.items():
        print(f"     {t_id} ({alloc['category']}) -> {alloc['assigned_staff_name']}")

    # 9. Backward Chaining Inference Test (Module V)
    print("\n[9/10] Testing Module V: Goal-Driven Backward Chaining...")
    bc_facts = {
        "category": "Anti-Ragging & Safety",
        "subject": "Ragging in common room",
        "description": "Junior threatened by seniors."
    }
    bc_res = engine.backward_chain("is_emergency", bc_facts)
    assert bc_res["proven"] is True
    print(f"  [PASS] Backward Chaining proved goal '{bc_res['goal']}' using rule '{bc_res['matching_rule']}'!")

    # 10. Search Comparison Benchmark (Module II vs Module III)
    print("\n[10/10] Testing Module II vs III: Informed (A*) vs Uninformed (UCS) Search...")
    astar_p, astar_tel = planner.search_with_telemetry("Hostel", "Emergency", True, True, "astar")
    ucs_p, ucs_tel = planner.search_with_telemetry("Hostel", "Emergency", True, True, "ucs")
    assert astar_tel["nodes_expanded"] <= ucs_tel["nodes_expanded"]
    assert astar_tel["path_cost_hours"] == ucs_tel["path_cost_hours"]
    print(f"  [PASS] A* expanded {astar_tel['nodes_expanded']} nodes vs UCS {ucs_tel['nodes_expanded']} nodes (Cost: {astar_tel['path_cost_hours']}h).")

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL 10 TEST SUITES PASSED! 100% OPERATIONAL.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_verifications()

