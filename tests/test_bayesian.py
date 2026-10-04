"""
Unit tests for Bayesian Urgency and Escalation Risk.
Addresses FAI Module VIII.
"""

import pytest
from backend.agents.bayesian_urgency import BayesianUrgencyEstimator


def test_bayesian_anti_ragging_emergency():
    estimator = BayesianUrgencyEstimator()
    post_e, urgency, pri, breakdown = estimator.infer_escalation_risk(
        category="Anti-Ragging & Safety",
        sentiment_score=-0.8,
        urgency_cues_count=2,
        is_cluster_or_recurring=False
    )
    assert post_e > 0.80
    assert pri == "Emergency"
    assert "prior_P(Escalation)" in breakdown


def test_bayesian_low_risk_library():
    estimator = BayesianUrgencyEstimator()
    post_e, urgency, pri, breakdown = estimator.infer_escalation_risk(
        category="Library",
        sentiment_score=0.2,
        urgency_cues_count=0,
        is_cluster_or_recurring=False
    )
    assert post_e < 0.30
    assert pri in ["Low", "Medium"]


def test_bayesian_cluster_recurrence_boost():
    estimator = BayesianUrgencyEstimator()
    post_normal, _, _, _ = estimator.infer_escalation_risk(
        category="Hostel",
        sentiment_score=0.0,
        urgency_cues_count=0,
        is_cluster_or_recurring=False
    )
    post_cluster, _, _, _ = estimator.infer_escalation_risk(
        category="Hostel",
        sentiment_score=0.0,
        urgency_cues_count=0,
        is_cluster_or_recurring=True
    )
    # Recurrence must increase probability of escalation
    assert post_cluster > post_normal
