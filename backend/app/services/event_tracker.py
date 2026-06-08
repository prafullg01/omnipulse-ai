"""
Central Event Tracking Engine
===============================

Universal function for tracking ALL customer activities.

Usage:
    track_event(customer_id, "PRODUCT_VIEW", "Nike Shoes", {"product_id": "123"}, db)
    track_event(customer_id, "ADD_TO_CART", "Nike Shoes", {"quantity": 1}, db)
    track_event(customer_id, "PURCHASE", "Order completed", {"order_id": "ORD-123", "amount": 2999}, db)

Every customer action MUST call this function.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json

from app.models.models import Event, CustomerProfile
from app.websocket.manager import manager


async def track_event(
    customer_id: str,
    event_type: str,
    event_value: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = None,
    broadcast: bool = True
) -> Event:
    """
    Universal event tracking function.
    
    Args:
        customer_id: Customer who performed the action
        event_type: Type of event (PRODUCT_VIEW, ADD_TO_CART, etc.)
        event_value: Brief description (product name, search query, etc.)
        metadata: Additional data (product_id, quantity, price, etc.)
        db: Database session
        broadcast: Whether to broadcast via WebSocket
    
    Returns:
        Created Event object
    
    Side Effects:
        - Creates event in database
        - Updates customer profile
        - Broadcasts to admin via WebSocket
        - Triggers analytics updates
    """
    
    # 1. Create event in database
    event = Event(
        customer_id=customer_id,
        event_type=event_type,
        event_value=event_value,
        metadata_json=metadata or {},
        timestamp=datetime.utcnow()
    )
    
    if db:
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # 2. Update customer profile
        await update_customer_profile(customer_id, event_type, metadata, db)
    
    # 3. Broadcast to admin dashboard
    if broadcast:
        await broadcast_event(event, db)
    
    return event


async def update_customer_profile(
    customer_id: str,
    event_type: str,
    metadata: Optional[Dict[str, Any]],
    db: Session
):
    """
    Update customer profile based on event.
    
    Updates:
    - Last activity timestamp
    - Engagement score
    - Favorite category/product
    - Journey stage
    """
    
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == customer_id
    ).first()
    
    if not profile:
        # Create profile if doesn't exist
        profile = CustomerProfile(customer_id=customer_id)
        db.add(profile)
    
    # Update last activity
    profile.updated_at = datetime.utcnow()
    
    # Increment engagement based on event type
    engagement_points = {
        'USER_LOGIN': 1,
        'SEARCH': 2,
        'CATEGORY_VIEW': 1,
        'PRODUCT_VIEW': 3,
        'ADD_TO_CART': 5,
        'PURCHASE_COMPLETED': 10,
        'REVIEW_SUBMITTED': 7,
        'SUPPORT_TICKET': -2,  # Negative for support issues
        'REFUND_REQUESTED': -5,
        'CAMPAIGN_OPENED': 2,
        'CAMPAIGN_CLICKED': 4,
        'NBA_ACCEPTED': 8,
    }
    
    if event_type in engagement_points:
        profile.engagement_score = min(100, max(0, 
            (profile.engagement_score or 50) + engagement_points[event_type]
        ))
    
    # Update favorite category
    if event_type == 'PRODUCT_VIEW' and metadata and 'category' in metadata:
        # Track most viewed category
        # For now, just update to latest
        # TODO: Implement frequency tracking
        pass
    
    db.commit()


async def broadcast_event(event: Event, db: Session):
    """
    Broadcast event to admin dashboard via WebSocket.
    
    Creates a formatted message for the live activity feed.
    """
    
    # Get customer info
    from app.models.models import Customer
    customer = db.query(Customer).filter(
        Customer.customer_id == event.customer_id
    ).first()
    
    customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
    
    # Format message based on event type
    message = format_event_message(event, customer_name)
    
    # Broadcast to admin WebSocket channel
    await manager.broadcast({
        "type": "customer_activity",
        "event_id": event.event_id,
        "customer_id": event.customer_id,
        "customer_name": customer_name,
        "event_type": event.event_type,
        "event_value": event.event_value,
        "message": message,
        "timestamp": event.timestamp.isoformat(),
        "metadata": event.metadata_json
    }, room="admin")


def format_event_message(event: Event, customer_name: str) -> str:
    """
    Format event into human-readable message for admin feed.
    
    Examples:
        "Yash searched for: Laptop"
        "Yash viewed product: Nike Shoes"
        "Yash added to cart: Samsung Monitor"
        "Yash completed purchase: ₹14,999"
    """
    
    event_messages = {
        'USER_REGISTERED': f"{customer_name} registered",
        'USER_LOGIN': f"{customer_name} logged in",
        'USER_LOGOUT': f"{customer_name} logged out",
        'SEARCH': f"{customer_name} searched for: {event.event_value}",
        'CATEGORY_VIEW': f"{customer_name} browsing: {event.event_value}",
        'PRODUCT_VIEW': f"{customer_name} viewed product: {event.event_value}",
        'ADD_TO_CART': f"{customer_name} added to cart: {event.event_value}",
        'REMOVE_FROM_CART': f"{customer_name} removed from cart: {event.event_value}",
        'ADD_TO_WISHLIST': f"{customer_name} added to wishlist: {event.event_value}",
        'REMOVE_FROM_WISHLIST': f"{customer_name} removed from wishlist: {event.event_value}",
        'CHECKOUT_STARTED': f"{customer_name} started checkout",
        'PURCHASE_COMPLETED': f"{customer_name} completed purchase: {event.event_value}",
        'SUPPORT_TICKET': f"{customer_name} opened support ticket",
        'REVIEW_SUBMITTED': f"{customer_name} submitted review: {event.event_value}",
        'REFUND_REQUESTED': f"{customer_name} requested refund",
        'CAMPAIGN_OPENED': f"{customer_name} opened campaign: {event.event_value}",
        'CAMPAIGN_CLICKED': f"{customer_name} clicked campaign: {event.event_value}",
        'NBA_ACCEPTED': f"{customer_name} accepted recommendation: {event.event_value}",
        'AI_CHAT_MESSAGE': f"{customer_name} chatted with AI",
    }
    
    return event_messages.get(event.event_type, f"{customer_name} - {event.event_type}")


# Synchronous version for non-async contexts
def track_event_sync(
    customer_id: str,
    event_type: str,
    event_value: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = None
) -> Event:
    """
    Synchronous version of track_event.
    
    Use this in non-async endpoints.
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        track_event(customer_id, event_type, event_value, metadata, db, broadcast=True)
    )
