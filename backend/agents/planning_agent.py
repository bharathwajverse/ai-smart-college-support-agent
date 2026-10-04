"""
Module III & VII: Informed Search & State Space Planning Agent.
Implements an A* Search Planning Algorithm with STRIPS-like Operators
to dynamically synthesize optimal grievance resolution action plans.
"""

import heapq
from typing import Dict, Any, List, Tuple


class PlanningAction:
    def __init__(
        self,
        name: str,
        actor: str,
        preconditions: Dict[str, Any],
        effects: Dict[str, Any],
        cost_hours: float,
        description: str
    ):
        self.name = name
        self.actor = actor
        self.preconditions = preconditions
        self.effects = effects
        self.cost_hours = cost_hours
        self.description = description

    def is_applicable(self, state: Dict[str, Any]) -> bool:
        """Checks if current state satisfies all preconditions."""
        for k, v in self.preconditions.items():
            if state.get(k) != v:
                return False
        return True

    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Applies effects to produce a successor state."""
        new_state = dict(state)
        for k, v in self.effects.items():
            new_state[k] = v
        return new_state


class StateSpacePlanningAgent:
    """
    Goal-based planning agent using A* Search (Module III & VII).
    Finds the shortest, lowest-cost sequence of institutional actions
    to transition a ticket from SUBMITTED to RESOLVED.
    """

    def __init__(self):
        self._init_operators()

    def _init_operators(self):
        """Define institutional action operators with preconditions and effects."""
        self.operators = [
            PlanningAction(
                name="VerifyGrievance",
                actor="Department Desk Coordinator",
                preconditions={"verified": False},
                effects={"verified": True},
                cost_hours=0.5,
                description="Cross-examine student identity, student record, and complaint validity."
            ),
            PlanningAction(
                name="EscalateDeanEmergency",
                actor="Chief Proctor / Dean of Student Welfare",
                preconditions={"verified": True, "requires_dean_alert": True, "dean_alerted": False},
                effects={"dean_alerted": True},
                cost_hours=0.2,
                description="Trigger immediate confidential alert to Dean & convene emergency committee."
            ),
            PlanningAction(
                name="DispatchSpecialist",
                actor="Department Head",
                preconditions={"verified": True, "specialist_assigned": False},
                effects={"specialist_assigned": True},
                cost_hours=1.0,
                description="Assign designated field engineer, warden, or academic counselor."
            ),
            PlanningAction(
                name="ProcureReplacementEquipment",
                actor="Store & Inventory Logistics",
                preconditions={
                    "specialist_assigned": True,
                    "requires_parts": True,
                    "parts_ready": False
                },
                effects={"parts_ready": True},
                cost_hours=3.5,
                description="Requisition and issue replacement hardware, plumbing, or lab components."
            ),
            PlanningAction(
                name="ExecuteCorrectiveAction",
                actor="Field Specialist / Action Squad",
                preconditions={
                    "specialist_assigned": True,
                    "parts_ready": True,
                    "work_executed": False
                },
                effects={"work_executed": True},
                cost_hours=2.0,
                description="Carry out on-site repair, mess batch seizure, or academic record rectification."
            ),
            PlanningAction(
                name="ConductSupervisoryAudit",
                actor="Quality & Vigilance Officer",
                preconditions={"work_executed": True, "audited": False},
                effects={"audited": True},
                cost_hours=0.5,
                description="Inspect physical repair, test WiFi bandwidth, or verify updated ledger."
            ),
            PlanningAction(
                name="NotifyStudentAndCloseTicket",
                actor="Automated Student Notification Agent",
                preconditions={"audited": True, "student_notified": False},
                effects={"student_notified": True, "resolved": True},
                cost_hours=0.3,
                description="Dispatch resolution summary to student portal and request feedback rating."
            )
        ]

    def _state_key(self, state: Dict[str, Any]) -> Tuple:
        """Hashable representation of state fluents."""
        return tuple(sorted(state.items()))

    def _heuristic(self, state: Dict[str, Any], goal: Dict[str, Any]) -> float:
        """
        Admissible Heuristic h(n):
        Underestimates remaining cost by calculating unsatisfied goal fluents * minimum action cost.
        """
        unsatisfied_count = 0
        if not state.get("verified", False):
            unsatisfied_count += 0.5
        if state.get("requires_dean_alert", False) and not state.get("dean_alerted", False):
            unsatisfied_count += 0.2
        if not state.get("specialist_assigned", False):
            unsatisfied_count += 1.0
        if state.get("requires_parts", False) and not state.get("parts_ready", False):
            unsatisfied_count += 3.5
        if not state.get("work_executed", False):
            unsatisfied_count += 2.0
        if not state.get("audited", False):
            unsatisfied_count += 0.5
        if not state.get("resolved", False):
            unsatisfied_count += 0.3
        return round(unsatisfied_count, 2)

    def _is_goal_satisfied(self, state: Dict[str, Any], goal: Dict[str, Any]) -> bool:
        for k, v in goal.items():
            if state.get(k) != v:
                return False
        return True

    def generate_plan(
        self,
        category: str,
        priority: str,
        requires_parts: bool = False,
        requires_dean_alert: bool = False,
        search_mode: str = "astar"
    ) -> List[Dict[str, Any]]:
        """
        Runs State-Space Graph Search to find the optimal resolution path.
        search_mode:
          - 'astar': Module III & VII Informed Search f(n) = g(n) + h(n) with admissible heuristic.
          - 'ucs': Module II Uninformed Search (Uniform Cost Search) f(n) = g(n) with h(n) = 0.
        """
        plan, _ = self.search_with_telemetry(
            category=category,
            priority=priority,
            requires_parts=requires_parts,
            requires_dean_alert=requires_dean_alert,
            search_mode=search_mode
        )
        return plan

    def search_with_telemetry(
        self,
        category: str,
        priority: str,
        requires_parts: bool = False,
        requires_dean_alert: bool = False,
        search_mode: str = "astar"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes search and records FAI search benchmarks (nodes expanded, generated, branch factor).
        """
        # Define Initial State S0
        initial_state = {
            "verified": False,
            "requires_dean_alert": requires_dean_alert,
            "dean_alerted": False if requires_dean_alert else True,
            "specialist_assigned": False,
            "requires_parts": requires_parts,
            "parts_ready": False if requires_parts else True,
            "work_executed": False,
            "audited": False,
            "student_notified": False,
            "resolved": False
        }

        # Define Goal State G
        goal_state = {
            "resolved": True,
            "student_notified": True,
            "audited": True,
            "work_executed": True
        }
        if requires_dean_alert:
            goal_state["dean_alerted"] = True

        # Priority Queue: stores (f_cost, g_cost, sequence_id, current_state, path)
        frontier = []
        counter = 0
        is_informed = (search_mode.lower() == "astar")
        start_h = self._heuristic(initial_state, goal_state) if is_informed else 0.0
        heapq.heappush(frontier, (start_h, 0.0, counter, initial_state, []))

        visited_costs = {self._state_key(initial_state): 0.0}
        expansions = 0
        generated = 1

        while frontier and expansions < 500:
            f, g, _, current_state, path = heapq.heappop(frontier)
            expansions += 1

            if self._is_goal_satisfied(current_state, goal_state):
                # Goal reached! Format plan
                formatted_plan = []
                cum_hours = 0.0
                for i, action in enumerate(path, 1):
                    cum_hours += action.cost_hours
                    formatted_plan.append({
                        "step_number": i,
                        "action": action.name,
                        "actor": action.actor,
                        "estimated_time_hours": action.cost_hours,
                        "cumulative_hours": round(cum_hours, 1),
                        "description": action.description
                    })
                
                telemetry = {
                    "algorithm": "A* Search (Informed - Module III & VII)" if is_informed else "Uniform Cost Search (Uninformed - Module II)",
                    "heuristic_admissible": True,
                    "search_mode": search_mode,
                    "nodes_expanded": expansions,
                    "nodes_generated": generated,
                    "path_cost_hours": round(cum_hours, 2),
                    "total_steps": len(path),
                    "optimality_guarantee": "Provably Optimal"
                }
                return formatted_plan, telemetry

            # Expand successors using applicable operators
            for op in self.operators:
                if op.is_applicable(current_state):
                    next_state = op.apply(current_state)
                    next_key = self._state_key(next_state)
                    next_g = g + op.cost_hours

                    if next_key not in visited_costs or next_g < visited_costs[next_key]:
                        visited_costs[next_key] = next_g
                        h = self._heuristic(next_state, goal_state) if is_informed else 0.0
                        f = next_g + h
                        counter += 1
                        generated += 1
                        heapq.heappush(
                            frontier,
                            (f, next_g, counter, next_state, path + [op])
                        )

        # Fallback linear plan if state space cutoff
        fallback = [
            {"step_number": 1, "action": "VerifyGrievance", "actor": "Desk Officer", "estimated_time_hours": 0.5, "cumulative_hours": 0.5, "description": "Verify issue details."},
            {"step_number": 2, "action": "DispatchSpecialist", "actor": "Coordinator", "estimated_time_hours": 1.0, "cumulative_hours": 1.5, "description": "Assign responsible officer."},
            {"step_number": 3, "action": "ExecuteCorrectiveAction", "actor": "Support Team", "estimated_time_hours": 3.0, "cumulative_hours": 4.5, "description": "Resolve complaint."},
            {"step_number": 4, "action": "NotifyStudentAndCloseTicket", "actor": "AI Agent", "estimated_time_hours": 0.2, "cumulative_hours": 4.7, "description": "Notify student."}
        ]
        return fallback, {"algorithm": "Fallback", "nodes_expanded": expansions, "nodes_generated": generated}

