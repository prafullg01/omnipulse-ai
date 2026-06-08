"""Events Router — Log and query customer events, trigger intelligence pipeline.

Every event → Database → WebSocket → Intelligence Orchestrator.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.models import Event, Customer
from app.utils.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter()


class EventCreate(BaseModel):
    event_type: str
    event_value: Optional[str] = None
    metadata_json: Optional[dict] = None


EVENT_TYPE_MAP = {
    "cart_add": "ADD_TO_CART",
    "cart_remove": "REMOVE_FROM_CART",
    "product_view": "PRODUCT_VIEW",
    "search": "SEARCH",
    "wishlist_add": "ADD_TO_WISHLIST",
    "wishlist_remove": "REMOVE_FROM_WISHLIST",
    "purchase": "PURCHASE_COMPLETED",
    "support_ticket": "SUPPORT_TICKET_CREATED",
    "ticket_created": "SUPPORT_TICKET_CREATED",
    "review_submit": "REVIEW_SUBMITTED",
    "offer_click": "CAMPAIGN_CLICKED",
    "message_open": "CAMPAIGN_OPENED",
    "category_view": "CATEGORY_VIEW",
    "checkout": "CHECKOUT_STARTED",
    "refund": "REFUND_REQUESTED",
    "ai_chat": "AI_CHAT",
}


def normalize_event_type(event_type: str) -> str:
    mapped = EVENT_TYPE_MAP.get(event_type.lower().strip())
    if mapped:
        return mapped
    return event_type.upper().replace(" ", "_")


@router.post("")
async def log_event(
    event_data: EventCreate,
    user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    normalized_type = normalize_event_type(event_data.event_type)
    
    event = Event(
        customer_id=user.customer_id,
        event_type=normalized_type,
        event_value=event_data.event_value,
        metadata_json=event_data.metadata_json or {},
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    customer_name = f"{user.first_name} {user.last_name}"
    
    # Broadcast activity event to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_id": event.event_id,
        "customer_id": user.customer_id,
        "customer_name": customer_name,
        "event_type": normalized_type,
        "event_value": event.event_value,
        "message": f"{customer_name} — {normalized_type.replace('_', ' ').title()}: {event.event_value or ''}",
        "timestamp": event.timestamp.isoformat(),
        "metadata": event.metadata_json,
    }, room="admin")
    
    # ── Trigger Intelligence Orchestrator ──
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Error: {e}")
    
    return {"event_id": event.event_id, "status": "recorded", "event_type": normalized_type}


@router.get("")
def list_events(
    customer_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Event).order_by(desc(Event.timestamp))
    if customer_id:
        q = q.filter(Event.customer_id == customer_id)
    if event_type:
        q = q.filter(Event.event_type == event_type)
    
    events = q.limit(limit).all()
    
    # Fetch customer names for display
    customer_ids = list(set(e.customer_id for e in events))
    customers = {c.customer_id: c for c in db.query(Customer).filter(Customer.customer_id.in_(customer_ids)).all()} if customer_ids else {}
    
    return [
        {
            "event_id": e.event_id,
            "customer_id": e.customer_id,
            "customer_name": f"{customers[e.customer_id].first_name} {customers[e.customer_id].last_name}" if e.customer_id in customers else "Unknown",
            "event_type": e.event_type,
            "event_value": e.event_value,
            "metadata": e.metadata_json,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in events
    ]


@router.get("/stream-stats")
def event_stats(db: Session = Depends(get_db)):
    total = db.query(Event).count()
    from sqlalchemy import func
    type_counts = (
        db.query(Event.event_type, func.count(Event.event_id))
        .group_by(Event.event_type)
        .all()
    )
    return {
        "total_events": total,
        "by_type": {t: c for t, c in type_counts},
        "ws_connections": manager.connection_count,
    }
