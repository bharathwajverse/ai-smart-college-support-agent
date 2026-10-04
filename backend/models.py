"""
Data models and schemas for Smart College Support and Complaint Management Agent.
Compliant with Pydantic v2 and SQLAlchemy 2.0.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, JSON
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TicketCategory(str, Enum):
    ACADEMICS = "Academics"
    HOSTEL = "Hostel"
    MESS = "Mess & Canteen"
    IT_FACILITIES = "IT & Infrastructure"
    ACCOUNTS_FEE = "Accounts & Fees"
    LIBRARY = "Library"
    ANTI_RAGGING = "Anti-Ragging & Safety"
    TRANSPORT = "Transport"
    EXAMINATIONS = "Examinations"
    GENERAL = "General"


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EMERGENCY = "Emergency"


class TicketStatus(str, Enum):
    SUBMITTED = "Submitted"
    TRIAGED = "Triaged"
    IN_PROGRESS = "In Progress"
    ESCALATED = "Escalated"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


# --- SQLAlchemy Models ---

class TicketDB(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_code = Column(String(32), unique=True, index=True)
    student_name = Column(String(128), default="Anonymous")
    student_id = Column(String(64), default="N/A")
    email = Column(String(128), default="")
    phone = Column(String(32), default="")
    is_anonymous = Column(Boolean, default=False)
    
    subject = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(128), default="")
    
    category = Column(String(64), nullable=False, default=TicketCategory.GENERAL.value)
    priority = Column(String(32), nullable=False, default=TicketPriority.MEDIUM.value)
    status = Column(String(32), nullable=False, default=TicketStatus.SUBMITTED.value)
    
    assigned_department = Column(String(128), default="")
    assigned_staff = Column(String(128), default="Auto-Dispatch Queue")
    sla_hours = Column(Integer, default=48)
    
    # AI Agent Diagnostics
    bayesian_urgency_score = Column(Float, default=0.5)
    escalation_risk = Column(Float, default=0.2)
    sentiment_score = Column(Float, default=0.0)
    cluster_id = Column(String(64), nullable=True)
    is_master_incident = Column(Boolean, default=False)
    
    # Stored as JSON
    extracted_entities = Column(JSON, default=dict)
    rules_triggered = Column(JSON, default=list)
    resolution_plan = Column(JSON, default=list)
    agent_reasoning = Column(JSON, default=dict)
    ai_generated_response = Column(Text, default="")
    
    # Resolution & Feedback
    resolution_notes = Column(Text, default="")
    feedback_score = Column(Integer, nullable=True)
    feedback_comments = Column(Text, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class AgentAuditLogDB(Base):
    __tablename__ = "agent_audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, nullable=True)
    agent_name = Column(String(64), nullable=False)
    module_reference = Column(String(64), nullable=False)  # e.g., "Module I", "Module III"
    action = Column(String(128), nullable=False)
    inputs = Column(JSON, default=dict)
    outputs = Column(JSON, default=dict)
    reasoning = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)


# --- Pydantic Request / Response Schemas ---

class PlanStep(BaseModel):
    step_number: int
    action: str
    actor: str
    target_entity: str
    estimated_time_hours: float
    state_after: str
    heuristic_cost: float


class ComplaintCreate(BaseModel):
    student_name: Optional[str] = "Anonymous"
    student_id: Optional[str] = "N/A"
    email: Optional[str] = ""
    phone: Optional[str] = ""
    is_anonymous: Optional[bool] = False
    subject: str = Field(..., min_length=3, max_length=256)
    description: str = Field(..., min_length=10)
    category: Optional[str] = None
    location: Optional[str] = ""


class ComplaintResponse(BaseModel):
    id: int
    ticket_code: str
    student_name: str
    student_id: str
    subject: str
    description: str
    location: str
    category: str
    priority: str
    status: str
    assigned_department: str
    assigned_staff: str
    sla_hours: int
    bayesian_urgency_score: float
    escalation_risk: float
    cluster_id: Optional[str] = None
    is_master_incident: bool = False
    extracted_entities: Dict[str, Any] = {}
    rules_triggered: List[Dict[str, Any]] = []
    resolution_plan: List[Dict[str, Any]] = []
    agent_reasoning: Dict[str, Any] = {}
    ai_generated_response: str = ""
    created_at: Optional[Any] = None
    status_history: Optional[List[str]] = []

    model_config = {"from_attributes": True}


class SupportChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    student_context: Optional[Dict[str, Any]] = None


class SupportChatResponse(BaseModel):
    answer: str
    intent: str
    category: str
    matched_rules: List[str] = []
    confidence: float
    suggested_action: str
    escalation_required: bool = False


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
    notes: Optional[str] = ""
    staff_name: Optional[str] = "Admin Staff"


class FeedbackSubmit(BaseModel):
    satisfaction_score: int = Field(..., ge=1, le=5)
    comments: Optional[str] = ""


class AgentMetrics(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    escalated_tickets: int
    avg_resolution_sla_hours: float
    categories_distribution: Dict[str, int]
    priorities_distribution: Dict[str, int]
    incident_clusters_detected: int
    satisfaction_rating_avg: float
    fai_modules_active: List[str]
