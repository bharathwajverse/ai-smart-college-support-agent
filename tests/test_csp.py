"""
Unit tests for Module IV: Constraint Satisfaction Problem (CSP) Staff Dispatch Agent.
"""

import pytest
from backend.agents.dispatch_csp import GrievanceCSP, Specialist


def test_csp_dispatch_solves_under_capacity():
    tickets = [
        {"ticket_code": "TCK-IT-001", "subject": "WiFi down in Hostel", "category": "IT & Infrastructure", "priority": "High", "location": "Shivalik Hostel"},
        {"ticket_code": "TCK-MESS-001", "subject": "Stale food in canteen", "category": "Mess & Canteen", "priority": "Medium", "location": "Central Mess"},
        {"ticket_code": "TCK-RAG-001", "subject": "Ragging incident in hostel", "category": "Anti-Ragging & Safety", "priority": "Emergency", "location": "Nilgiri Hostel"}
    ]
    csp = GrievanceCSP(tickets=tickets)
    solution, telemetry = csp.solve()

    assert solution is not None
    assert telemetry["solved"] is True
    assert len(solution) == 3

    # Check qualification constraints
    assert "Vikram" in solution["TCK-IT-001"]["assigned_staff_name"] or "Pooja" in solution["TCK-IT-001"]["assigned_staff_name"]
    assert "Sunita" in solution["TCK-MESS-001"]["assigned_staff_name"] or "Parthasarathy" in solution["TCK-MESS-001"]["assigned_staff_name"]
    assert solution["TCK-RAG-001"]["is_senior_on_call"] is True
    assert "Proctor" in solution["TCK-RAG-001"]["department"]


def test_csp_capacity_constraint_enforcement():
    # Create 4 IT tickets with specialists having capacity 1 each
    specialists = [
        Specialist("S1", "Engineer 1", "IT", ["IT & Infrastructure"], max_capacity=1),
        Specialist("S2", "Engineer 2", "IT", ["IT & Infrastructure"], max_capacity=1)
    ]
    # 2 tickets should be solvable
    tickets = [
        {"ticket_code": "T1", "category": "IT & Infrastructure", "priority": "Medium", "location": "Lab 1"},
        {"ticket_code": "T2", "category": "IT & Infrastructure", "priority": "Medium", "location": "Lab 2"}
    ]
    csp = GrievanceCSP(tickets=tickets, specialists=specialists)
    solution, telemetry = csp.solve()
    assert solution is not None
    assert solution["T1"]["assigned_staff_id"] != solution["T2"]["assigned_staff_id"]

    # 3 tickets should fail capacity check (2 capacity < 3 tickets)
    tickets_overload = tickets + [{"ticket_code": "T3", "category": "IT & Infrastructure", "priority": "Medium", "location": "Lab 3"}]
    csp_overload = GrievanceCSP(tickets=tickets_overload, specialists=specialists)
    solution_overload, telemetry_overload = csp_overload.solve()
    assert solution_overload is None
    assert telemetry_overload["solved"] is False


def test_csp_emergency_clearance_constraint():
    # Only senior staff can handle Emergency
    specialists = [
        Specialist("J1", "Junior Technician", "IT", ["IT & Infrastructure"], max_capacity=2, is_senior_on_call=False),
        Specialist("S1", "Senior Lead", "IT", ["IT & Infrastructure"], max_capacity=1, is_senior_on_call=True)
    ]
    tickets = [
        {"ticket_code": "T_EMERG", "category": "IT & Infrastructure", "priority": "Emergency", "location": "Server Room"}
    ]
    csp = GrievanceCSP(tickets=tickets, specialists=specialists)
    solution, _ = csp.solve()
    assert solution is not None
    assert solution["T_EMERG"]["assigned_staff_id"] == "S1"
