"""
Mahabharata AI Agent - FastAPI Backend

Enhanced version with:
- ChromaDB vector database for semantic search
- Sentence-transformer embeddings
- RAG (Retrieval-Augmented Generation) pipeline
- JWT authentication
- Conversation history
- SQLite for user data
"""

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from api.models import init_db, get_db, User, Conversation, Message, Feedback
from api.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_user
)
from api.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserProfile,
    ChatRequest, ChatResponse, SourceReference,
    ConversationSummary, ConversationDetail, MessageOut,
    FeedbackRequest, SystemStats
)
from vectordb.manager import vector_db
from vectordb.ingest import ingest_all_data
from agent.rag_agent import agent, CATEGORIES

# ── Logging ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ── FastAPI App ──────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="A RAG-powered AI agent for Mahabharata knowledge",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ──────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("Initializing database...")
    init_db()

    logger.info("Initializing vector database...")
    vector_db.initialize()

    # Check if we need to ingest data
    stats = vector_db.get_stats()
    if stats["total_documents"] < 10:
        logger.info("Vector DB appears empty. Running data ingestion...")
        ingest_all_data()
    else:
        logger.info(f"Vector DB has {stats['total_documents']} documents. Skipping ingestion.")

    logger.info("=" * 50)
    logger.info(f" {settings.APP_NAME} is ready!")
    logger.info(f" Vector DB: {stats['total_documents']} documents")
    logger.info(f" Embedding model: {settings.EMBEDDING_MODEL}")
    logger.info("=" * 50)


# ── Health Check ─────────────────────────────────────
@app.get("/api/health")
async def health():
    stats = vector_db.get_stats()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "vector_db_documents": stats["total_documents"],
        "embedding_model": stats["embedding_model"],
    }


# ── Auth Routes ──────────────────────────────────────
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Check existing
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=get_password_hash(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token, username=user.username, user_id=user.id)


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token, username=user.username, user_id=user.id)


@app.get("/api/auth/profile", response_model=UserProfile)
async def get_profile(user: User = Depends(require_user), db: Session = Depends(get_db)):
    conv_count = db.query(Conversation).filter(Conversation.user_id == user.id).count()
    msg_count = db.query(Message).join(Conversation).filter(Conversation.user_id == user.id).count()

    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        total_conversations=conv_count,
        total_messages=msg_count,
    )


# ── Chat Route (Main Agent Endpoint) ────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """
    Main chat endpoint. Sends a query to the RAG agent and returns the answer.
    Automatically manages conversation history.
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Get or create conversation
    conversation = None
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == user.id,
        ).first()

    if not conversation:
        # Create new conversation, use first ~40 chars of query as title
        title = query[:40] + ("..." if len(query) > 40 else "")
        conversation = Conversation(user_id=user.id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=query,
    )
    db.add(user_msg)

    # Run the RAG agent
    result = agent.answer(query, conversation_id=conversation.id)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"],
        sources=json.dumps(result["sources"]),
        confidence=result["confidence"],
        category=result["category"],
    )
    db.add(assistant_msg)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assistant_msg)

    # Build source references
    source_refs = [
        SourceReference(
            text=s.get("text", ""),
            category=s.get("category", ""),
            similarity=s.get("similarity", 0.0),
        )
        for s in result["sources"]
    ]

    return ChatResponse(
        answer=result["answer"],
        conversation_id=conversation.id,
        message_id=assistant_msg.id,
        sources=source_refs,
        category=result["category"],
        confidence=result["confidence"],
        analysis=result.get("analysis"),
    )


# ── Guest Chat (no auth required) ───────────────────
@app.post("/api/chat/guest")
async def guest_chat(req: ChatRequest):
    """Chat endpoint that doesn't require authentication (for trying out)."""
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = agent.answer(query)

    return {
        "answer": result["answer"],
        "category": result["category"],
        "confidence": result["confidence"],
        "sources": result["sources"],
    }


# ── Conversation Routes ──────────────────────────────
@app.get("/api/conversations", response_model=list[ConversationSummary])
async def list_conversations(user: User = Depends(require_user), db: Session = Depends(get_db)):
    convs = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.updated_at.desc()).limit(50).all()

    result = []
    for c in convs:
        msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()
        last_msg = db.query(Message).filter(
            Message.conversation_id == c.id
        ).order_by(Message.created_at.desc()).first()

        result.append(ConversationSummary(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=msg_count,
            last_message=last_msg.content[:100] if last_msg else None,
        ))

    return result


@app.get("/api/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str, user: User = Depends(require_user),
                           db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        messages=[
            MessageOut(
                id=m.id, role=m.role, content=m.content,
                sources=m.sources, confidence=m.confidence,
                category=m.category, created_at=m.created_at,
            )
            for m in messages
        ],
        created_at=conv.created_at,
    )


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user: User = Depends(require_user),
                              db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    ).first()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted"}


# ── Feedback ─────────────────────────────────────────
@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest, user: User = Depends(require_user),
                          db: Session = Depends(get_db)):
    feedback = Feedback(
        message_id=req.message_id,
        user_id=user.id,
        is_helpful=req.is_helpful,
        comment=req.comment,
    )
    db.add(feedback)
    db.commit()
    return {"message": "Feedback submitted"}


# ── System Stats ─────────────────────────────────────
@app.get("/api/stats", response_model=SystemStats)
async def get_stats():
    stats = vector_db.get_stats()
    return SystemStats(
        total_documents=stats["total_documents"],
        total_chunks=stats["total_documents"],
        embedding_model=stats["embedding_model"],
        categories=CATEGORIES,
        vector_db="ChromaDB",
    )


# ── Re-ingest endpoint (admin) ──────────────────────
@app.post("/api/admin/reingest")
async def reingest_data():
    """Re-run the data ingestion pipeline."""
    stats = ingest_all_data()
    return {"message": "Data re-ingested", "stats": stats}
