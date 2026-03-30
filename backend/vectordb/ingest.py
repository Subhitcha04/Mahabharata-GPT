"""
Data Ingestion Pipeline

Loads all Mahabharata data (JSON Q&A pairs + text chunks) into ChromaDB.
Run once on first setup, or whenever data changes.
"""

import os
import json
import re
import logging

from config import settings
from vectordb.manager import vector_db

logger = logging.getLogger(__name__)

# Mapping of JSON file -> (key in JSON, category name)
JSON_SOURCES = {
    "comparison.json": ("queries", "Comparison"),
    "creatures.json": ("creatures", "CreatureOrSpecies"),
    "cultural_events.json": ("cultural_events", "CulturalOrHistorical"),
    "mythology_eras.json": ("mythology_eras", "MythologyEra"),
    "mythology_systems.json": ("mythology_systems", "MythologySystem"),
    "objects.json": ("objects", "ObjectOrArtifact"),
    "places.json": ("places", "PlaceOrLocation"),
    "prophecies.json": ("prophecies", "ProphecyOrFate"),
    "riddles.json": ("riddles", "RiddleOrPuzzle"),
    "scenes.json": ("scenes_or_incidents", "SceneOrIncident"),
    "themes.json": ("themes", "ThemeOrMoral"),
}


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """
    Split text into overlapping chunks for better retrieval.
    Uses story boundaries (~ markers) when available.
    """
    chunks = []

    # Try to split by story markers first (the ~ X ~ pattern)
    stories = re.split(r'\n~\s*\d+\.', text)

    if len(stories) > 5:
        # We have story-level chunks
        current_chunk = ""
        for story in stories:
            story = story.strip()
            if not story:
                continue

            if len(current_chunk) + len(story) < chunk_size:
                current_chunk += "\n\n" + story
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = story

        if current_chunk.strip():
            chunks.append(current_chunk.strip())
    else:
        # Fall back to paragraph-based chunking
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += "\n\n" + para
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # Keep some overlap
                words = current_chunk.split()
                overlap_text = " ".join(words[-overlap//5:]) if len(words) > overlap//5 else ""
                current_chunk = overlap_text + "\n\n" + para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

    return chunks


def ingest_all_data():
    """Main ingestion function - loads everything into ChromaDB."""
    vector_db.initialize()

    logger.info("=" * 60)
    logger.info("Starting data ingestion into ChromaDB")
    logger.info("=" * 60)

    total_docs = 0

    # 1. Ingest JSON Q&A data
    for filename, (json_key, category) in JSON_SOURCES.items():
        filepath = os.path.join(settings.DATA_DIR, filename)
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data.get(json_key, data) if isinstance(data, dict) else data
            if isinstance(items, list):
                vector_db.ingest_qa_pairs(items, category)
                total_docs += len(items)
                logger.info(f"  {filename}: {len(items)} items -> category '{category}'")
        except Exception as e:
            logger.error(f"  Error loading {filename}: {e}")

    # 2. Ingest Mahabharata text
    text_path = os.path.join(settings.DATA_DIR, "mahabharata.txt")
    if os.path.exists(text_path):
        try:
            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = chunk_text(text, chunk_size=600, overlap=100)
            vector_db.ingest_text_chunks(chunks, category="MahabharataText", source="mahabharata.txt")
            total_docs += len(chunks)
            logger.info(f"  mahabharata.txt: {len(chunks)} chunks ingested")
        except Exception as e:
            logger.error(f"  Error loading mahabharata.txt: {e}")

    stats = vector_db.get_stats()
    logger.info("=" * 60)
    logger.info(f"Ingestion complete. Total vectors in ChromaDB: {stats['total_documents']}")
    logger.info("=" * 60)

    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_all_data()
