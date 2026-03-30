<div align="center">

# 🏹 Mahabharata AI Agent

### An AI-Powered Knowledge Agent for the World's Greatest Epic

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange)](https://www.trychroma.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-Educational-green)](#license)

**Ask about characters, stories, battles, dharma, and the timeless wisdom of the Mahabharata — powered by Retrieval-Augmented Generation (RAG) with semantic vector search.**

[Getting Started](#-quick-start) · [Architecture](#-architecture) · [API Docs](#-api-endpoints) · [Screenshots](#-screenshots) · [v1 vs v2](#-v1-vs-v2-comparison)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [v1 vs v2 Comparison](#-v1-vs-v2-comparison)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [How the RAG Agent Works](#-how-the-rag-agent-works)
- [Data Sources](#-data-sources)
- [Screenshots](#-screenshots)
- [License](#license)

---

## 📖 About

This is a **mythology-based AI chatbot** that answers questions about the Mahabharata using NLP and semantic search. It was originally built as a 6th semester college project and has been significantly enhanced in v2.

**v1** (original) used TF-IDF matching with MongoDB and Django.  
**v2** (current) is a complete rewrite using a **RAG (Retrieval-Augmented Generation) pipeline** with a vector database, neural embeddings, and a modern React frontend.

---

## 🔄 v1 vs v2 Comparison

| Feature | v1 (Original) | v2 (Enhanced) |
|:--------|:---------------|:--------------|
| **Search Method** | TF-IDF + regex matching | Semantic vector search (ChromaDB) |
| **Embeddings** | CountVectorizer / Word2Vec | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Database** | MongoDB (manual Q&A lookup) | ChromaDB (vector DB) + SQLite (users) |
| **Backend** | Django + Djongo | **FastAPI** (async, modern) |
| **Frontend** | Empty React folder | **Full React + Tailwind CSS** app |
| **NLP Pipeline** | Naive Bayes classification | **RAG Agent** — intent detection, entity extraction, multi-strategy retrieval, answer synthesis |
| **Authentication** | Basic password check | **JWT tokens** (python-jose + bcrypt) |
| **Chat History** | Single query-response | **Full conversation persistence** with sidebar |
| **Confidence Scoring** | None | High / Medium / Low with similarity % |
| **Source Citations** | None | Expandable source references per answer |
| **Feedback** | None | Thumbs up/down per message |
| **Deployment** | Manual only | **Docker + Docker Compose** ready |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        USER QUERY                            │
│                   "Who is Arjuna?"                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  1. QUERY UNDERSTANDING                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ spaCy NER   │  │ Intent       │  │ Category            │ │
│  │ & POS Tags  │  │ Detection    │  │ Classification      │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
│  Entities: [Arjuna: PERSON]                                  │
│  Intent: who_is  |  Category: Character                      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  2. SEMANTIC RETRIEVAL (ChromaDB)                            │
│  ┌───────────────────┐    ┌────────────────────────────────┐ │
│  │ Sentence-         │    │ ChromaDB Vector Store          │ │
│  │ Transformer       │───▶│ 500+ embedded documents        │ │
│  │ Embedding         │    │ Cosine similarity search       │ │
│  └───────────────────┘    └────────────────────────────────┘ │
│  Strategy: Category-filtered search → Broad fallback         │
│  Returns: Top-K documents with similarity scores             │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  3. ANSWER SYNTHESIS                                         │
│  • Select best matching answer                               │
│  • Score confidence (high ≥ 0.70 | medium ≥ 0.50 | low)     │
│  • Attach source citations with similarity %                 │
│  • Add supplementary context from related results            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|:-----------|:--------|
| **Python 3.12** | Runtime |
| **FastAPI** | Web framework (async, auto-docs at `/docs`) |
| **ChromaDB** | Vector database for semantic search |
| **Sentence Transformers** | Neural embeddings (`all-MiniLM-L6-v2`) |
| **spaCy** | NLP — entity recognition, POS tagging |
| **NLTK** | Tokenization, stopwords, lemmatization |
| **SQLAlchemy + SQLite** | User accounts, conversations, messages |
| **python-jose + passlib** | JWT authentication + bcrypt hashing |

### Frontend
| Technology | Purpose |
|:-----------|:--------|
| **React 18** | UI framework |
| **Tailwind CSS** | Styling |
| **React Router v6** | Client-side routing |
| **React Markdown** | Render markdown in chat messages |
| **Lucide React** | Icons |
| **Axios** | HTTP client |
| **Vite** | Build tool & dev server |

### DevOps
| Technology | Purpose |
|:-----------|:--------|
| **Docker** | Multi-stage build (frontend + backend) |
| **Docker Compose** | One-command deployment |

---

## 📁 Project Structure

```
Mahabharata-GPT/
│
├── backend/
│   ├── main.py                    # FastAPI app & all API routes
│   ├── config.py                  # Settings & configuration
│   ├── requirements.txt           # Python dependencies
│   │
│   ├── agent/
│   │   └── rag_agent.py           # 🧠 RAG Agent (query understanding + synthesis)
│   │
│   ├── vectordb/
│   │   ├── manager.py             # ChromaDB vector store manager
│   │   └── ingest.py              # Data ingestion pipeline
│   │
│   ├── api/
│   │   ├── models.py              # SQLAlchemy models (User, Conversation, Message)
│   │   ├── schemas.py             # Pydantic request/response schemas
│   │   └── auth.py                # JWT authentication utilities
│   │
│   └── data/                      # 📚 Knowledge base
│       ├── mahabharata.txt        # 200 stories (Tiny Tales by Laura Gibbs)
│       ├── comparison.json        # Character comparisons
│       ├── creatures.json         # Mythological creatures
│       ├── places.json            # Sacred places & locations
│       ├── scenes.json            # Key scenes & incidents
│       ├── themes.json            # Themes & morals
│       ├── objects.json           # Weapons & artifacts
│       ├── prophecies.json        # Prophecies & curses
│       ├── riddles.json           # Riddles & puzzles
│       ├── cultural_events.json
│       ├── mythology_eras.json
│       └── mythology_systems.json
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx               # React entry point
│       ├── App.jsx                # Router & auth provider
│       ├── index.css              # Tailwind + custom styles
│       ├── utils/
│       │   ├── api.js             # Axios API client
│       │   └── AuthContext.jsx    # Auth state management
│       ├── components/
│       │   ├── Sidebar.jsx        # Conversation sidebar
│       │   ├── ChatMessage.jsx    # Message bubble with sources
│       │   ├── ChatInput.jsx      # Input with suggestions
│       │   └── WelcomeScreen.jsx  # Landing screen
│       └── pages/
│           ├── AuthPage.jsx       # Login / Register
│           ├── ChatPage.jsx       # Main chat interface
│           └── ProfilePage.jsx    # User profile & system stats
│
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # One-command deployment
├── .gitignore
├── .dockerignore
└── README.md
```

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/Subhitcha04/Mahabharata-GPT.git
cd Mahabharata-GPT

docker-compose up --build
```
App available at **http://localhost:8000**

### Option 2 — Manual Setup

#### Backend

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> **First startup takes 1–2 minutes** — it downloads the sentence-transformer model and ingests all data into ChromaDB. Subsequent starts are instant (cached).

#### Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at **http://localhost:3000** and proxies `/api` calls to the backend.

---

## 📡 API Endpoints

FastAPI auto-generates interactive docs at **http://localhost:8000/docs**

| Method | Endpoint | Auth | Description |
|:-------|:---------|:----:|:------------|
| `POST` | `/api/auth/register` | ❌ | Create account |
| `POST` | `/api/auth/login` | ❌ | Sign in → JWT token |
| `GET` | `/api/auth/profile` | ✅ | User profile |
| `POST` | `/api/chat` | ✅ | Send message to RAG agent |
| `POST` | `/api/chat/guest` | ❌ | Guest chat (no history saved) |
| `GET` | `/api/conversations` | ✅ | List user's conversations |
| `GET` | `/api/conversations/:id` | ✅ | Full conversation with messages |
| `DELETE` | `/api/conversations/:id` | ✅ | Delete a conversation |
| `POST` | `/api/feedback` | ✅ | Thumbs up/down on a message |
| `GET` | `/api/stats` | ❌ | System statistics |
| `GET` | `/api/health` | ❌ | Health check |
| `POST` | `/api/admin/reingest` | ❌ | Re-run data ingestion |

---

## 🧠 How the RAG Agent Works

**Example: User asks "Who is Arjuna?"**

**Step 1 — Query Understanding**
```
Intent:    who_is (person identification)
Entities:  [Arjuna → PERSON]
Category:  Character (keyword match)
```

**Step 2 — Semantic Retrieval**
```
→ Embed query using all-MiniLM-L6-v2
→ Search ChromaDB with category filter "Character"
→ If results are weak, broaden search across all categories
→ Return Top-5 documents with cosine similarity scores
```

**Step 3 — Answer Synthesis**
```
→ Best match (similarity 0.87): Answer about Arjuna from characters data
→ Confidence: HIGH (≥ 0.70)
→ Sources: [Character/Arjuna: 87%, MahabharataText/Chapter1: 72%]
→ Supplementary context from related text chunks
```

---

## 📚 Data Sources

| Source | Description | Documents |
|:-------|:------------|:----------|
| `mahabharata.txt` | 200 stories from *Tiny Tales* by Laura Gibbs (CC BY-NC-SA 4.0) | ~200 chunks |
| 11 JSON files | Q&A pairs across 11 categories (characters, places, themes, etc.) | 81 entries |
| **Total** | All data chunked and embedded | **500+ vectors** in ChromaDB |

### Knowledge Categories
`Character` · `StoryOrEvent` · `SceneOrIncident` · `PlaceOrLocation` · `ObjectOrArtifact` · `ThemeOrMoral` · `MythologySystem` · `MythologyEra` · `CreatureOrSpecies` · `ProphecyOrFate` · `Comparison` · `CulturalOrHistorical` · `RiddleOrPuzzle`

---

## 📸 Screenshots

### Authentication Page
Login/Register with gradient branding panel

### Chat Interface
Full conversation with sidebar, message bubbles, typing indicators, confidence badges, and expandable source citations

### Profile Page
User stats, system architecture info, and knowledge category overview

---

## 👩‍💻 Author

**Subhitcha** — 6th Semester Project

---

## License

This project is for **educational purposes** (college semester project).  
Mahabharata text data: CC BY-NC-SA 4.0 by Laura Gibbs.