"""
Unit tests for A* State-Space Planning Agent.
Addresses FAI Module III & VII.
"""

import pytest
from backend.agents.planning_agent import StateSpacePlanningAgent


def test_astar_planning_standard():
    planner = StateSpacePlanningAgent()
    plan = planner.generate_plan(
        category="Academics",
        priority="Medium",
        requires_parts=False,
        requires_dean_alert=False
    )
    assert len(plan) >= 3
    # Step numbers must be sequential
    for i, step in enumerate(plan, 1):
        assert step["step_number"] == i
    # Final step must be notify student and close
    assert plan[-1]["action"] == "NotifyStudentAndCloseTicket"


def test_astar_planning_emergency_with_parts():
    planner = StateSpacePlanningAgent()
    plan = planner.generate_plan(
        category="Hostel",
        priority="Emergency",
        requires_parts=True,
        requires_dean_alert=True
    )
    actions = [s["action"] for s in plan]
    assert "EscalateDeanEmergency" in actions
    assert "ProcureReplacementEquipment" in actions
    assert "ExecuteCorrectiveAction" in actions
    assert "NotifyStudentAndCloseTicket" in actions


def test_search_mode_ucs_vs_astar():
    planner = StateSpacePlanningAgent()
    # A* Informed Search
    astar_plan, astar_tel = planner.search_with_telemetry(
        category="Hostel",
        priority="Emergency",
        requires_parts=True,
        requires_dean_alert=True,
        search_mode="astar"
    )
    # Uniform Cost Search (Uninformed, h = 0)
    ucs_plan, ucs_tel = planner.search_with_telemetry(
        category="Hostel",
        priority="Emergency",
        requires_parts=True,
        requires_dean_alert=True,
        search_mode="ucs"
    )

    # Both must find optimal path of the exact same cost
    assert astar_tel["path_cost_hours"] == ucs_tel["path_cost_hours"]
    # Informed A* must expand less than or equal nodes compared to UCS
    assert astar_tel["nodes_expanded"] <= ucs_tel["nodes_expanded"]
    assert astar_tel["heuristic_admissible"] is True

