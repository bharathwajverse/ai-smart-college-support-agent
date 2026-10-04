"""
Integration tests for FastAPI REST Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_submit_complaint():
    payload = {
        "student_name": "Test Student",
        "student_id": "22CS999",
        "email": "test@apex.edu",
        "subject": "Broken washroom geyser in Shivalik Block A",
        "description": "The water heater on the second floor has an electrical short circuit and sparks when switched on.",
        "location": "Shivalik Hostel Block A, 2nd Floor",
        "category": "Hostel",
        "is_anonymous": False
    }
    response = client.post("/api/complaints", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "ticket_code" in data
    assert data["category"] == "Hostel"
    assert len(data["resolution_plan"]) > 0
    assert "ai_generated_response" in data


def test_api_chat():
    payload = {"query": "How many percent attendance is mandatory?"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "75%" in data["answer"]


def test_api_get_complaints():
    response = client.get("/api/complaints")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_api_update_status_and_feedback():
    # Submit first
    payload = {
        "student_name": "Feedback Tester",
        "subject": "Lab 102 computer keyboard not working",
        "description": "Keys sticking on computer terminal 12 in CSE department lab 102.",
        "category": "IT & Infrastructure"
    }
    create_res = client.post("/api/complaints", json=payload)
    ticket_code = create_res.json()["ticket_code"]

    # Transition status to Resolved
    patch_res = client.patch(
        f"/api/complaints/{ticket_code}/status",
        json={"status": "Resolved", "notes": "Replaced keyboard with spare.", "staff_name": "Lab Assistant"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "Resolved"

    # Submit feedback rating
    fb_res = client.post(
        f"/api/complaints/{ticket_code}/feedback",
        json={"satisfaction_score": 5, "comments": "Resolved quickly!"}
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["feedback_score"] == 5


def test_api_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] > 0
    assert "fai_modules_active" in data


def test_api_fai_diagnostics():
    response = client.get("/api/fai-diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert "peas_model" in data
    assert "planning_operators" in data
    assert "inference_rule_base" in data
    assert "csp_specification" in data
    assert "search_algorithms" in data


def test_api_csp_dispatch():
    response = client.post("/api/csp/dispatch")
    assert response.status_code == 200
    data = response.json()
    assert "telemetry" in data
    assert data["telemetry"]["solved"] is True or "message" in data["telemetry"]


def test_api_backward_chaining():
    payload = {
        "goal": "is_emergency",
        "facts": {
            "category": "Anti-Ragging & Safety",
            "subject": "Ragging complaint",
            "description": "Junior harassed in room."
        }
    }
    response = client.post("/api/inference/backward-chain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["proven"] is True
    assert data["matching_rule"] == "RULE_RAGGING_ZERO_TOLERANCE"


def test_api_compare_search():
    payload = {
        "category": "Hostel",
        "priority": "Emergency",
        "requires_parts": True,
        "requires_dean_alert": True
    }
    response = client.post("/api/planning/compare-search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "astar_informed_search" in data
    assert "uniform_cost_search_uninformed" in data
    assert "academic_comparison" in data

