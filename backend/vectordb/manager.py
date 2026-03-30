"""
Vector Database Manager using ChromaDB + Sentence Transformers

This replaces the old TF-IDF + MongoDB approach with proper semantic embeddings
stored in a vector database for fast similarity search (RAG pipeline).
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Tuple, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger(__name__)


class VectorDBManager:
    """Manages the ChromaDB vector store for Mahabharata knowledge."""

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection = None
        self._initialized = False

    def initialize(self):
        """Load embedding model and connect to ChromaDB."""
        if self._initialized:
            return

        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        self._initialized = True
        count = self.collection.count()
        logger.info(f"ChromaDB initialized. Collection '{settings.CHROMA_COLLECTION_NAME}' has {count} documents.")

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def _doc_id(self, text: str, category: str) -> str:
        """Generate a stable document ID."""
        h = hashlib.md5(f"{category}:{text}".encode()).hexdigest()
        return f"{category}_{h[:12]}"

    # ── Ingestion ────────────────────────────────────
    def ingest_qa_pairs(self, items: List[Dict], category: str):
        """
        Ingest question-answer pairs from JSON data.
        Each item has 'queries' (list of questions) and 'answers'/'answer' (response text).
        """
        ids, documents, metadatas, embeddings = [], [], [], []

        for item in items:
            # Get the answer text
            answer = ""
            if "answers" in item and item["answers"]:
                answer = item["answers"][0] if isinstance(item["answers"], list) else item["answers"]
            elif "answer" in item and item["answer"]:
                answer = item["answer"]

            if not answer:
                continue

            queries = item.get("queries", [])
            # Get a title/name field for context
            title = (
                item.get("name", "")
                or item.get("scene_title", "")
                or item.get("place_name", "")
                or item.get("object_name", "")
                or item.get("theme", "")
                or item.get("system_name", "")
                or item.get("era_name", "")
                or item.get("species", "")
                or item.get("prophecy_title", "")
                or item.get("riddle", "")
                or item.get("culture_event", "")
                or item.get("comparison", "")
                or item.get("title", "")
                or ""
            )

            # Index the answer itself as a document
            doc_id = self._doc_id(answer[:200], category)
            if doc_id not in ids:
                combined_text = f"{title}. {answer}" if title else answer
                ids.append(doc_id)
                documents.append(combined_text)
                metadatas.append({
                    "category": category,
                    "title": title,
                    "answer": answer[:4000],
                    "type": "qa_answer",
                    "queries": json.dumps(queries[:5]),
                })

            # Also index each query pointing to the answer
            for q in queries:
                q_id = self._doc_id(q, category)
                if q_id not in ids:
                    ids.append(q_id)
                    documents.append(q)
                    metadatas.append({
                        "category": category,
                        "title": title,
                        "answer": answer[:4000],
                        "type": "qa_query",
                        "queries": json.dumps([q]),
                    })

        if ids:
            embs = self.embed(documents)
            # Batch upsert (ChromaDB has a limit of ~5000 per call)
            batch_size = 500
            for i in range(0, len(ids), batch_size):
                self.collection.upsert(
                    ids=ids[i:i+batch_size],
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    embeddings=embs[i:i+batch_size],
                )
            logger.info(f"Ingested {len(ids)} documents for category '{category}'")

    def ingest_text_chunks(self, chunks: List[str], category: str = "mahabharata_text",
                           source: str = "mahabharata.txt"):
        """Ingest plain text chunks (from the Mahabharata text file)."""
        ids, documents, metadatas, embeddings = [], [], [], []

        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) < 30:
                continue
            doc_id = self._doc_id(chunk[:200], f"{category}_{i}")
            ids.append(doc_id)
            documents.append(chunk)
            metadatas.append({
                "category": category,
                "title": f"Mahabharata Text - Chunk {i+1}",
                "answer": chunk[:4000],
                "type": "text_chunk",
                "source": source,
                "queries": "[]",
            })

        if ids:
            embs = self.embed(documents)
            batch_size = 500
            for i in range(0, len(ids), batch_size):
                self.collection.upsert(
                    ids=ids[i:i+batch_size],
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    embeddings=embs[i:i+batch_size],
                )
            logger.info(f"Ingested {len(ids)} text chunks from '{source}'")

    # ── Retrieval ────────────────────────────────────
    def search(self, query: str, top_k: int = None, category_filter: str = None) -> List[Dict]:
        """
        Semantic search: embed the query and find the top-k most similar documents.
        Returns list of {text, category, title, answer, similarity, type}.
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS

        query_embedding = self.embed([query])[0]

        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # ChromaDB cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity: 1 - (distance / 2)
                similarity = 1.0 - (distance / 2.0)

                meta = results["metadatas"][0][i]
                output.append({
                    "text": results["documents"][0][i],
                    "category": meta.get("category", "unknown"),
                    "title": meta.get("title", ""),
                    "answer": meta.get("answer", ""),
                    "similarity": round(similarity, 4),
                    "type": meta.get("type", "unknown"),
                })

        return output

    def get_stats(self) -> Dict:
        """Return collection statistics."""
        count = self.collection.count() if self.collection else 0
        return {
            "total_documents": count,
            "embedding_model": settings.EMBEDDING_MODEL,
            "persist_dir": settings.CHROMA_PERSIST_DIR,
            "collection_name": settings.CHROMA_COLLECTION_NAME,
        }


# Singleton instance
vector_db = VectorDBManager()
