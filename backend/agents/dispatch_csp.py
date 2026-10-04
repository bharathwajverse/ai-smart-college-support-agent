"""
Module IV: Defining Constraint Satisfaction Problems (CSPs),
Constraint Propagation, and Backtracking Search for Institutional Staff Dispatch.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import copy


class Specialist:
    """Institutional Staff / Specialist Entity."""
    def __init__(
        self,
        staff_id: str,
        name: str,
        department: str,
        categories: List[str],
        max_capacity: int = 2,
        is_senior_on_call: bool = False,
        jurisdiction: Optional[str] = None
    ):
        self.staff_id = staff_id
        self.name = name
        self.department = department
        self.categories = categories
        self.max_capacity = max_capacity
        self.is_senior_on_call = is_senior_on_call
        self.jurisdiction = jurisdiction  # e.g. "Shivalik Hostel", "Nilgiri Hostel", "Campus-Wide"


class GrievanceCSP:
    """
    Formal Constraint Satisfaction Problem Formulation (Module IV).
    Variables: List of Ticket IDs needing assignment.
    Domains: Set of eligible specialists.
    Constraints:
      1. Qualification Constraint (Category match)
      2. Capacity Constraint (Max workload per specialist)
      3. Seniority / Emergency Clearance Constraint (Emergency requires senior on-call officer)
      4. Spatial Jurisdiction Constraint (Hostel-specific jurisdiction matching)
    """

    def __init__(self, tickets: List[Dict[str, Any]], specialists: Optional[List[Specialist]] = None):
        self.tickets = {t["ticket_code"]: t for t in tickets}
        self.variables = list(self.tickets.keys())

        if specialists is None:
            self.specialists = self._default_roster()
        else:
            self.specialists = specialists

        self.specialist_dict = {s.staff_id: s for s in self.specialists}

        # Initialize Domains D(Xi)
        self.domains: Dict[str, List[str]] = {}
        for var in self.variables:
            ticket = self.tickets[var]
            legal_specialists = []
            for s in self.specialists:
                if self._is_initially_eligible(ticket, s):
                    legal_specialists.append(s.staff_id)
            self.domains[var] = legal_specialists

        self.backtrack_count = 0
        self.constraint_checks = 0

    def _default_roster(self) -> List[Specialist]:
        """Default campus staff roster for institutional triage."""
        return [
            Specialist("STF_PROCTOR_01", "Prof. R. S. Rathore (Chief Proctor)", "Proctorial Board", ["Anti-Ragging & Safety"], max_capacity=2, is_senior_on_call=True),
            Specialist("STF_PROCTOR_02", "Dr. Shalini Gupta (Anti-Ragging Cell)", "Proctorial Board", ["Anti-Ragging & Safety"], max_capacity=2, is_senior_on_call=True),
            Specialist("STF_NET_01", "Er. Vikram Singh (Senior Network Eng.)", "IT & Infrastructure", ["IT & Infrastructure"], max_capacity=3, is_senior_on_call=True),
            Specialist("STF_NET_02", "Pooja Deshmukh (Systems Admin)", "IT & Infrastructure", ["IT & Infrastructure"], max_capacity=2, is_senior_on_call=False),
            Specialist("STF_HOSTEL_01", "Dr. A. K. Nair (Shivalik Warden)", "Hostel Administration", ["Hostel"], max_capacity=2, is_senior_on_call=True, jurisdiction="Shivalik"),
            Specialist("STF_HOSTEL_02", "Dr. M. Roy (Nilgiri Warden)", "Hostel Administration", ["Hostel"], max_capacity=2, is_senior_on_call=True, jurisdiction="Nilgiri"),
            Specialist("STF_HOSTEL_03", "K. Ramamurthy (Campus Estate Eng.)", "Hostel Administration", ["Hostel"], max_capacity=3, is_senior_on_call=False, jurisdiction="Campus-Wide"),
            Specialist("STF_MESS_01", "Dr. Sunita Rao (Health & Food Inspector)", "Mess & Canteen", ["Mess & Canteen"], max_capacity=2, is_senior_on_call=True),
            Specialist("STF_MESS_02", "G. Parthasarathy (Catering Supervisor)", "Mess & Canteen", ["Mess & Canteen"], max_capacity=3, is_senior_on_call=False),
            Specialist("STF_ACAD_01", "Prof. Meenakshi (Academic Dean's Desk)", "Academic Affairs", ["Academics"], max_capacity=3, is_senior_on_call=True),
            Specialist("STF_EXAM_01", "R. K. Tyagi (Controller of Exams Staff)", "Examinations", ["Examinations"], max_capacity=3, is_senior_on_call=True),
            Specialist("STF_ACC_01", "Subhash Chandra (Senior Accounts Officer)", "Finance & Accounts", ["Accounts & Fees"], max_capacity=3, is_senior_on_call=True),
            Specialist("STF_GEN_01", "Ananya Sen (Student Welfare Helpdesk)", "General Administration", ["General", "Library", "Transport"], max_capacity=4, is_senior_on_call=False)
        ]

    def _is_initially_eligible(self, ticket: Dict[str, Any], specialist: Specialist) -> bool:
        """Unary constraint check for initial domain construction."""
        # 1. Category qualification
        cat = ticket.get("category", "")
        if cat not in specialist.categories:
            if not (cat in ["General", "Other", "Transport", "Library"] and "General" in specialist.categories):
                return False

        # 2. Emergency clearance
        pri = ticket.get("priority", "Medium")
        if pri == "Emergency" and not specialist.is_senior_on_call:
            return False

        # 3. Spatial jurisdiction check (if specific)
        loc = ticket.get("location", "")
        if specialist.jurisdiction and specialist.jurisdiction != "Campus-Wide":
            if specialist.jurisdiction.lower() not in loc.lower() and loc != "":
                return False

        return True

    def is_consistent(self, var: str, staff_id: str, assignment: Dict[str, str]) -> bool:
        """
        Binary / Global constraint verification:
        Ensures assigning specialist staff_id to var does not violate capacity limits.
        """
        self.constraint_checks += 1
        specialist = self.specialist_dict.get(staff_id)
        if not specialist:
            return False

        # Count current assignments of this specialist
        current_load = sum(1 for assigned_staff in assignment.values() if assigned_staff == staff_id)
        if current_load + 1 > specialist.max_capacity:
            return False

        return True

    def select_unassigned_variable_mrv(self, assignment: Dict[str, str], domains: Dict[str, List[str]]) -> str:
        """
        Minimum Remaining Values (MRV) Heuristic:
        Selects the unassigned variable with the fewest legal values in its domain (Fail-First principle).
        Tie-breaker: Degree heuristic (highest degree / most constraints).
        """
        unassigned = [v for v in self.variables if v not in assignment]
        # Sort by (domain_size, -degree)
        return min(
            unassigned,
            key=lambda v: (
                len(domains.get(v, [])),
                -1 if self.tickets[v].get("priority") == "Emergency" else 0
            )
        )

    def order_domain_values_lcv(self, var: str, domains: Dict[str, List[str]], assignment: Dict[str, str]) -> List[str]:
        """
        Least Constraining Value (LCV) Heuristic:
        Prioritizes the staff member that leaves the most capacity / options open for remaining variables.
        """
        values = domains.get(var, [])

        def remaining_capacity(staff_id: str) -> int:
            spec = self.specialist_dict.get(staff_id)
            if not spec:
                return 0
            used = sum(1 for assigned_staff in assignment.values() if assigned_staff == staff_id)
            return spec.max_capacity - used

        # Higher remaining capacity preferred first
        return sorted(values, key=remaining_capacity, reverse=True)

    def forward_check(
        self,
        var: str,
        assigned_staff: str,
        assignment: Dict[str, str],
        domains: Dict[str, List[str]]
    ) -> Optional[Dict[str, List[str]]]:
        """
        Forward Checking (Constraint Propagation - Module IV):
        Prunes the domains of unassigned variables. If assigned_staff reaches max capacity,
        removes assigned_staff from all other unassigned variables' domains.
        Returns pruned domains, or None if domain wipeout occurs.
        """
        new_domains = {v: list(vals) for v, vals in domains.items()}
        current_load = sum(1 for s in assignment.values() if s == assigned_staff) + 1
        spec = self.specialist_dict.get(assigned_staff)

        if spec and current_load >= spec.max_capacity:
            # Capacity exhausted: remove from all other unassigned variables
            for other_var in self.variables:
                if other_var not in assignment and other_var != var:
                    if assigned_staff in new_domains[other_var]:
                        new_domains[other_var].remove(assigned_staff)
                        # Check domain wipeout
                        if len(new_domains[other_var]) == 0:
                            return None  # Failure: domain wipeout

        return new_domains

    def solve(self) -> Tuple[Optional[Dict[str, Dict[str, Any]]], Dict[str, Any]]:
        """
        Executes Recursive Backtracking Search with MRV, LCV, and Forward Checking.
        Returns (solution_mapping, diagnostic_telemetry).
        """
        self.backtrack_count = 0
        self.constraint_checks = 0

        initial_assignment = {}
        solution = self._backtrack(initial_assignment, self.domains)

        if solution is None:
            return None, {
                "solved": False,
                "message": "Unable to assign all tickets within specialist capacity constraints.",
                "backtracks": self.backtrack_count,
                "constraint_checks": self.constraint_checks,
                "variables_count": len(self.variables)
            }

        # Format complete institutional assignment
        formatted_result = {}
        for var, staff_id in solution.items():
            spec = self.specialist_dict[staff_id]
            t = self.tickets[var]
            formatted_result[var] = {
                "ticket_code": var,
                "subject": t.get("subject"),
                "category": t.get("category"),
                "priority": t.get("priority"),
                "assigned_staff_id": staff_id,
                "assigned_staff_name": spec.name,
                "department": spec.department,
                "is_senior_on_call": spec.is_senior_on_call
            }

        telemetry = {
            "solved": True,
            "algorithm": "Backtracking Search + MRV + LCV + Forward Checking (Module IV)",
            "backtracks": self.backtrack_count,
            "constraint_checks": self.constraint_checks,
            "variables_count": len(self.variables),
            "specialists_utilized": len(set(solution.values())),
            "specialist_capacity_utilization": {
                spec.name: f"{sum(1 for s in solution.values() if s == spec.staff_id)} / {spec.max_capacity}"
                for spec in self.specialists if any(s == spec.staff_id for s in solution.values())
            }
        }
        return formatted_result, telemetry

    def _backtrack(
        self,
        assignment: Dict[str, str],
        domains: Dict[str, List[str]]
    ) -> Optional[Dict[str, str]]:
        """Internal recursive backtracking engine."""
        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_unassigned_variable_mrv(assignment, domains)
        ordered_values = self.order_domain_values_lcv(var, domains, assignment)

        for val in ordered_values:
            if self.is_consistent(var, val, assignment):
                assignment[var] = val

                # Forward check / constraint propagation
                pruned_domains = self.forward_check(var, val, assignment, domains)
                if pruned_domains is not None:
                    result = self._backtrack(assignment, pruned_domains)
                    if result is not None:
                        return result

                # Backtrack
                self.backtrack_count += 1
                del assignment[var]

        return None
