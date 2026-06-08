"""Support Router — Tickets CRUD with sentiment analysis."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.models import SupportTicket, Customer, CustomerProfile, Event
from app.utils.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter()


def analyze_sentiment(text: str) -> tuple[str, float]:
    """Simple rule-based + keyword sentiment analysis."""
    text_lower = text.lower()
    
    angry_words = ["terrible", "worst", "hate", "angry", "furious", "disgusting", "scam", "fraud", "refund", "unacceptable"]
    frustrated_words = ["disappointed", "frustrated", "annoyed", "waiting", "delayed", "broken", "damaged", "wrong", "issue", "problem"]
    happy_words = ["love", "amazing", "excellent", "great", "awesome", "perfect", "thank", "happy", "wonderful", "best"]
    excited_words = ["excited", "fantastic", "incredible", "wow", "outstanding", "brilliant"]
    
    angry_count = sum(1 for w in angry_words if w in text_lower)
    frustrated_count = sum(1 for w in frustrated_words if w in text_lower)
    happy_count = sum(1 for w in happy_words if w in text_lower)
    excited_count = sum(1 for w in excited_words if w in text_lower)
    
    scores = {
        "angry": angry_count * 2,
        "frustrated": frustrated_count * 1.5,
        "happy": happy_count * 1.5,
        "excited": excited_count * 2,
        "neutral": 1,
    }
    
    sentiment = max(scores, key=scores.get)
    confidence = min(scores[sentiment] / 5, 1.0)
    
    return sentiment, confidence


class TicketCreate(BaseModel):
    subject: Optional[str] = None
    message: str


@router.post("")
async def create_ticket(
    ticket_data: TicketCreate,
    user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sentiment, score = analyze_sentiment(ticket_data.message)
    
    ticket = SupportTicket(
        customer_id=user.customer_id,
        subject=ticket_data.subject,
        message=ticket_data.message,
        sentiment=sentiment,
        sentiment_score=score,
    )
    db.add(ticket)
    
    # Log event
    event = Event(
        customer_id=user.customer_id,
        event_type="ticket_created",
        event_value=sentiment,
        metadata_json={"ticket_subject": ticket_data.subject, "sentiment": sentiment},
    )
    db.add(event)
    
    # Update customer emotion
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == user.customer_id
    ).first()
    if profile:
        profile.emotion = sentiment
        if sentiment in ["angry", "frustrated"]:
            profile.trust_score = max(0, profile.trust_score - 5)
            profile.happiness_score = max(0, profile.happiness_score - 10)
            profile.churn_probability = min(1, profile.churn_probability + 0.1)
    
    db.commit()
    db.refresh(ticket)
    
    # Broadcast
    await manager.broadcast_event("emotion_updated", {
        "customer_id": user.customer_id,
        "customer_name": f"{user.first_name} {user.last_name}",
        "emotion": sentiment,
        "source": "support_ticket",
    })
    
    await manager.broadcast_event("risk_updated", {
        "customer_id": user.customer_id,
        "customer_name": f"{user.first_name} {user.last_name}",
        "churn_probability": profile.churn_probability if profile else 0,
        "trust_score": profile.trust_score if profile else 50,
    })
    
    return {
        "ticket_id": ticket.ticket_id,
        "sentiment": sentiment,
        "sentiment_score": score,
        "status": "open",
    }


@router.get("")
def list_tickets(
    user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role == "admin":
        tickets = db.query(SupportTicket).order_by(desc(SupportTicket.created_at)).limit(50).all()
    else:
        tickets = db.query(SupportTicket).filter(
            SupportTicket.customer_id == user.customer_id
        ).order_by(desc(SupportTicket.created_at)).all()
    
    return [
        {
            "ticket_id": t.ticket_id,
            "customer_id": t.customer_id,
            "subject": t.subject,
            "message": t.message,
            "sentiment": t.sentiment,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
        }
        for t in tickets
    ]
