"""
Master Agent Orchestrator:
Coordinates the collaborative multi-agent pipeline for intelligent complaint processing.
Integrates Classifier, Inference Engine, Bayesian Estimator, Duplicate Detector,
A* State Space Planner, and Communication Agent.
"""

import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models import TicketDB, AgentAuditLogDB, TicketCategory, TicketPriority, TicketStatus
from backend.agents.peas_agent import PEASModel, calculate_agent_utility
from backend.agents.classifier_agent import ClassifierAgent
from backend.agents.inference_engine import KnowledgeInferenceEngine
from backend.agents.planning_agent import StateSpacePlanningAgent
from backend.agents.bayesian_urgency import BayesianUrgencyEstimator
from backend.agents.duplicate_agent import DuplicateDetectionAgent
from backend.agents.communication_agent import CommunicationAgent
from backend.agents.dispatch_csp import GrievanceCSP



class CampusResolveOrchestrator:
    def __init__(self):
        self.peas_model = PEASModel()
        self.classifier = ClassifierAgent()
        self.inference_engine = KnowledgeInferenceEngine()
        self.planner = StateSpacePlanningAgent()
        self.bayesian = BayesianUrgencyEstimator()
        self.duplicate_agent = DuplicateDetectionAgent()
        self.communicator = CommunicationAgent()

    def process_new_complaint(
        self,
        db: Session,
        subject: str,
        description: str,
        student_name: str = "Anonymous",
        student_id: str = "N/A",
        email: str = "",
        phone: str = "",
        location: str = "",
        user_category: Optional[str] = None,
        is_anonymous: bool = False
    ) -> TicketDB:
        """
        Full Multi-Agent Pipeline Execution:
        Sensors -> Classification -> Logic Inference -> Bayesian Uncertainty -> Clustering -> A* Planning -> Actuators
        """
        # Step 1: Classifier Agent (NLP + Entity Extraction)
        detected_cat, cat_conf, nlp_diag = self.classifier.classify(
            subject=subject,
            description=description,
            user_category=user_category
        )
        entities = nlp_diag.get("entities", {})
        sentiment = nlp_diag.get("sentiment", 0.0)
        detected_loc = location or ", ".join(entities.get("detected_locations", []))

        # Step 2: Knowledge-Based Forward Chaining Inference (Module V & VI)
        facts = {
            "category": detected_cat,
            "subject": subject,
            "description": description,
            "sentiment": sentiment,
            "is_anonymous": is_anonymous
        }
        infer_result = self.inference_engine.forward_chain(facts)
        derived = infer_result["derived_facts"]
        fired_rules = infer_result["fired_rules"]

        # Step 3: Duplicate & Semantic Clustering Agent (Module III & IX)
        active_tickets = db.query(TicketDB).filter(
            TicketDB.status.in_([TicketStatus.SUBMITTED.value, TicketStatus.TRIAGED.value, TicketStatus.IN_PROGRESS.value])
        ).all()
        ticket_dicts = [
            {"id": t.id, "ticket_code": t.ticket_code, "subject": t.subject, "description": t.description, "category": t.category, "location": t.location, "cluster_id": t.cluster_id, "status": t.status}
            for t in active_tickets
        ]
        best_match, max_sim, cluster_matches = self.duplicate_agent.find_similar_tickets(
            new_subject=subject,
            new_description=description,
            new_category=detected_cat,
            existing_tickets=ticket_dicts,
            new_location=detected_loc
        )

        cluster_id = None
        is_recurring = False
        if best_match and max_sim >= 0.58:
            is_recurring = True
            cluster_id = best_match.get("cluster_id") or f"CLUSTER_{uuid.uuid4().hex[:6].upper()}"
            # If the matching ticket doesn't have a cluster_id yet, update it
            matching_db_ticket = db.query(TicketDB).filter(TicketDB.ticket_code == best_match["ticket_code"]).first()
            if matching_db_ticket and not matching_db_ticket.cluster_id:
                matching_db_ticket.cluster_id = cluster_id
                matching_db_ticket.is_master_incident = True

        # Step 4: Bayesian Urgency & Escalation Risk Estimator (Module VIII)
        urgency_cues_count = len(entities.get("urgency_cues", []))
        has_deadline = any(w in description.lower() for w in ["tomorrow", "today", "urgent", "exam", "deadline"])
        
        post_escalation, urgency_score, bayes_priority, bayes_breakdown = self.bayesian.infer_escalation_risk(
            category=detected_cat,
            sentiment_score=sentiment,
            urgency_cues_count=urgency_cues_count,
            is_cluster_or_recurring=is_recurring,
            has_deadline=has_deadline
        )

        # Reconcile Priority & SLA (taking maximum severity to protect student welfare)
        priority_ranks = {
            TicketPriority.LOW.value: 1,
            TicketPriority.MEDIUM.value: 2,
            TicketPriority.HIGH.value: 3,
            TicketPriority.EMERGENCY.value: 4
        }
        rule_priority = derived.get("priority_override")
        if rule_priority:
            final_priority = rule_priority if priority_ranks.get(rule_priority, 2) >= priority_ranks.get(bayes_priority, 2) else bayes_priority
        else:
            final_priority = bayes_priority

        cat_meta = self.inference_engine.categories.get(detected_cat, {})
        base_sla = derived.get("sla_hours_override") or cat_meta.get("default_sla_hours", 48)
        
        if final_priority == TicketPriority.EMERGENCY.value:
            final_sla = min(base_sla, 4)
        elif final_priority == TicketPriority.HIGH.value:
            final_sla = min(base_sla, 24)
        else:
            final_sla = base_sla


        # Step 5: A* State-Space Resolution Planner (Module III & VII)
        requires_parts = detected_cat in [TicketCategory.IT_FACILITIES.value, TicketCategory.HOSTEL.value]
        requires_dean = bool(derived.get("mandatory_alerts") or final_priority == TicketPriority.EMERGENCY.value)
        resolution_plan = self.planner.generate_plan(
            category=detected_cat,
            priority=final_priority,
            requires_parts=requires_parts,
            requires_dean_alert=requires_dean
        )

        # Step 6: Generate Ticket Code
        random_suffix = uuid.uuid4().hex[:5].upper()
        ticket_code = f"TCK-{detected_cat[:3].upper()}-{random_suffix}"

        # Step 7: Communication Agent (Drafts response to student)
        ai_response_text = self.communicator.generate_student_acknowledgement(
            ticket_code=ticket_code,
            student_name="Anonymous Student" if is_anonymous else student_name,
            category=detected_cat,
            priority=final_priority,
            department=cat_meta.get("department", "Campus Administration"),
            sla_hours=final_sla,
            fired_rules=fired_rules,
            resolution_plan=resolution_plan,
            is_cluster=bool(cluster_id)
        )

        # Calculate agent utility
        total_plan_time = resolution_plan[-1]["cumulative_hours"] if resolution_plan else float(final_sla)
        agent_utility = calculate_agent_utility(
            resolution_time_hrs=total_plan_time,
            sla_hours=final_sla,
            escalation_risk=post_escalation
        )

        agent_reasoning = {
            "classification_confidence": cat_conf,
            "sentiment_score": sentiment,
            "bayesian_breakdown": bayes_breakdown,
            "forward_chaining_iterations": infer_result.get("iterations_to_fixpoint", 1),
            "similarity_with_existing": max_sim,
            "calculated_utility": agent_utility,
            "fai_modules_exercised": [
                "Module I: PEAS Specification & Utility Agent",
                "Module III: Informed Search & Cosine Metric",
                "Module V & VI: Logic Reasoning & Forward Chaining",
                "Module VII: A* State Space Planning",
                "Module VIII: Bayesian Uncertainty & Escalation Inference",
                "Module IX: Incident Clustering & Duplicate Learning"
            ]
        }

        # Step 8: Persist to Database
        db_ticket = TicketDB(
            ticket_code=ticket_code,
            student_name="Anonymous" if is_anonymous else student_name,
            student_id="ANON" if is_anonymous else (entities.get("detected_student_id") or student_id),
            email="" if is_anonymous else email,
            phone="" if is_anonymous else (entities.get("phone_number") or phone),
            is_anonymous=is_anonymous,
            subject=subject,
            description=description,
            location=detected_loc,
            category=detected_cat,
            priority=final_priority,
            status=TicketStatus.TRIAGED.value,
            assigned_department=cat_meta.get("department", "Student Grievance Office"),
            assigned_staff=cat_meta.get("action_team", "Support Queue"),
            sla_hours=final_sla,
            bayesian_urgency_score=urgency_score,
            escalation_risk=post_escalation,
            sentiment_score=sentiment,
            cluster_id=cluster_id,
            is_master_incident=False if cluster_id and best_match else (True if cluster_id else False),
            extracted_entities=entities,
            rules_triggered=fired_rules,
            resolution_plan=resolution_plan,
            agent_reasoning=agent_reasoning,
            ai_generated_response=ai_response_text
        )

        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)

        # Audit Log
        audit_log = AgentAuditLogDB(
            ticket_id=db_ticket.id,
            agent_name="CampusResolveOrchestrator",
            module_reference="Modules I, III, V, VI, VII, VIII, IX",
            action="AUTO_TRIAGE_AND_PLAN_SYNTHESIS",
            inputs={"subject": subject, "category_hint": user_category},
            outputs={"category": detected_cat, "priority": final_priority, "sla_hours": final_sla, "plan_steps": len(resolution_plan)},
            reasoning=f"Classified into {detected_cat} with confidence {cat_conf}. Fired {len(fired_rules)} logic rules. Escalation risk {post_escalation}."
        )
        db.add(audit_log)
        db.commit()

        return db_ticket

    def handle_student_chat(self, query: str, student_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Interactive student conversational QA.
        Checks Knowledge Base (Module VI) and responds dynamically.
        """
        faq_data = self.inference_engine.query_faq(query)
        detected_cat, _, _ = self.classifier.classify(subject=query, description="")
        return self.communicator.generate_chat_response(
            query=query,
            category=detected_cat,
            faq_data=faq_data
        )

    def assign_pending_tickets_csp(self, db: Session) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Module IV: Constraint Satisfaction Problem (CSP) Staff Dispatch.
        Collects active unassigned or auto-queue tickets and runs Backtracking Search
        with MRV, LCV, and Forward Checking to assign specialized officers.
        """
        active_tickets = db.query(TicketDB).filter(
            TicketDB.status.in_([TicketStatus.SUBMITTED.value, TicketStatus.TRIAGED.value, TicketStatus.IN_PROGRESS.value])
        ).all()

        if not active_tickets:
            return None, {"solved": False, "message": "No active tickets requiring dispatch."}

        ticket_data = [
            {
                "ticket_code": t.ticket_code,
                "subject": t.subject,
                "category": t.category,
                "priority": t.priority,
                "location": t.location
            }
            for t in active_tickets
        ]

        csp_solver = GrievanceCSP(tickets=ticket_data)
        solution, telemetry = csp_solver.solve()

        if solution:
            # Update database records with assigned specialist
            for code, alloc in solution.items():
                t = db.query(TicketDB).filter(TicketDB.ticket_code == code).first()
                if t:
                    t.assigned_staff = alloc["assigned_staff_name"]
                    t.status = TicketStatus.IN_PROGRESS.value
            db.commit()

            # Record audit log
            audit = AgentAuditLogDB(
                ticket_id=None,
                agent_name="GrievanceCSPDispatchAgent",
                module_reference="Module IV: CSP Backtracking & Forward Checking",
                action="BATCH_STAFF_DISPATCH_OPTIMAL_CSP",
                inputs={"tickets_count": len(active_tickets)},
                outputs={"allocated_count": len(solution)},
                reasoning=f"Solved CSP for {len(solution)} tickets in {telemetry['constraint_checks']} constraint checks with {telemetry['backtracks']} backtracks."
            )
            db.add(audit)
            db.commit()

        return solution, telemetry

