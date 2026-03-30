from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── Auth ────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    total_conversations: int
    total_messages: int


# ─── Chat ────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


class SourceReference(BaseModel):
    text: str
    category: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    message_id: str
    sources: List[SourceReference]
    category: str
    confidence: str
    analysis: Optional[dict] = None


# ─── Conversations ───────────────────────────────────
class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[str] = None
    confidence: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageOut]
    created_at: datetime


# ─── Feedback ────────────────────────────────────────
class FeedbackRequest(BaseModel):
    message_id: str
    is_helpful: bool
    comment: Optional[str] = None


# ─── System ──────────────────────────────────────────
class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    embedding_model: str
    categories: List[str]
    vector_db: str = "ChromaDB"
