"""
Module VIII: Uncertainty in AI - Bayesian Urgency & Escalation Risk Estimator.
Implements Bayesian Network inference to calculate the posterior probability of
grievance escalation given uncertainty in student sentiment, lexical urgency, and incident recurrence.
"""

from typing import Dict, Any, Tuple


class BayesianUrgencyEstimator:
    """
    Bayesian Inference Engine for Grievance Prioritization.
    Addresses FAI Module VIII: Representing Knowledge in an Uncertain Domain.
    """

    def __init__(self):
        # Prior probabilities P(Escalation) conditioned on Category
        self.category_priors = {
            "Anti-Ragging & Safety": 0.85,
            "Mess & Canteen": 0.50,
            "Hostel": 0.35,
            "Examinations": 0.40,
            "IT & Infrastructure": 0.25,
            "Accounts & Fees": 0.20,
            "Academics": 0.20,
            "Transport": 0.15,
            "Library": 0.08,
            "General": 0.15
        }

        # Conditional Likelihood Distributions:
        # P(Evidence | Escalation = True) vs P(Evidence | Escalation = False)
        self.likelihoods = {
            "distress_sentiment": {True: 0.85, False: 0.20},
            "urgency_keywords": {True: 0.80, False: 0.25},
            "recurring_or_cluster": {True: 0.75, False: 0.15},
            "time_sensitive_deadline": {True: 0.70, False: 0.18}
        }

    def infer_escalation_risk(
        self,
        category: str,
        sentiment_score: float,
        urgency_cues_count: int,
        is_cluster_or_recurring: bool = False,
        has_deadline: bool = False
    ) -> Tuple[float, float, str, Dict[str, Any]]:
        """
        Calculates posterior probability P(Escalation | Evidence) via Bayes' Theorem:
        P(E | e1, e2, e3, e4) = alpha * P(E) * PROD( P(ei | E) )
        """
        prior_e = self.category_priors.get(category, 0.20)
        prior_not_e = 1.0 - prior_e

        # Evaluate evidence states
        ev_distress = sentiment_score < -0.2
        ev_urgency = urgency_cues_count > 0
        ev_recurrence = is_cluster_or_recurring
        ev_deadline = has_deadline

        # Compute Likelihood for E = True
        l_e_distress = self.likelihoods["distress_sentiment"][True] if ev_distress else (1.0 - self.likelihoods["distress_sentiment"][True])
        l_e_urgency = self.likelihoods["urgency_keywords"][True] if ev_urgency else (1.0 - self.likelihoods["urgency_keywords"][True])
        l_e_rec = self.likelihoods["recurring_or_cluster"][True] if ev_recurrence else (1.0 - self.likelihoods["recurring_or_cluster"][True])
        l_e_dead = self.likelihoods["time_sensitive_deadline"][True] if ev_deadline else (1.0 - self.likelihoods["time_sensitive_deadline"][True])

        # Compute Likelihood for E = False
        l_ne_distress = self.likelihoods["distress_sentiment"][False] if ev_distress else (1.0 - self.likelihoods["distress_sentiment"][False])
        l_ne_urgency = self.likelihoods["urgency_keywords"][False] if ev_urgency else (1.0 - self.likelihoods["urgency_keywords"][False])
        l_ne_rec = self.likelihoods["recurring_or_cluster"][False] if ev_recurrence else (1.0 - self.likelihoods["recurring_or_cluster"][False])
        l_ne_dead = self.likelihoods["time_sensitive_deadline"][False] if ev_deadline else (1.0 - self.likelihoods["time_sensitive_deadline"][False])

        numerator_e = prior_e * l_e_distress * l_e_urgency * l_e_rec * l_e_dead
        numerator_not_e = prior_not_e * l_ne_distress * l_ne_urgency * l_ne_rec * l_ne_dead

        # Normalization factor alpha
        marginal = numerator_e + numerator_not_e
        if marginal == 0:
            posterior_escalation = prior_e
        else:
            posterior_escalation = numerator_e / marginal

        posterior_escalation = round(float(posterior_escalation), 3)

        # Composite Urgency Score (0.0 to 1.0)
        urgency_score = round(
            0.5 * posterior_escalation +
            0.3 * (1.0 if ev_urgency else 0.2) +
            0.2 * (abs(min(sentiment_score, 0.0))),
            3
        )
        urgency_score = min(1.0, max(0.05, urgency_score))

        # Assign Priority based on Bayesian Risk Bounds
        if posterior_escalation >= 0.80 or category == "Anti-Ragging & Safety":
            priority = "Emergency"
        elif posterior_escalation >= 0.55:
            priority = "High"
        elif posterior_escalation >= 0.25:
            priority = "Medium"
        else:
            priority = "Low"

        breakdown = {
            "prior_P(Escalation)": prior_e,
            "evidence_observed": {
                "distress_sentiment": ev_distress,
                "urgency_cues": ev_urgency,
                "recurring_incident": ev_recurrence,
                "time_deadline": ev_deadline
            },
            "posterior_P(Escalation|Evidence)": posterior_escalation,
            "marginal_probability_P(Evidence)": round(marginal, 5)
        }

        return posterior_escalation, urgency_score, priority, breakdown
