"""
Copilot Router — REST + SSE streaming endpoints for the AI Marketer Copilot.

Endpoints:
    POST /chat          Non-streaming chat (fallback)
    POST /stream        SSE streaming chat (primary)
    GET  /history/{id}  Load conversation history
    GET  /conversations List recent conversations
    DELETE /conversations/{id}  Clear a conversation
"""
import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database.connection import get_db
from app.models.models import CopilotConversation
from app.services.copilot_service import chat_sync, chat_stream

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


# ── Non-Streaming Chat ──────────────────────────────────────────
@router.post("/chat")
def copilot_chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Standard non-streaming chat endpoint. Returns complete response."""
    conv_id = req.conversation_id or str(uuid.uuid4())
    result = chat_sync(req.message, conv_id, db)
    return result


# ── SSE Streaming Chat ──────────────────────────────────────────
@router.post("/stream")
async def copilot_stream(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Server-Sent Events streaming chat.

    Emits events:
        data: {"type": "intent", "intent": "churn"}
        data: {"type": "chunk", "content": "Based on..."}
        data: {"type": "done", "references": [...]}
    """
    conv_id = req.conversation_id or str(uuid.uuid4())

    return StreamingResponse(
        chat_stream(req.message, conv_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Conversation History ────────────────────────────────────────
@router.get("/history/{conversation_id}")
def get_history(conversation_id: str, db: Session = Depends(get_db)):
    """Load all messages for a conversation."""
    messages = (
        db.query(CopilotConversation)
        .filter(CopilotConversation.conversation_id == conversation_id)
        .order_by(CopilotConversation.created_at)
        .all()
    )
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "references": m.references or [],
                "context_used": m.context_used,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


# ── List Recent Conversations ───────────────────────────────────
@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db)):
    """List recent conversation threads (most recent first)."""
    convs = (
        db.query(
            CopilotConversation.conversation_id,
            func.min(CopilotConversation.content).label("first_message"),
            func.count(CopilotConversation.id).label("message_count"),
            func.max(CopilotConversation.created_at).label("last_active"),
        )
        .filter(CopilotConversation.role == "user")
        .group_by(CopilotConversation.conversation_id)
        .order_by(desc(func.max(CopilotConversation.created_at)))
        .limit(20)
        .all()
    )
    return [
        {
            "conversation_id": c.conversation_id,
            "preview": (c.first_message or "")[:100],
            "message_count": c.message_count,
            "last_active": c.last_active.isoformat() if c.last_active else None,
        }
        for c in convs
    ]


# ── Delete Conversation ─────────────────────────────────────────
@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Clear all messages in a conversation."""
    deleted = (
        db.query(CopilotConversation)
        .filter(CopilotConversation.conversation_id == conversation_id)
        .delete()
    )
    db.commit()
    return {"deleted": deleted, "conversation_id": conversation_id}
