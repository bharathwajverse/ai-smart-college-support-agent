"""
FastAPI Application Entrypoint for Smart College Support and Complaint Management Agent.
Serves REST API, AI Agent pipeline, and static frontend dashboard.
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from backend.database import init_db, get_db, SessionLocal
from backend.models import (
    TicketDB, AgentAuditLogDB,
    ComplaintCreate, ComplaintResponse,
    SupportChatRequest, SupportChatResponse,
    TicketUpdateStatus, FeedbackSubmit, AgentMetrics,
    TicketStatus
)
from backend.agents.orchestrator import CampusResolveOrchestrator
from backend.agents.peas_agent import PEASModel

# Initialize Database
init_db()

# Initialize AI Master Agent
orchestrator = CampusResolveOrchestrator()
peas_model = PEASModel()

app = FastAPI(
    title="CampusResolve AI - Smart College Support & Grievance Agent",
    description="Agentic grievance triage, A* resolution planning, Bayesian escalation estimation, and Knowledge-Based policy QA for FAI.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_initial_tickets_if_empty():
    """Seeds realistic sample campus tickets if DB is empty."""
    db = SessionLocal()
    try:
        count = db.query(TicketDB).count()
        if count == 0:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            seed_file = os.path.join(base_dir, "knowledge_base", "sample_tickets.json")
            if os.path.exists(seed_file):
                with open(seed_file, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                for item in samples:
                    # Run A* planner to seed plans for initial tickets
                    plan = orchestrator.planner.generate_plan(
                        category=item["category"],
                        priority=item["priority"],
                        requires_parts=item["category"] in ["IT & Infrastructure", "Hostel"],
                        requires_dean_alert=item["priority"] == "Emergency"
                    )
                    t = TicketDB(
                        ticket_code=item["ticket_code"],
                        student_name=item["student_name"],
                        student_id=item["student_id"],
                        email=item.get("email", ""),
                        phone=item.get("phone", ""),
                        is_anonymous=item.get("is_anonymous", False),
                        subject=item["subject"],
                        description=item["description"],
                        location=item.get("location", ""),
                        category=item["category"],
                        priority=item["priority"],
                        status=item.get("status", "Triaged"),
                        assigned_department=item.get("assigned_department", "Campus Admin"),
                        assigned_staff=item.get("assigned_staff", "Support Staff"),
                        sla_hours=item.get("sla_hours", 24),
                        bayesian_urgency_score=item.get("bayesian_urgency_score", 0.5),
                        escalation_risk=item.get("escalation_risk", 0.3),
                        cluster_id=item.get("cluster_id"),
                        is_master_incident=item.get("is_master_incident", False),
                        resolution_plan=plan,
                        ai_generated_response=f"Ticket {item['ticket_code']} registered and processed by CampusResolve AI.",
                        feedback_score=item.get("feedback_score"),
                        feedback_comments=item.get("feedback_comments", "")
                    )
                    db.add(t)
                db.commit()
    finally:
        db.close()

seed_initial_tickets_if_empty()


# --- REST API Endpoints ---

@app.post("/api/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def submit_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Submits a new student complaint and executes the autonomous multi-agent pipeline.
    """
    ticket = orchestrator.process_new_complaint(
        db=db,
        subject=payload.subject,
        description=payload.description,
        student_name=payload.student_name,
        student_id=payload.student_id,
        email=payload.email,
        phone=payload.phone,
        location=payload.location,
        user_category=payload.category,
        is_anonymous=payload.is_anonymous
    )
    return ticket


