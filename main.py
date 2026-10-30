import logging
import os
import sqlite3
import uuid
from typing import Literal
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import (
    Groq,
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
    APIStatusError
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BASE_DIR = Path(__file__).resolve().parent
DB_NAME = str(BASE_DIR / "careerpilot.db")

load_dotenv()

app = FastAPI(title="CareerPilot AI API")

# Initialize the Groq client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """
You are CareerPilot AI, a helpful AI assistant for entry-level
technology job seekers.

Your responsibilities:
- Answer general questions clearly and accurately.
- Provide practical career guidance and job-search advice.
- Help users improve resumes and analyze job descriptions.
- Identify skill gaps based on the user's actual skills.
- Prepare users for technical and HR interviews.
- Explain technical concepts in beginner-friendly language.

Guidelines:
- Give concise, structured, actionable answers.
- Explain unfamiliar technical terms simply.
- Never invent a user's experience, qualifications, or skills.
- Distinguish facts from assumptions and mention uncertainty
  when appropriate.
- If a question requires live information you cannot access,
  be transparent about that limitation.
- Ask a clarifying question when essential information is missing.
- Adapt your answer to the user's experience level.
"""

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)

class ChatRequest(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        # Store each conversation separately
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Keep the existing messages table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add conversation_id only if it doesn't exist yet
        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(messages)"
            ).fetchall()
        }

        if "conversation_id" not in columns:
            conn.execute("""
                ALTER TABLE messages
                ADD COLUMN conversation_id TEXT
            """)

def create_conversation(conversation_id, title="New Chat"):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            INSERT INTO conversations (id, title)
            VALUES (?, ?)
            """,
            (conversation_id, title)
        )


def save_message(conversation_id, role, content):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )

def get_recent_messages(conversation_id, limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit)
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in reversed(rows)
    ]

def update_conversation_title(conversation_id, title):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            UPDATE conversations
            SET title = ?
            WHERE id = ?
            """,
            (title, conversation_id)
        )

init_db()

@app.get("/")
def home():
    return {"message": "CareerPilot AI backend is running!"}

@app.post("/conversations")
def new_conversation():
    conversation_id = str(uuid.uuid4())

    create_conversation(conversation_id)

    return {
        "conversation_id": conversation_id,
        "title": "New Chat"
    }


@app.get("/conversations")
def list_conversations():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            ORDER BY created_at DESC
            """
        ).fetchall()

    return {
        "conversations": [
            {
                "conversation_id": row[0],
                "title": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]
    }


@app.get("/history")
def history(conversation_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        conversation = conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            (conversation_id,)
        ).fetchone()

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found."
            )
    return {"messages": get_recent_messages(conversation_id, limit=100)}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if client is None:
        logging.error("GROQ_API_KEY is not configured.")
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured. Please contact the administrator."
        )

    try:

        with sqlite3.connect(DB_NAME) as conn:
            conversation = conn.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (request.conversation_id,)
            ).fetchone()

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found. Create a new chat first."
            )
        # Keep only the 10 most recent previous messages
        recent_history = request.history[-10:]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        messages.extend(
            {"role": item.role, "content": item.content}
            for item in recent_history
        )

        # Add the current user message last
        messages.append({
            "role": "user",
            "content": request.message
        })


        # Check whether this is the first message
        with sqlite3.connect(DB_NAME) as conn:
            count = conn.execute(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE conversation_id = ?
                """,
                (request.conversation_id,)
            ).fetchone()[0]

        # Use the first question as the conversation title
        if count == 0:
            title = request.message.strip().replace("\n", " ")
            if len(title) > 40:
                title = title[:37] + "..."

            update_conversation_title(
                request.conversation_id,
                title or "New Chat"
            )

        # Save the user's message
        save_message(
            request.conversation_id,
            "user",
            request.message
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=2000,
            temperature=0.3
        )

        answer = response.choices[0].message.content

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty response."
            )

        save_message(
            request.conversation_id,
            "assistant",
            answer
        )

        return ChatResponse(reply=answer)

    except HTTPException:
        raise

    except RateLimitError:
        logging.warning("Groq API rate limit reached.")
        raise HTTPException(
            status_code=429,
            detail="AI service usage limit reached. Please try again later."
        )

    except AuthenticationError:
        logging.error("Groq API authentication failed.")
        raise HTTPException(
            status_code=503,
            detail="AI service authentication failed. Please check the API configuration."
        )

    except APIConnectionError:
        logging.exception("Could not connect to Groq API.")
        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please try again."
        )

    except APIStatusError as e:
        logging.exception("Groq API returned an error.")
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected error."
        )

    except Exception:
        logging.exception("CareerPilot AI: Unexpected error")
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred."
        )
