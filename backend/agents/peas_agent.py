"""
Module I: Intelligent Agents & PEAS Specification.
Defines the Formal PEAS model, Agent Types, and Utility functions
for the College Support & Complaint Management System.
"""

from typing import Dict, Any


class PEASModel:
    """
    Formal PEAS (Performance, Environment, Actuators, Sensors) Model.
    Directly addresses FAI Module I: Intelligent Agents.
    """

    def __init__(self):
        self.performance_measures = {
            "sla_compliance_rate": "Target >= 95% complaints resolved within defined SLA hours",
            "escalation_avoidance": "Proactive detection of grievances before administrative escalation",
            "student_satisfaction": "Target average rating >= 4.2 / 5.0",
            "triage_accuracy": "Target >= 90% automatic correct department classification"
        }
        
        self.environment = {
            "type": "Partially Observable, Stochastic, Sequential, Dynamic, Continuous, Multi-Agent",
            "entities": [
                "Undergraduate & Postgraduate Students",
                "Hostel Wardens & Mess Committees",
                "Heads of Departments & Faculty",
                "IT Infrastructure & Network Engineers",
                "Proctorial Board & Anti-Ragging Cell",
                "Finance & Accounts Section"
            ]
        }
        
        self.actuators = [
            "Ticket Category Classifier & Department Router",
            "Bayesian Priority & SLA Allocator",
            "A* State-Space Plan Generator",
            "Emergency Escalation Broadcaster (Dean/Wardens)",
            "Automated Student Resolution & Notification Dispatcher",
            "Duplicate Incident Clustering Mechanism"
        ]
        
        self.sensors = [
            "Student Complaint Subject & Description (NLP Text Stream)",
            "Extracted Location & Hostel/Lab Identifiers",
            "Student Identity / Anonymous Flag",
            "Sentiment Polarity & Urgency Lexicon Signals",
            "Historical Incident Recurrence & Ticket Logs",
            "Post-Resolution Student Feedback Ratings (1-5 Stars)"
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "performance_measures": self.performance_measures,
            "environment": self.environment,
            "actuators": self.actuators,
            "sensors": self.sensors,
            "agent_types": {
                "reflex_agent": "Rule-based emergency keyword detector for immediate response",
                "model_based_agent": "Maintains world state of active tickets, past grievances, and department loads",
                "goal_based_agent": "Ensures every ticket achieves the goal state 'RESOLVED'",
                "utility_based_agent": "Optimizes resolution utility U = w1*(1/time) + w2*(satisfaction) - w3*(escalation_risk)"
            }
        }


def calculate_agent_utility(resolution_time_hrs: float, sla_hours: float, escalation_risk: float, satisfaction: float = 4.0) -> float:
    """
    Utility Function for the College Management Agent:
    U(x) = alpha * (SLA_margin) + beta * (Satisfaction) - gamma * (Escalation_Risk)
    """
    sla_margin = max(0.0, (sla_hours - resolution_time_hrs) / max(sla_hours, 1.0))
    utility = (0.4 * sla_margin) + (0.4 * (satisfaction / 5.0)) - (0.2 * escalation_risk)
    return round(float(utility), 3)