@app.get("/api/complaints", response_model=List[ComplaintResponse])
def get_complaints(
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    cluster_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve all complaints with optional filtering."""
    query = db.query(TicketDB)
    if category:
        query = query.filter(TicketDB.category == category)
    if status:
        query = query.filter(TicketDB.status == status)
    if priority:
        query = query.filter(TicketDB.priority == priority)
    if cluster_id:
        query = query.filter(TicketDB.cluster_id == cluster_id)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (TicketDB.subject.ilike(search_filter)) |
            (TicketDB.description.ilike(search_filter)) |
            (TicketDB.ticket_code.ilike(search_filter))
        )
    return query.order_by(TicketDB.created_at.desc()).all()


@app.get("/api/complaints/{id_or_code}", response_model=ComplaintResponse)
def get_complaint_detail(id_or_code: str, db: Session = Depends(get_db)):
    """Retrieve detailed information about a specific complaint by ID or ticket code."""
    if id_or_code.isdigit():
        ticket = db.query(TicketDB).filter(TicketDB.id == int(id_or_code)).first()
    else:
        ticket = db.query(TicketDB).filter(TicketDB.ticket_code == id_or_code).first()
        
    if not ticket:
        raise HTTPException(status_code=404, detail="Complaint ticket not found")
    return ticket


@app.patch("/api/complaints/{id_or_code}/status", response_model=ComplaintResponse)
def update_complaint_status(id_or_code: str, payload: TicketUpdateStatus, db: Session = Depends(get_db)):
    """Admin / Staff endpoint to transition ticket status in the workflow."""
    if id_or_code.isdigit():
        ticket = db.query(TicketDB).filter(TicketDB.id == int(id_or_code)).first()
    else:
        ticket = db.query(TicketDB).filter(TicketDB.ticket_code == id_or_code).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Complaint ticket not found")

    old_status = ticket.status
    ticket.status = payload.status.value
    if payload.notes:
        ticket.resolution_notes = f"{ticket.resolution_notes or ''}\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {payload.staff_name}: {payload.notes}".strip()
    if payload.status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    # Log action
    log = AgentAuditLogDB(
        ticket_id=ticket.id,
        agent_name="HumanStaffSupervisor",
        module_reference="Module I: Human-in-the-Loop Agent",
        action=f"STATUS_TRANSITION_{old_status}_TO_{ticket.status}",
        inputs={"previous": old_status, "new": ticket.status, "staff": payload.staff_name},
        outputs={"updated_status": ticket.status},
        reasoning=payload.notes or "Manual status update by campus authority."
    )
    db.add(log)
    db.commit()

    return ticket


@app.post("/api/complaints/{id_or_code}/feedback")
def submit_student_feedback(id_or_code: str, payload: FeedbackSubmit, db: Session = Depends(get_db)):
    """Student submits feedback rating (Module IX: Learning Agent feedback loop)."""
    if id_or_code.isdigit():
        ticket = db.query(TicketDB).filter(TicketDB.id == int(id_or_code)).first()
    else:
        ticket = db.query(TicketDB).filter(TicketDB.ticket_code == id_or_code).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Complaint ticket not found")

    ticket.feedback_score = payload.satisfaction_score
    ticket.feedback_comments = payload.comments
    db.commit()

    # Module IX: Learning Agent feedback audit log
    fb_log = AgentAuditLogDB(
        ticket_id=ticket.id,
        agent_name="StudentFeedbackLearningAgent",
        module_reference="Module IX: Learning Agents (Reward & Policy Feedback)",
        action="RECORD_SATISFACTION_REWARD",
        inputs={"satisfaction_score": payload.satisfaction_score, "comments": payload.comments},
        outputs={"recorded_score": payload.satisfaction_score},
        reasoning=f"Student provided {payload.satisfaction_score}/5 stars. Used for utility adaptation."
    )
    db.add(fb_log)
    db.commit()

    return {
        "status": "success",
        "message": "Feedback received. Thank you for helping CampusResolve AI learn and improve!",
        "feedback_score": payload.satisfaction_score
    }


@app.post("/api/csp/dispatch")
def run_csp_staff_dispatch(db: Session = Depends(get_db)):
    """
    Module IV: Constraint Satisfaction Problem (CSP) Staff Dispatch.
    Executes Backtracking Search with MRV, LCV, and Forward Checking
    to optimally assign duty specialists to active grievances.
    """
    solution, telemetry = orchestrator.assign_pending_tickets_csp(db)
    return {
        "assignments": solution or {},
        "telemetry": telemetry
    }


@app.post("/api/inference/backward-chain")
def test_backward_chain(payload: dict):
    """
    Module V: Goal-Driven Backward Chaining Inference.
    Evaluates whether a target goal (e.g. 'is_emergency', 'alert_dean') is proven.
    """
    goal = payload.get("goal", "is_emergency")
    facts = payload.get("facts", {})
    goal_value = payload.get("goal_value")
    result = orchestrator.inference_engine.backward_chain(goal, facts, goal_value)
    return result


@app.post("/api/planning/compare-search")
def compare_search_algorithms(payload: dict):
    """
    Module II vs Module III: Side-by-side comparison of Uninformed Search (UCS)
    vs Informed Search (A* Search with Admissible Heuristic).
    """
    category = payload.get("category", "Hostel")
    priority = payload.get("priority", "Emergency")
    requires_parts = payload.get("requires_parts", True)
    requires_dean_alert = payload.get("requires_dean_alert", True)

    astar_plan, astar_telemetry = orchestrator.planner.search_with_telemetry(
        category=category,
        priority=priority,
        requires_parts=requires_parts,
        requires_dean_alert=requires_dean_alert,
        search_mode="astar"
    )

    ucs_plan, ucs_telemetry = orchestrator.planner.search_with_telemetry(
        category=category,
        priority=priority,
        requires_parts=requires_parts,
        requires_dean_alert=requires_dean_alert,
        search_mode="ucs"
    )

    return {
        "scenario": {
            "category": category,
            "priority": priority,
            "requires_parts": requires_parts,
            "requires_dean_alert": requires_dean_alert
        },
        "astar_informed_search": {
            "telemetry": astar_telemetry,
            "plan_steps": astar_plan
        },
        "uniform_cost_search_uninformed": {
            "telemetry": ucs_telemetry,
            "plan_steps": ucs_plan
        },
        "academic_comparison": {
            "nodes_expanded_difference": f"A* expanded {astar_telemetry['nodes_expanded']} nodes vs UCS {ucs_telemetry['nodes_expanded']} nodes.",
            "search_pruning_efficiency": f"Heuristic h(n) pruned state space search by {max(0, ucs_telemetry['nodes_expanded'] - astar_telemetry['nodes_expanded'])} nodes."
        }
    }



@app.post("/api/chat", response_model=SupportChatResponse)
def support_chat(payload: SupportChatRequest):
    """Interactive AI Conversational Support (Module VI Knowledge Base & FAQ)."""
    result = orchestrator.handle_student_chat(query=payload.query, student_context=payload.student_context)
    return SupportChatResponse(
        answer=result.get("answer", "I am unable to answer this query at the moment."),
        intent=result.get("intent", "General"),
        category=result.get("category", "General"),
        confidence=result.get("confidence", 0.5),
        suggested_action=result.get("suggested_action", "Check FAQ or File Complaint"),
        escalation_required=result.get("escalation_required", False)
    )


@app.get("/api/metrics", response_model=AgentMetrics)
def get_metrics(db: Session = Depends(get_db)):
    """Aggregated analytical telemetry for administrative oversight and FAI evaluation."""
    tickets = db.query(TicketDB).all()
    total = len(tickets)
    open_count = sum(1 for t in tickets if t.status not in ["Resolved", "Closed"])
    resolved_count = sum(1 for t in tickets if t.status == "Resolved")
    escalated_count = sum(1 for t in tickets if t.status == "Escalated")
    
    avg_sla = round(sum(t.sla_hours for t in tickets) / max(total, 1), 1)

    cat_counts = {}
    pri_counts = {}
    ratings = []
    clusters = set()

    for t in tickets:
        cat_counts[t.category] = cat_counts.get(t.category, 0) + 1
        pri_counts[t.priority] = pri_counts.get(t.priority, 0) + 1
        if t.feedback_score:
            ratings.append(t.feedback_score)
        if t.cluster_id:
            clusters.add(t.cluster_id)

    avg_satisfaction = round(sum(ratings) / len(ratings), 2) if ratings else 4.6

    return AgentMetrics(
        total_tickets=total,
        open_tickets=open_count,
        resolved_tickets=resolved_count,
        escalated_tickets=escalated_count,
        avg_resolution_sla_hours=avg_sla,
        categories_distribution=cat_counts,
        priorities_distribution=pri_counts,
        incident_clusters_detected=len(clusters),
        satisfaction_rating_avg=avg_satisfaction,
        fai_modules_active=[
            "Module I: PEAS Specification & Utility Agent",
            "Module II: Uninformed Search Strategies (Uniform Cost Search)",
            "Module III: Informed Search Strategies (A* Search with Heuristics)",
            "Module IV: Constraint Satisfaction Problems (CSP Backtracking & MRV)",
            "Module V & VI: Logic Reasoning, Forward & Backward Chaining",
            "Module VII: State Space Planning (STRIPS-style Operators)",
            "Module VIII: Uncertainty in AI (Bayesian Networks)",
            "Module IX: Learning Agents (Reward Feedback & Clustering)",
            "Module X: AI in Governance & Campus Administration"
        ]
    )


@app.get("/api/fai-diagnostics")
def get_fai_diagnostics():
    """Returns transparent academic inspection data for examiners and students."""
    from backend.agents.dispatch_csp import GrievanceCSP
    sample_csp = GrievanceCSP(tickets=[])

    return {
        "peas_model": peas_model.to_dict(),
        "search_algorithms": {
            "uninformed": "Uniform Cost Search (UCS, Module II) - f(n) = g(n)",
            "informed": "A* Search (Module III & VII) - f(n) = g(n) + h(n)",
            "heuristic_property": "Admissible (underestimates true cost)",
        },
        "planning_operators": [
            {
                "name": op.name,
                "actor": op.actor,
                "preconditions": op.preconditions,
                "effects": op.effects,
                "cost_hours": op.cost_hours,
                "description": op.description
            }
            for op in orchestrator.planner.operators
        ],
        "csp_specification": {
            "module": "Module IV: Constraint Satisfaction Problems",
            "algorithm": "Backtracking Search + MRV + LCV + Forward Checking",
            "specialist_roster": [
                {
                    "staff_id": s.staff_id,
                    "name": s.name,
                    "department": s.department,
                    "categories": s.categories,
                    "capacity": s.max_capacity,
                    "senior_on_call": s.is_senior_on_call
                }
                for s in sample_csp.specialists
            ]
        },
        "inference_rule_base": orchestrator.inference_engine.rules,
        "inference_algorithms": ["Forward Chaining (Modus Ponens)", "Backward Chaining (Goal-Driven)"],
        "bayesian_model_parameters": {
            "category_priors": orchestrator.bayesian.category_priors,
            "likelihood_distributions": orchestrator.bayesian.likelihoods
        }
    }



# Mount Static Frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
