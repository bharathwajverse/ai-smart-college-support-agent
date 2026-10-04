"""
Classifier Agent: Natural Language Processing, Category Assignment,
and Entity Extraction for Campus Grievance Intake.
"""

import re
import json
import os
from typing import Dict, Any, Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ClassifierAgent:
    def __init__(self, rules_path: str = None):
        if rules_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "knowledge_base", "college_rules.json")
            
        with open(rules_path, "r", encoding="utf-8") as f:
            self.knowledge = json.load(f)
            
        self.categories_meta = self.knowledge.get("categories", [])
        self._init_vectorizer()

    def _init_vectorizer(self):
        """Build reference document vectors for each category using category keywords."""
        self.cat_names = [cat["name"] for cat in self.categories_meta]
        self.cat_corpus = [
            f"{cat['name']} {' '.join(cat['keywords'])} {cat['department']}"
            for cat in self.categories_meta
        ]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.category_vectors = self.vectorizer.fit_transform(self.cat_corpus)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract structured campus entities using regex and linguistic rules."""
        entities = {}

        # 1. Roll Number / Student ID (e.g. 21CS042, 22EC104, 2021BCSE001)
        roll_pattern = r"\b(20\d{2}[A-Z]{2,4}\d{2,4}|\d{2}[A-Z]{2,4}\d{2,4})\b"
        roll_match = re.search(roll_pattern, text, re.IGNORECASE)
        if roll_match:
            entities["detected_student_id"] = roll_match.group(1).upper()

        # 2. Location (Hostels, Blocks, Mess, Labs, Rooms)
        locations = []
        loc_patterns = [
            r"\b((?:Shivalik|Nilgiri|Aravalli|Vindhya|Satpura|Ganga|Yamuna|Kaveri)\s+(?:Hostel|Bhawan|Block(?:\s+[A-Z])?))\b",
            r"\b(Room\s*(?:No\.?)?\s*\d{2,4}[A-Za-z]?)\b",
            r"\b(Floor\s*\d|\d+(?:st|nd|rd|th)\s*floor)\b",
            r"\b(Annapurna\s+(?:Mess|Canteen)|Central\s+Mess|Hostel\s+Mess)\b",
            r"\b(Lab\s*(?:No\.?)?\s*\d{2,4}|Computer\s+Centre|Admin\s+Block|Library|Sports\s+Complex)\b"
        ]
        for pat in loc_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                locations.append(m.strip())
        if locations:
            entities["detected_locations"] = list(dict.fromkeys(locations))

        # 3. Transaction / UTR numbers
        utr_pattern = r"\b(UTR\s*[:#-]?\s*[A-Z0-9]{8,18}|TXN\s*[:#-]?\s*[A-Z0-9]{8,18})\b"
        utr_match = re.search(utr_pattern, text, re.IGNORECASE)
        if utr_match:
            entities["transaction_ref"] = utr_match.group(1)

        # 4. Phone numbers
        phone_pattern = r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b"
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            entities["phone_number"] = phone_match.group(0)

        # 5. Distress / Urgency markers
        urgency_markers = [
            "emergency", "urgent", "immediate", "ragging", "threat", "danger",
            "hospital", "severe", "asap", "vomiting", "bleeding", "food poisoning"
        ]
        detected_urgency = [word for word in urgency_markers if re.search(r"\b" + word + r"\b", text, re.IGNORECASE)]
        if detected_urgency:
            entities["urgency_cues"] = detected_urgency

        return entities

    def compute_sentiment(self, text: str) -> float:
        """
        Lightweight lexical sentiment calculation:
        Returns value between -1.0 (highly distressed/negative) and +1.0 (calm/positive).
        """
        text_lower = text.lower()
        negative_lexicon = [
            "terrible", "awful", "horrible", "disaster", "danger", "harass",
            "threat", "worst", "unacceptable", "sick", "pain", "failed", "broken",
            "useless", "emergency", "poisoning", "retaliation", "distress"
        ]
        positive_lexicon = [
            "please", "kindly", "request", "help", "thank", "grateful",
            "appreciate", "resolved", "good", "courteous"
        ]
        
        neg_count = sum(1 for w in negative_lexicon if w in text_lower)
        pos_count = sum(1 for w in positive_lexicon if w in text_lower)
        
        total = neg_count + pos_count
        if total == 0:
            return 0.0
        return round((pos_count - neg_count) / max(total, 1), 2)

    def classify(self, subject: str, description: str, user_category: str = None) -> Tuple[str, float, Dict[str, Any]]:
        """
        Classifies the complaint into an institutional category.
        Returns: (best_category_name, confidence, diagnostic_metadata)
        """
        full_text = f"{subject} {description}".strip()
        entities = self.extract_entities(full_text)
        sentiment = self.compute_sentiment(full_text)

        # Safety override: If anti-ragging or safety cues are strongly present, classify as Anti-Ragging
        safety_words = ["ragging", "harassment", "bully", "threatened", "forced to strip", "assault"]
        if any(w in full_text.lower() for w in safety_words):
            return "Anti-Ragging & Safety", 0.99, {
                "method": "Safety Rule Override",
                "entities": entities,
                "sentiment": sentiment,
                "department": "Proctorial Board & Anti-Ragging Cell"
            }

        # Vector similarity matching
        query_vec = self.vectorizer.transform([full_text])
        similarities = cosine_similarity(query_vec, self.category_vectors)[0]

        # Apply specific domain keyword boosts
        text_lower = full_text.lower()
        scored_cats = []
        for idx, cat_name in enumerate(self.cat_names):
            sim = float(similarities[idx])
            cat_meta = next((c for c in self.categories_meta if c["name"] == cat_name), {})
            kw_hits = sum(1 for kw in cat_meta.get("keywords", []) if re.search(r"\b" + re.escape(kw) + r"\b", text_lower))
            # If primary technical keyword like wifi/router/internet matches for IT, boost
            if cat_name == "IT & Infrastructure" and any(k in text_lower for k in ["wifi", "wi-fi", "internet", "router", "lan", "erp"]):
                sim += 0.35
            elif cat_name == "Mess & Canteen" and any(k in text_lower for k in ["food", "mess", "canteen", "lunch", "dinner", "dal"]):
                sim += 0.30
            elif cat_name == "Accounts & Fees" and any(k in text_lower for k in ["fee", "fees", "refund", "receipt", "deducted twice", "challan"]):
                sim += 0.30
            elif cat_name == "Examinations" and any(k in text_lower for k in ["exam", "hall ticket", "admit card", "re-evaluation", "marksheet"]):
                sim += 0.30

            total_score = sim + (kw_hits * 0.05)
            scored_cats.append((total_score, cat_name, sim))

        scored_cats.sort(key=lambda x: x[0], reverse=True)
        best_score, best_cat_name, best_sim = scored_cats[0]
        best_confidence = min(1.0, float(best_score))

        # If similarity is negligible across all domains and no keywords matched, default to General
        if best_confidence < 0.12 and not user_category:
            best_cat_name = "General"
            best_confidence = 0.45

        # If user explicitly specified category, validate or reconcile
        if user_category and user_category in self.cat_names:
            best_cat_name = user_category
            best_confidence = max(best_confidence, 0.6)

        matched_meta = next((c for c in self.categories_meta if c["name"] == best_cat_name), {})

        diagnostics = {
            "method": "TF-IDF Vector Space Classifier",
            "confidence": round(best_confidence, 3),
            "department": matched_meta.get("department", "General Administration"),
            "default_sla_hours": matched_meta.get("default_sla_hours", 48),
            "entities": entities,
            "sentiment": sentiment
        }

        return best_cat_name, round(best_confidence, 3), diagnostics
