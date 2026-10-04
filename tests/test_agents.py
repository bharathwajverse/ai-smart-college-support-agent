"""
Unit tests for Classifier Agent, PEAS model, and Communication Agent.
"""

import pytest
from backend.agents.peas_agent import PEASModel, calculate_agent_utility
from backend.agents.classifier_agent import ClassifierAgent
from backend.agents.communication_agent import CommunicationAgent


def test_peas_model_structure():
    peas = PEASModel()
    data = peas.to_dict()
    assert "performance_measures" in data
    assert "environment" in data
    assert "actuators" in data
    assert "sensors" in data
    assert "agent_types" in data
    assert len(data["actuators"]) >= 4
    assert len(data["sensors"]) >= 4


def test_utility_calculation():
    # resolution within SLA -> positive utility
    u = calculate_agent_utility(resolution_time_hrs=5.0, sla_hours=24.0, escalation_risk=0.1, satisfaction=5.0)
    assert u > 0.5

    # exceeded SLA and high escalation risk -> lower utility
    u_low = calculate_agent_utility(resolution_time_hrs=30.0, sla_hours=24.0, escalation_risk=0.9, satisfaction=2.0)
    assert u_low < u


def test_classifier_agent_it():
    classifier = ClassifierAgent()
    cat, conf, diag = classifier.classify(
        subject="Hostel WiFi disconnected",
        description="The campus router in Shivalik Block C is not connecting to the internet."
    )
    assert cat == "IT & Infrastructure"
    assert conf > 0.2
    assert "detected_locations" in diag["entities"]


def test_classifier_anti_ragging_safety_override():
    classifier = ClassifierAgent()
    cat, conf, diag = classifier.classify(
        subject="Harassment in hostel",
        description="Seniors are bullying and ragging juniors in the common room."
    )
    assert cat == "Anti-Ragging & Safety"
    assert conf >= 0.95


def test_communicator_student_acknowledgement():
    comm = CommunicationAgent()
    msg = comm.generate_student_acknowledgement(
        ticket_code="TCK-TEST-001",
        student_name="Rahul",
        category="Hostel",
        priority="Medium",
        department="Hostel Office",
        sla_hours=24,
        fired_rules=[],
        resolution_plan=[{"step_number": 1, "action": "Verify", "actor": "Officer", "cumulative_hours": 0.5}],
        is_cluster=False
    )
    assert "TCK-TEST-001" in msg
    assert "Rahul" in msg
    assert "24 hours" in msg
