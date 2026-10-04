"""
Module V & VI: Inferences, Knowledge Representation & Reasoning.
Implements a Forward Chaining Inference Engine using First-Order/Propositional Logic
for College Ordinances, Safety Rules, and Academic Policies.
"""

import json
import os
from typing import Dict, Any, List, Optional


class KnowledgeInferenceEngine:
    def __init__(self, rules_path: str = None):
        if rules_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "knowledge_base", "college_rules.json")
            
        with open(rules_path, "r", encoding="utf-8") as f:
            self.knowledge = json.load(f)
            
        self.rules = self.knowledge.get("rules", [])
        self.faqs = self.knowledge.get("faq_knowledge", [])
        self.categories = {cat["name"]: cat for cat in self.knowledge.get("categories", [])}

    def _eval_condition(self, cond: Dict[str, Any], facts: Dict[str, Any]) -> bool:
        """Evaluates a single atomic logical condition or composite clause."""
        if "and" in cond:
            return all(self._eval_condition(sub_cond, facts) for sub_cond in cond["and"])
        if "or" in cond:
            return any(self._eval_condition(sub_cond, facts) for sub_cond in cond["or"])

        field = cond.get("field")
        val = facts.get(field)

        if "equals" in cond:
            return val == cond["equals"]
        if "in" in cond:
            return val in cond["in"]
        if "contains_any" in cond:
            text = str(val).lower() if val else ""
            return any(target.lower() in text for target in cond["contains_any"])
        if "greater_than" in cond:
            try:
                return float(val) > float(cond["greater_than"])
            except (ValueError, TypeError):
                return False
        return False

    def forward_chain(self, ticket_facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forward Chaining Inference Algorithm (Modus Ponens):
        Iterates over the rule base, evaluating antecedents against current working memory,
        and derives new consequent facts (Priority, SLA overrides, Dean escalation, etc.).
        """
        working_memory = dict(ticket_facts)
        # Ensure text is lowercase for robust matching
        working_memory["text"] = f"{ticket_facts.get('subject', '')} {ticket_facts.get('description', '')}".lower()
        
        fired_rules = []
        derived_facts = {
            "priority_override": None,
            "sla_hours_override": None,
            "mandatory_alerts": [],
            "action_required": [],
            "policy_references": []
        }

        # Forward chaining pass
        rule_queue = list(self.rules)
        changed = True
        iterations = 0

        while changed and iterations < 10:
            changed = False
            iterations += 1
            remaining_rules = []

            for rule in rule_queue:
                antecedent = rule.get("antecedent", {})
                if self._eval_condition(antecedent, working_memory):
                    # Rule matches! Fire consequent
                    consequent = rule.get("consequent", {})
                    fired_rules.append({
                        "rule_id": rule.get("rule_id"),
                        "module": rule.get("module"),
                        "consequent": consequent
                    })

                    if "set_priority" in consequent:
                        derived_facts["priority_override"] = consequent["set_priority"]
                        working_memory["priority"] = consequent["set_priority"]

                    if "set_sla_hours" in consequent:
                        derived_facts["sla_hours_override"] = consequent["set_sla_hours"]
                        working_memory["sla_hours"] = consequent["set_sla_hours"]

                    if "set_mandatory_alert" in consequent:
                        derived_facts["mandatory_alerts"].append(consequent["set_mandatory_alert"])

                    if "action_required" in consequent:
                        derived_facts["action_required"].append(consequent["action_required"])

                    if "policy_reference" in consequent:
                        derived_facts["policy_references"].append(consequent["policy_reference"])

                    changed = True
                else:
                    remaining_rules.append(rule)
                    
            rule_queue = remaining_rules

        return {
            "fired_rules_count": len(fired_rules),
            "fired_rules": fired_rules,
            "derived_facts": derived_facts,
            "iterations_to_fixpoint": iterations
        }

    def backward_chain(self, goal_type: str, ticket_facts: Dict[str, Any], goal_value: Any = None) -> Dict[str, Any]:
        """
        Backward Chaining Inference Algorithm (Module V & VI):
        Goal-directed reasoning that starts from a target hypothesis/goal
        (e.g., 'is_emergency', 'alert_dean', 'priority_override') and works backward
        through production rules to evaluate whether antecedent premises are satisfied.
        """
        working_memory = dict(ticket_facts)
        working_memory["text"] = f"{ticket_facts.get('subject', '')} {ticket_facts.get('description', '')}".lower()

        # Goal mapping definitions
        candidate_rules = []
        for rule in self.rules:
            consequent = rule.get("consequent", {})
            if goal_type == "is_emergency":
                if consequent.get("set_priority") == "Emergency":
                    candidate_rules.append(rule)
            elif goal_type == "alert_dean":
                if "Dean" in consequent.get("set_mandatory_alert", ""):
                    candidate_rules.append(rule)
            elif goal_type == "priority_override":
                if goal_value is None or consequent.get("set_priority") == goal_value:
                    candidate_rules.append(rule)
            elif goal_type == "sla_override":
                if goal_value is None or consequent.get("set_sla_hours") == goal_value:
                    candidate_rules.append(rule)
            elif goal_type in consequent:
                if goal_value is None or consequent.get(goal_type) == goal_value:
                    candidate_rules.append(rule)

        proof_path = []
        goal_satisfied = False
        matching_rule = None

        for rule in candidate_rules:
            antecedent = rule.get("antecedent", {})
            if self._eval_condition(antecedent, working_memory):
                goal_satisfied = True
                matching_rule = rule
                proof_path.append({
                    "rule_id": rule.get("rule_id"),
                    "module": rule.get("module"),
                    "antecedent_eval": "PROVED_TRUE",
                    "consequent": rule.get("consequent")
                })
                break
            else:
                proof_path.append({
                    "rule_id": rule.get("rule_id"),
                    "module": rule.get("module"),
                    "antecedent_eval": "UNSATISFIED_PREMISES"
                })

        return {
            "goal": goal_type,
            "goal_value": goal_value,
            "proven": goal_satisfied,
            "matching_rule": matching_rule.get("rule_id") if matching_rule else None,
            "policy_reference": matching_rule.get("consequent", {}).get("policy_reference") if matching_rule else None,
            "action_required": matching_rule.get("consequent", {}).get("action_required") if matching_rule else None,
            "proof_tree": proof_path
        }

    def query_faq(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Knowledge-Based QA: Searches ontological FAQs to answer general student inquiries.
        """
        query_words = set(user_query.lower().split())
        best_match = None
        max_overlap = 0

        for item in self.faqs:
            keywords = set(item.get("keywords", []))
            overlap = len(query_words.intersection(keywords))
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = item

        if best_match and max_overlap >= 1:
            return {
                "topic": best_match["topic"],
                "answer": best_match["answer"],
                "confidence": min(1.0, 0.4 + (max_overlap * 0.2))
            }
        return None

