"""
Module III & IX: Duplicate Detection, Similarity Search & Incident Clustering Agent.
Identifies recurring campus-wide issues (e.g. WiFi outage across hostel floors, mess food issues)
using TF-IDF vectorization and Cosine Similarity.
"""

from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DuplicateDetectionAgent:
    """
    Search and Clustering Agent:
    Clusters semantically related student grievances to prevent redundant staff dispatch.
    """

    def __init__(self, similarity_threshold: float = 0.58):
        self.similarity_threshold = similarity_threshold

    def find_similar_tickets(
        self,
        new_subject: str,
        new_description: str,
        new_category: str,
        existing_tickets: List[Dict[str, Any]],
        new_location: str = ""
    ) -> Tuple[Optional[Dict[str, Any]], float, List[Dict[str, Any]]]:
        """
        Compares new ticket against open/active existing tickets.
        Returns: (best_matching_ticket, max_similarity, list_of_close_matches)
        """
        # Filter candidate tickets by category or location to prune search space (informed search)
        candidates = [
            t for t in existing_tickets
            if t.get("status") in ["Submitted", "Triaged", "In Progress", "Escalated"]
        ]

        if not candidates:
            return None, 0.0, []

        new_doc = f"{new_subject} {new_description}"
        corpus = [f"{t.get('subject', '')} {t.get('description', '')}" for t in candidates]

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([new_doc] + corpus)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        except Exception:
            return None, 0.0, []

        close_matches = []
        best_match = None
        max_sim = 0.0

        for idx, sim in enumerate(similarities):
            sim_val = round(float(sim), 3)
            # Boost similarity if category matches
            if candidates[idx].get("category") == new_category:
                sim_val = min(1.0, sim_val + 0.10)

            # Spatial match boost: if both tickets share the same specific location
            cand_loc = (candidates[idx].get("location") or "").lower()
            if new_location and cand_loc and len(cand_loc) > 3:
                if any(w in cand_loc for w in new_location.lower().split() if len(w) > 4):
                    sim_val = min(1.0, sim_val + 0.08)

            if sim_val >= self.similarity_threshold:
                close_matches.append({
                    "ticket_code": candidates[idx].get("ticket_code"),
                    "subject": candidates[idx].get("subject"),
                    "similarity": sim_val,
                    "cluster_id": candidates[idx].get("cluster_id")
                })
                if sim_val > max_sim:
                    max_sim = sim_val
                    best_match = candidates[idx]

        return best_match, max_sim, close_matches

