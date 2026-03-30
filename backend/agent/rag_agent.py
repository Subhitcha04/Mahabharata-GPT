"""
Mahabharata RAG Agent

This is the core intelligence module. It implements a Retrieval-Augmented Generation
pipeline using:
1. Query Understanding (intent + entity extraction via spaCy)
2. Semantic Retrieval (ChromaDB vector search)
3. Answer Synthesis (combines retrieved context into coherent answers)
4. Confidence Scoring (how sure we are about the answer)

This replaces the old TF-IDF + regex matching with proper semantic search.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple

import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from config import settings
from vectordb.manager import vector_db

logger = logging.getLogger(__name__)

# Download NLTK data quietly
for pkg in ['punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger',
            'averaged_perceptron_tagger_eng', 'wordnet']:
    nltk.download(pkg, quiet=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.info("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# ── Category definitions ─────────────────────────────
CATEGORIES = [
    "Character", "StoryOrEvent", "SceneOrIncident", "PlaceOrLocation",
    "ObjectOrArtifact", "ThemeOrMoral", "MythologySystem", "MythologyEra",
    "CreatureOrSpecies", "ProphecyOrFate", "Comparison", "CulturalOrHistorical",
    "RiddleOrPuzzle", "MahabharataText", "General"
]

# Keywords for category hinting
CATEGORY_KEYWORDS = {
    "Character": ["who", "character", "person", "king", "queen", "hero", "warrior",
                   "arjuna", "krishna", "bhishma", "draupadi", "duryodhana", "karna",
                   "yudhishthira", "bhima", "nakula", "sahadeva", "pandava", "kaurava",
                   "drona", "gandhari", "kunti", "shakuni", "vidura", "dhritarashtra"],
    "StoryOrEvent": ["story", "event", "tale", "happen", "narrative", "episode", "war",
                     "battle", "kurukshetra"],
    "SceneOrIncident": ["scene", "incident", "moment", "dice", "game", "disrobing",
                        "swayamvara"],
    "PlaceOrLocation": ["where", "place", "location", "kingdom", "city", "forest",
                        "hastinapura", "indraprastha", "kurukshetra"],
    "ObjectOrArtifact": ["weapon", "object", "artifact", "bow", "arrow", "chariot",
                         "gandiva", "chakra", "mace", "sword"],
    "ThemeOrMoral": ["theme", "moral", "lesson", "meaning", "dharma", "karma", "duty",
                     "righteousness"],
    "Comparison": ["compare", "difference", "versus", "vs", "similar", "between"],
    "CreatureOrSpecies": ["creature", "demon", "rakshasa", "naga", "asura", "deva",
                          "gandharva", "apsara"],
    "ProphecyOrFate": ["prophecy", "fate", "destiny", "curse", "boon", "prediction"],
    "MythologyEra": ["yuga", "era", "age", "dvapara", "kali", "satya", "treta"],
    "MythologySystem": ["pantheon", "cosmology", "veda", "vedic", "mythology system"],
    "CulturalOrHistorical": ["ritual", "ceremony", "yagna", "sacrifice", "cultural",
                             "historical", "festival"],
    "RiddleOrPuzzle": ["riddle", "puzzle", "question", "yaksha"],
}

# Intent patterns
INTENT_PATTERNS = {
    "who_is": r"^(who|whom)\s+(is|was|are|were)\s+",
    "what_is": r"^(what|which)\s+(is|was|are|were)\s+",
    "why": r"^why\s+",
    "how": r"^how\s+",
    "where": r"^where\s+",
    "when": r"^when\s+",
    "tell_me": r"^(tell|describe|explain|narrate)\s+",
    "list": r"^(list|name|enumerate)\s+",
    "compare": r"(compare|difference|versus|vs\.?)\s+",
}

# Greeting patterns
GREETING_PATTERNS = [
    r"^(hi|hello|hey|namaste|greetings|good\s*(morning|afternoon|evening))[\s!.?]*$",
    r"^(how are you|what\'?s up|sup)[\s!.?]*$",
]

GREETING_RESPONSES = [
    "Namaste! 🙏 I am the Mahabharata Knowledge Agent. Ask me anything about the great epic — characters, stories, battles, dharma, or any aspect of the Mahabharata. What would you like to explore?",
    "Welcome, seeker of knowledge! 🏹 I can help you understand the Mahabharata — from the rivalry of the Pandavas and Kauravas to the wisdom of Lord Krishna. What question burns in your mind?",
    "Greetings! 📜 I am here to guide you through the vast world of the Mahabharata. Ask me about characters, events, weapons, places, themes, or anything from the great epic!",
]

FAREWELL_PATTERNS = [
    r"^(bye|goodbye|see you|thanks|thank you|ok thanks|that\'?s all)[\s!.?]*$",
]

FAREWELL_RESPONSES = [
    "May dharma guide your path! 🙏 Feel free to return whenever you seek more wisdom from the Mahabharata.",
    "Farewell, seeker! Remember — as Krishna said, 'You have a right to perform your duties, but not to the fruits of your actions.' Come back anytime!",
]


class MahabharataAgent:
    """
    The main RAG agent for answering Mahabharata questions.
    
    Pipeline:
    1. Understand the query (intent, entities, category hint)
    2. Retrieve relevant documents from ChromaDB
    3. Synthesize a coherent answer from retrieved context
    4. Score confidence and provide sources
    """

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.conversation_context: Dict[str, List[Dict]] = {}  # conv_id -> recent messages

    def _detect_intent(self, query: str) -> str:
        """Detect the user's intent from the query pattern."""
        q_lower = query.lower().strip()

        for intent, pattern in INTENT_PATTERNS.items():
            if re.search(pattern, q_lower):
                return intent

        return "general"

    def _extract_entities(self, query: str) -> List[Dict]:
        """Extract named entities and noun phrases from the query."""
        doc = nlp(query)

        entities = []
        for ent in doc.ents:
            entities.append({"text": ent.text, "label": ent.label_})

        # Also grab noun chunks for mythology terms that spaCy might miss
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip().lower()
            # Skip if already captured or too generic
            if any(e["text"].lower() == chunk_text for e in entities):
                continue
            if chunk_text not in self.stop_words and len(chunk_text) > 2:
                entities.append({"text": chunk.text, "label": "NOUN_PHRASE"})

        return entities

    def _guess_category(self, query: str) -> Optional[str]:
        """Guess the most likely category based on keywords in the query."""
        q_lower = query.lower()
        scores = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in q_lower)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return None

    def _is_greeting(self, query: str) -> bool:
        q_lower = query.lower().strip()
        return any(re.match(p, q_lower) for p in GREETING_PATTERNS)

    def _is_farewell(self, query: str) -> bool:
        q_lower = query.lower().strip()
        return any(re.match(p, q_lower) for p in FAREWELL_PATTERNS)

    def _synthesize_answer(self, query: str, results: List[Dict], intent: str,
                           entities: List[Dict]) -> Tuple[str, str, List[Dict]]:
        """
        Synthesize a final answer from retrieved results.
        Returns (answer_text, confidence_level, source_list).
        """
        if not results:
            return (
                "I couldn't find specific information about that in my Mahabharata knowledge base. "
                "Could you rephrase your question or ask about a specific character, event, or concept from the epic?",
                "low",
                []
            )

        top = results[0]
        top_sim = top["similarity"]

        # Collect unique answers from top results
        seen_answers = set()
        relevant_answers = []
        sources = []

        for r in results:
            answer_text = r.get("answer", r.get("text", ""))
            if not answer_text:
                continue

            # Deduplicate by checking content overlap
            answer_key = answer_text[:100].lower()
            if answer_key in seen_answers:
                continue
            seen_answers.add(answer_key)

            if r["similarity"] >= settings.SIMILARITY_THRESHOLD:
                relevant_answers.append({
                    "text": answer_text,
                    "title": r.get("title", ""),
                    "category": r.get("category", ""),
                    "similarity": r["similarity"],
                })
                sources.append({
                    "text": r.get("title", answer_text[:80]),
                    "category": r.get("category", "unknown"),
                    "similarity": r["similarity"],
                })

        if not relevant_answers:
            return (
                "I found some loosely related information, but I'm not confident it directly answers your question. "
                "Try being more specific — for example, ask about a particular character like Arjuna, "
                "an event like the Kurukshetra War, or a concept like Dharma.",
                "low",
                []
            )

        # Build the answer
        # If top result is very confident, use it directly
        if top_sim >= settings.HIGH_CONFIDENCE_THRESHOLD:
            main_answer = relevant_answers[0]["text"]
            confidence = "high"
        elif top_sim >= 0.50:
            main_answer = relevant_answers[0]["text"]
            confidence = "medium"
        else:
            # Combine multiple results for a richer answer
            parts = []
            for ra in relevant_answers[:3]:
                parts.append(ra["text"])
            main_answer = "\n\n".join(parts)
            confidence = "medium"

        # Add supplementary context if we have multiple good results
        if len(relevant_answers) > 1 and confidence != "low":
            supplementary = []
            for ra in relevant_answers[1:3]:
                if ra["similarity"] >= 0.40 and ra["text"] not in main_answer:
                    supp_text = ra["text"]
                    if len(supp_text) > 300:
                        supp_text = supp_text[:300] + "..."
                    supplementary.append(supp_text)

            if supplementary:
                main_answer += "\n\n**Additional Context:**\n" + "\n\n".join(supplementary)

        return main_answer, confidence, sources[:5]

    def analyze_query(self, query: str) -> Dict:
        """Full NLP analysis of the query (exposed for the API)."""
        doc = nlp(query)

        return {
            "intent": self._detect_intent(query),
            "entities": self._extract_entities(query),
            "category_hint": self._guess_category(query),
            "tokens": [t.text for t in doc],
            "pos_tags": [(t.text, t.pos_) for t in doc],
            "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
        }

    def answer(self, query: str, conversation_id: str = None) -> Dict:
        """
        Main entry point: answer a user's question about the Mahabharata.
        
        Returns: {
            answer: str,
            category: str,
            confidence: str,
            sources: list,
            analysis: dict,
        }
        """
        import random

        query = query.strip()
        if not query:
            return {
                "answer": "Please ask a question about the Mahabharata!",
                "category": "General",
                "confidence": "low",
                "sources": [],
                "analysis": {},
            }

        # Handle greetings
        if self._is_greeting(query):
            return {
                "answer": random.choice(GREETING_RESPONSES),
                "category": "General",
                "confidence": "high",
                "sources": [],
                "analysis": {"intent": "greeting"},
            }

        # Handle farewells
        if self._is_farewell(query):
            return {
                "answer": random.choice(FAREWELL_RESPONSES),
                "category": "General",
                "confidence": "high",
                "sources": [],
                "analysis": {"intent": "farewell"},
            }

        # Step 1: Analyze the query
        analysis = self.analyze_query(query)
        intent = analysis["intent"]
        entities = analysis["entities"]
        category_hint = analysis["category_hint"]

        # Step 2: Retrieve from vector DB
        # First try with category filter if we have a strong hint
        results = []
        if category_hint:
            results = vector_db.search(query, top_k=settings.TOP_K_RESULTS,
                                       category_filter=category_hint)

        # If category-filtered search didn't yield good results, search broadly
        if not results or (results and results[0]["similarity"] < 0.45):
            broad_results = vector_db.search(query, top_k=settings.TOP_K_RESULTS + 3)
            # Merge and deduplicate
            seen_ids = {r["text"][:50] for r in results}
            for br in broad_results:
                if br["text"][:50] not in seen_ids:
                    results.append(br)
                    seen_ids.add(br["text"][:50])
            # Re-sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:settings.TOP_K_RESULTS + 2]

        # Step 3: Synthesize answer
        answer_text, confidence, sources = self._synthesize_answer(
            query, results, intent, entities
        )

        # Determine the category from the best result
        category = "General"
        if results and results[0]["similarity"] >= settings.SIMILARITY_THRESHOLD:
            category = results[0].get("category", "General")

        return {
            "answer": answer_text,
            "category": category,
            "confidence": confidence,
            "sources": sources,
            "analysis": analysis,
        }


# Singleton
agent = MahabharataAgent()
