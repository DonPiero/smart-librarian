# 📚 Smart Librarian — RAG Chatbot (FastAPI + LangChain + OpenAI + ChromaDB)

A production-ready demo that answers **book-related questions** using an **agent with tools** on top of a **local Chroma vector store**. 
It exposes a **FastAPI** backend with JWT auth, a minimal **vanilla JS UI**, and endpoints for **chat, STT, TTS, and image generation**.

## ✨ Features

- **Agentic RAG**: LangChain agent with two tools
  - `search_relevant_books(query)` → finds relevant titles from the embedded library
  - `get_summary_by_title(title)` → returns the full summary of a chosen title
- **Never recommends books outside the embedded library.** Profanity is filtered before invoking the LLM tools.
- **Deterministic flow**: Agent is instructed to **always show a ranked list of titles first**, then reveal summaries on request.
- **Vector store**: ChromaDB persisted under `data/chroma_store/` (auto-built on first run from `data/book_summaries.json`).
- **Auth & sessions**: JWT login/register, multi-conversation history stored in SQLite (`logs.db`).
- **Multimodal bits**:
  - **STT** `/conversations/{id}/stt` → parse speech and send as a message (OpenAI Whisper)
  - **TTS** `/conversations/{id}/tts` → returns `audio/mpeg` generated from the latest assistant reply
  - **Image** `/conversations/{id}/image` → returns a PNG generated from recent chat context
- **Frontend**: Static HTML/CSS/JS served from `/` with a clean chat UI.
- **Dockerized**: Single-image build + `docker-compose.yml` for quick runs + Kubernetes for deployment and service.
- **CORS enabled** for easy local testing.

---

## 🚀 Quickstart

### Option A — Docker (recommended)

1) Create `.env` in the project root:
```env
SECRET_KEY="replace-me"
OPENAI_API_KEY="sk-..."
```
2)  Build & run:
```bash
docker compose up --build
```
3)  Open:
- UI → http://localhost:8000/ 
- Swagger → http://localhost:8000/docs

> First run will also **build embeddings** into `data/chroma_store/` (can take ~seconds)

---

### Option B — Local (uvicorn)

```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
export SECRET_KEY="replace-me"
export OPENAI_API_KEY="sk-..."
uvicorn app.main:app --reload
```
Open the same URLs as above.

---

## 🔐 Environment variables

| Name             | Required | Description                                  |
|------------------|----------|----------------------------------------------|
| `OPENAI_API_KEY` | ✅        | Used for Chat + Embeddings + STT + TTS + IMG |
| `SECRET_KEY`     | ✅        | JWT signing secret                           |

SQLite path is set to `sqlite:///./logs.db` (see `app/config/constants.py`).

---

## 🧭 API Overview

All endpoints require `Authorization: Bearer <token>` after login.

### Auth
- `POST /register` → create a user (`{"username": "...","password":"..."}`)
- `POST /login` → returns `{"access_token": "...","token_type":"bearer"}`

### Conversations
- `POST /conversations` → create & return a new conversation
- `GET /conversations` → list your conversations
- `GET /conversations/{conversation_id}` → get conversation + messages
- `POST /conversations/{conversation_id}/messages` → send a message (`{"content": "..."}`)
- `POST /conversations/{conversation_id}/stt` → upload audio; transcript is sent as a message
- `GET /conversations/{conversation_id}/tts` → returns MP3 from the **latest assistant** message
- `GET /conversations/{conversation_id}/image` → returns PNG based on recent context
- `DELETE /conversations/{conversation_id}` → delete conversation (and agent instance)

---

**Key parts**
- `app/main.py` — FastAPI app + CORS + static UI + DB init on startup
- `app/controller/*` — route handlers (auth + chatbot: chat, STT, TTS, IMG, CRUD)
- `app/services/*` — agent factory, LLM wiring, DB session & OpenAI clients
- `app/utils/*` — vector search, tools, validators (profanity), helpers
- `app/models/*` — SQLAlchemy models & Pydantic schemas
- `app/config/*` — env-backed config and constants
- `app/view/*` — minimal HTML/CSS/JS chat frontend
- `data/book_summaries.json` — seed data; used to build the Chroma store

---

## 🧠 How RAG is built here

- Embeddings: `text-embedding-3-small` (configurable)
- Vector store: **Chroma**, persisted to `data/chroma_store/`
- Bootstrapping: on first import of `utils/retriever.py`, if no index exists, it embeds `book_summaries.json` and persists the store.
- Agent: `create_openai_tools_agent` with memory. Tools are the only way it can retrieve book info.
- Guardrails: profanity blocked; the prompt **forces** showing a ranked list of titles before summaries.

---

## 🛡️ Security notes

- JWT tokens expire after 60 minutes (see `app/auth/jwt_handler.py`).
- CORS is open for local testing; restrict in production.
- Never commit real secrets. Use `.env` (see Docker/compose).

