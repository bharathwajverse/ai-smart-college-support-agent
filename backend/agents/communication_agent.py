"""
Communication & Notification Agent:
Synthesizes empathetic, transparent natural language responses to students,
explaining AI triage decisions, estimated resolution time, and institutional policies.
Includes live LLM generation (Groq / Qwen / Llama) with high-quality offline heuristic fallback.
"""

import os
import httpx
from typing import Dict, Any, List, Optional


class CommunicationAgent:
    def __init__(self):
        self.groq_api_key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Invokes Groq LLM API if key is present; returns None on timeout/failure."""
        if not self.groq_api_key or not self.groq_api_key.strip().startswith("gsk_"):
            return None
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key.strip()}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are CampusResolve AI, an empathetic, smart college student support assistant. "
                            "Provide concise, helpful, and polite guidance to college students about campus life, "
                            "hostel issues, academics, examinations, and grievance redressal."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 180,
                "temperature": 0.4
            }
            resp = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=4.0
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return None
        return None

    def generate_student_acknowledgement(
        self,
        ticket_code: str,
        student_name: str,
        category: str,
        priority: str,
        department: str,
        sla_hours: int,
        fired_rules: List[Dict[str, Any]],
        resolution_plan: List[Dict[str, Any]],
        is_cluster: bool = False
    ) -> str:
        """
        Drafts a comprehensive, reassuring notification to the student
        explaining the AI triage decisions and action steps.
        """
        name_greeting = f"Dear {student_name}," if student_name and student_name != "Anonymous" else "Dear Student,"
        
        emergency_notice = ""
        if priority == "Emergency":
            emergency_notice = (
                "\n⚠️ **URGENT PRIORITY ACTIVATED**: This complaint has been flagged as an Emergency. "
                "The Chief Proctor, Dean, and Health/Safety task forces have been alerted via high-priority dispatch.\n"
            )

        cluster_notice = ""
        if is_cluster:
            cluster_notice = (
                "\nℹ️ **Campus Incident Clustered**: Our AI detected multiple reports regarding this same issue in your area. "
                "Your grievance has been merged into a prioritized Master Incident to expedite rapid resolution.\n"
            )

        policy_notes = ""
        if fired_rules:
            policies = []
            for r in fired_rules:
                ref = r.get("consequent", {}).get("policy_reference")
                if ref:
                    policies.append(f"- *{ref}*")
            if policies:
                policy_notes = "\n**Applicable Campus Regulations & Ordinances:**\n" + "\n".join(policies) + "\n"

        plan_summary = ""
        if resolution_plan:
            plan_lines = [f"{step['step_number']}. **{step['action']}** (Assignee: {step['actor']})" for step in resolution_plan[:3]]
            plan_summary = "\n**Resolution Workflow Initiated:**\n" + "\n".join(plan_lines)

        message = f"""{name_greeting}

Thank you for contacting the CampusResolve AI Grievance Management System. Your ticket **{ticket_code}** has been successfully registered and evaluated by our intelligent multi-agent triage pipeline.
{emergency_notice}{cluster_notice}
**Ticket Summary:**
- **Category:** {category}
- **Assigned Authority:** {department}
- **Priority Assessment:** {priority}
- **Expected SLA Resolution Window:** within {sla_hours} hours
{policy_notes}{plan_summary}

You can track real-time resolution progress and agent execution steps directly on your student portal dashboard.

*In case of immediate physical danger, please contact the 24x7 Campus Helpline at 1800-180-5522.*
"""
        return message.strip()

    def generate_chat_response(
        self,
        query: str,
        category: str,
        faq_data: Dict[str, Any] = None,
        fired_rules: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answers student real-time chat queries with knowledge base, LLM reasoning, and policy rules.
        """
        if faq_data:
            return {
                "answer": faq_data["answer"],
                "confidence": faq_data["confidence"],
                "suggested_action": f"Refer to campus regulation for {faq_data['topic']}.",
                "intent": "Policy_Inquiry",
                "escalation_required": False
            }

        # Anti-ragging or safety direct query
        if category == "Anti-Ragging & Safety":
            return {
                "answer": "If you or someone you know is experiencing ragging or harassment, report it immediately! CampusResolve AI guarantees total anonymity. You may submit an emergency complaint now or call the Proctorial Board hotline at 1800-180-5522.",
                "confidence": 0.95,
                "suggested_action": "File an Anonymous Emergency Complaint",
                "intent": "Safety_Emergency",
                "escalation_required": True
            }

        # Live LLM response generation if available
        llm_response = self._call_llm(query)
        if llm_response:
            return {
                "answer": llm_response,
                "confidence": 0.88,
                "suggested_action": f"Track or submit grievance under {category}",
                "intent": "AI_LLM_Support",
                "escalation_required": False
            }

        return {
            "answer": f"I have categorized your query under **{category}**. To register an official grievance with automated A* resolution tracking, please submit a ticket using the 'New Complaint' form.",
            "confidence": 0.70,
            "suggested_action": "File Official Complaint",
            "intent": "General_Support",
            "escalation_required": False
        }
