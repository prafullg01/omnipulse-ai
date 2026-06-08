"""Customers Router — Customer 360, Orders, Session tracking, Intelligence.

Enhanced Customer 360 includes:
- Profile, demographics, session info
- Cart items, wishlist items, search history, product views
- Orders, tickets, journey timeline
- Real-time AI scores (churn, trust, NBA, CLV, digital twin)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database.connection import get_db
from app.models.models import (
    Customer, CustomerProfile, Order, OrderItem, Event,
    SupportTicket, NBADecision, Journey, Message, CampaignResponse, Product
)
from app.models.realtime_models import (
    CartItem, WishlistItem, SearchHistory, ProductView, CustomerSession
)
from app.utils.auth import get_current_user, require_role

router = APIRouter()


def safe_decode(value):
    """Safely decode bytes to string or return original value."""
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except:
            return "Unknown"
    return value


@router.get("/360/{customer_id}")
def customer_360(customer_id: str, db: Session = Depends(get_db)):
    """Complete Customer 360 view with everything linked."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == customer_id
    ).first()
    
    # Orders
    orders = db.query(Order).filter(
        Order.customer_id == customer_id
    ).order_by(desc(Order.order_date)).limit(20).all()
    
    # Events (for journey timeline)
    events = db.query(Event).filter(
        Event.customer_id == customer_id
    ).order_by(desc(Event.timestamp)).limit(100).all()
    
    # Support tickets
    tickets = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id
    ).order_by(desc(SupportTicket.created_at)).limit(10).all()
    
    # NBA decisions
    nba = db.query(NBADecision).filter(
        NBADecision.customer_id == customer_id
    ).order_by(desc(NBADecision.timestamp)).limit(5).all()
    
    # Messages
    messages = db.query(Message).filter(
        Message.customer_id == customer_id
    ).order_by(desc(Message.timestamp)).limit(10).all()
    
    # Cart items
    cart_items_data = db.query(CartItem, Product).join(
        Product, CartItem.product_id == Product.product_id
    ).filter(
        CartItem.customer_id == customer_id
    ).all()
    
    # Wishlist items
    wishlist_items_data = db.query(WishlistItem, Product).join(
        Product, WishlistItem.product_id == Product.product_id
    ).filter(
        WishlistItem.customer_id == customer_id
    ).all()
    
    # Search history
    searches = db.query(SearchHistory).filter(
        SearchHistory.customer_id == customer_id
    ).order_by(desc(SearchHistory.timestamp)).limit(20).all()
    
    # Product views
    views = db.query(ProductView).filter(
        ProductView.customer_id == customer_id
    ).order_by(desc(ProductView.timestamp)).limit(20).all()
    
    # Current session
    active_session = db.query(CustomerSession).filter(
        CustomerSession.customer_id == customer_id,
        CustomerSession.is_active == True
    ).order_by(desc(CustomerSession.login_time)).first()
    
    # Revenue calculations
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.customer_id == customer_id, Order.status != "cancelled"
    ).scalar() or 0
    
    order_count = db.query(Order).filter(
        Order.customer_id == customer_id, Order.status != "cancelled"
    ).count()
    
    avg_order_value = total_revenue / order_count if order_count > 0 else 0
    
    # Cart value
    cart_value = sum(p.price * ci.quantity for ci, p in cart_items_data) if cart_items_data else 0
    
    return {
        "customer": {
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "gender": safe_decode(customer.gender),
            "age": customer.age,
            "city": safe_decode(customer.city),
            "country": customer.country,
            "registration_date": customer.registration_date.isoformat() if customer.registration_date else None,
            "preferred_language": customer.preferred_language,
            "status": customer.status,
        },
        "session": {
            "is_active": active_session is not None,
            "session_id": active_session.session_id if active_session else None,
            "login_time": active_session.login_time.isoformat() if active_session and active_session.login_time else None,
            "device": active_session.device if active_session else None,
            "browser": active_session.browser if active_session else None,
            "ip_address": active_session.ip_address if active_session else None,
            "duration_seconds": int((datetime.utcnow() - active_session.login_time).total_seconds()) if active_session and active_session.login_time else 0,
        },
        "intelligence": {
            "risk_score": profile.risk_score if profile else 0,
            "trust_score": profile.trust_score if profile else 50,
            "happiness_score": profile.happiness_score if profile else 50,
            "churn_probability": profile.churn_probability if profile else 0,
            "clv": profile.clv if profile else 0,
            "predicted_clv": profile.predicted_clv if profile else 0,
            "persona": profile.persona if profile else "Unknown",
            "emotion": profile.emotion if profile else "neutral",
            "segment": profile.segment if profile else "new",
            "engagement_score": profile.engagement_score if profile else 50,
            "competitive_risk": profile.competitive_risk if profile else 0,
            "recency_days": profile.recency_days if profile else 0,
            "frequency": profile.frequency if profile else 0,
            "monetary": profile.monetary if profile else 0,
        },
        "cart": {
            "items": [
                {
                    "product_id": p.product_id,
                    "product_name": p.name,
                    "product_image": p.image_url,
                    "price": p.price,
                    "quantity": ci.quantity,
                    "category": p.category,
                }
                for ci, p in cart_items_data
            ],
            "total_value": round(cart_value, 2),
            "item_count": len(cart_items_data),
        },
        "wishlist": {
            "items": [
                {
                    "product_id": p.product_id,
                    "product_name": p.name,
                    "product_image": p.image_url,
                    "price": p.price,
                    "category": p.category,
                }
                for wi, p in wishlist_items_data
            ],
            "count": len(wishlist_items_data),
        },
        "recent_searches": [
            {
                "query": s.search_query,
                "results_count": s.results_count,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in searches
        ],
        "recent_views": [
            {
                "product_id": v.product_id,
                "product_name": v.product_name,
                "category": v.product_category,
                "timestamp": v.timestamp.isoformat(),
            }
            for v in views
        ],
        "orders": [
            {
                "order_id": o.order_id,
                "total_amount": o.total_amount,
                "status": o.status,
                "order_date": o.order_date.isoformat(),
                "payment_method": o.payment_method,
            }
            for o in orders
        ],
        "journey_timeline": [
            {
                "event_type": e.event_type,
                "event_value": e.event_value,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata_json,
            }
            for e in sorted(events, key=lambda x: x.timestamp)
        ],
        "tickets": [
            {
                "ticket_id": t.ticket_id,
                "subject": t.subject,
                "message": t.message[:100] if t.message else "",
                "sentiment": t.sentiment,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
            }
            for t in tickets
        ],
        "nba_decisions": [
            {
                "decision_id": n.decision_id,
                "recommended_action": n.recommended_action,
                "channel": n.channel,
                "offer": n.offer,
                "confidence": n.confidence,
                "reason": n.reason,
                "inference_tier": n.inference_tier,
                "status": n.status,
                "timestamp": n.timestamp.isoformat(),
            }
            for n in nba
        ],
        "messages": [
            {
                "channel": m.channel,
                "subject": m.subject,
                "opened": m.opened,
                "clicked": m.clicked,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in messages
        ],
        "total_revenue": round(total_revenue, 2),
        "total_orders": order_count,
        "average_order_value": round(avg_order_value, 2),
        # ── Top-level aliases for frontend compatibility ──
        # Customer360.tsx reads profile.name, profile.email, etc.
        "name": f"{customer.first_name} {customer.last_name}",
        "email": customer.email,
        "city": safe_decode(customer.city),
        "segment": profile.segment if profile else "new",
        "emotion": profile.emotion if profile else "neutral",
        "trust_score": profile.trust_score if profile else 0,
        "happiness_score": profile.happiness_score if profile else 0,
        "engagement_score": profile.engagement_score if profile else 0,
        "churn_probability": profile.churn_probability if profile else 0,
        "risk_score": profile.risk_score if profile else 0,
        # ── 'events' key for Recent Activity section ──
        # Frontend reads profile.events on line 362
        "events": [
            {
                "event_type": e.event_type,
                "event_value": e.event_value,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata_json,
            }
            for e in sorted(events, key=lambda x: x.timestamp, reverse=True)
        ][:30],
    }


@router.get("")
def list_customers(
    segment: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    List customers with RANDOM but reproducible sampling.
    Returns a diverse mix of customers across all risk levels.
    """
    results = db.query(Customer, CustomerProfile).join(
        CustomerProfile, Customer.customer_id == CustomerProfile.customer_id
    ).filter(
        Customer.role == "customer"
    ).order_by(func.random()).limit(limit).all()
    
    customer_list = []
    for c, p in results:
        try:
            customer_data = {
                "customer_id": c.customer_id,
                "name": f"{c.first_name} {c.last_name}",
                "email": c.email,
                "age": c.age,
                "gender": safe_decode(c.gender),
                "city": safe_decode(c.city),
                "status": c.status,
                "risk_score": p.risk_score if p else 0,
                "trust_score": p.trust_score if p else 50,
                "happiness_score": p.happiness_score if p else 50,
                "churn_probability": p.churn_probability if p else 0,
                "clv": p.clv if p else 0,
                "persona": p.persona if p else "Unknown",
                "emotion": p.emotion if p else "neutral",
                "segment": p.segment if p else "medium",
                "engagement_score": p.engagement_score if p else 50,
            }
            customer_list.append(customer_data)
        except Exception as e:
            print(f"Error processing customer {c.customer_id}: {e}")
            continue
    
    return customer_list


@router.get("/sessions/active")
def get_active_sessions(db: Session = Depends(get_db)):
    """Get all currently active customer sessions."""
    sessions = db.query(CustomerSession, Customer).join(
        Customer, CustomerSession.customer_id == Customer.customer_id
    ).filter(
        CustomerSession.is_active == True
    ).all()
    
    return {
        "active_count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "customer_id": s.customer_id,
                "customer_name": f"{c.first_name} {c.last_name}",
                "login_time": s.login_time.isoformat() if s.login_time else None,
                "duration_seconds": int((datetime.utcnow() - s.login_time).total_seconds()) if s.login_time else 0,
                "device": s.device,
                "browser": s.browser,
                "ip_address": s.ip_address,
            }
            for s, c in sessions
        ]
    }


class OrderCreate(BaseModel):
    items: List[dict]  # [{product_id, quantity}]
    payment_method: str = "card"
    shipping_address: Optional[str] = None


@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.websocket.manager import manager
    
    total = 0
    order_items = []
    for item in order_data.items:
        product = db.query(Product).filter(Product.product_id == item["product_id"]).first()
        if product:
            price = product.price * item.get("quantity", 1)
            total += price
            order_items.append(OrderItem(
                product_id=product.product_id,
                quantity=item.get("quantity", 1),
                price=product.price,
            ))
    
    order = Order(
        customer_id=user.customer_id,
        total_amount=total,
        payment_method=order_data.payment_method,
        shipping_address=order_data.shipping_address,
        status="confirmed",
    )
    db.add(order)
    db.flush()
    
    for oi in order_items:
        oi.order_id = order.order_id
        db.add(oi)
    
    event = Event(
        customer_id=user.customer_id,
        event_type="PURCHASE_COMPLETED",
        event_value=str(total),
        metadata_json={"order_id": order.order_id, "item_count": len(order_items)},
    )
    db.add(event)
    db.commit()
    
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "PURCHASE_COMPLETED",
        "customer_id": user.customer_id,
        "customer_name": f"{user.first_name} {user.last_name}",
        "event_value": f"₹{total:,.0f}",
        "message": f"💰 {user.first_name} {user.last_name} completed purchase — ₹{total:,.0f}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"order_id": order.order_id, "total": total},
    }, room="admin")
    
    return {"order_id": order.order_id, "total": total, "status": "confirmed"}


@router.get("/orders")
def get_orders(user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(
        Order.customer_id == user.customer_id
    ).order_by(desc(Order.order_date)).all()
    return [
        {
            "order_id": o.order_id,
            "total_amount": o.total_amount,
            "status": o.status,
            "payment_method": o.payment_method,
            "order_date": o.order_date.isoformat(),
        }
        for o in orders
    ]
