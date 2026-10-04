"""
Unit tests for Knowledge Inference Engine and Forward Chaining.
Addresses FAI Module V & VI.
"""

import pytest
from backend.agents.inference_engine import KnowledgeInferenceEngine


def test_forward_chaining_ragging_rule():
    engine = KnowledgeInferenceEngine()
    facts = {
        "category": "Anti-Ragging & Safety",
        "subject": "Ragging incident reported",
        "description": "Junior students forced to stay up late by seniors.",
        "sentiment": -0.8
    }
    result = engine.forward_chain(facts)
    assert result["fired_rules_count"] >= 1
    assert result["derived_facts"]["priority_override"] == "Emergency"
    assert result["derived_facts"]["sla_hours_override"] == 2
    assert len(result["derived_facts"]["mandatory_alerts"]) >= 1


def test_forward_chaining_food_safety():
    engine = KnowledgeInferenceEngine()
    facts = {
        "category": "Mess & Canteen",
        "subject": "Severe food poisoning in canteen",
        "description": "Students vomiting and experiencing stomach pain after mess dinner.",
        "sentiment": -0.7
    }
    result = engine.forward_chain(facts)
    assert result["derived_facts"]["priority_override"] == "Emergency"
    assert result["derived_facts"]["sla_hours_override"] == 4


def test_faq_retrieval():
    engine = KnowledgeInferenceEngine()
    faq = engine.query_faq("What is the minimum attendance requirement?")
    assert faq is not None
    assert "75%" in faq["answer"]
    assert faq["topic"] == "Attendance Rules"


def test_backward_chaining_goal_verification():
    engine = KnowledgeInferenceEngine()
    facts = {
        "category": "Anti-Ragging & Safety",
        "subject": "Seniors ragging juniors",
        "description": "Junior threatened and bullied."
    }
    # Goal: Is emergency triage proven?
    res_emergency = engine.backward_chain("is_emergency", facts)
    assert res_emergency["proven"] is True
    assert res_emergency["matching_rule"] == "RULE_RAGGING_ZERO_TOLERANCE"

    # Goal: Does this mandate Dean alert?
    res_dean = engine.backward_chain("alert_dean", facts)
    assert res_dean["proven"] is True

    # Goal on benign facts should fail
    benign_facts = {"category": "Library", "subject": "Book return", "description": "Need extension on book."}
    res_fail = engine.backward_chain("is_emergency", benign_facts)
    assert res_fail["proven"] is False

