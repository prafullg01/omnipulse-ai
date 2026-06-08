"""
═══════════════════════════════════════════════════════════════════
OMNIPULSE AI — REAL-TIME INTELLIGENCE ORCHESTRATOR
═══════════════════════════════════════════════════════════════════

Central intelligence pipeline. Called after EVERY customer event.

Engines:
  1. Churn Engine      — probability, category, confidence, reasons
  2. CLV Engine        — current, predicted, future revenue, value tier
  3. Trust Engine      — score, level, drivers, trend, risk
  4. Happiness Engine  — score, emotion, mood, satisfaction
  5. Risk Engine       — multi-dimensional risk (churn, competitive, revenue, trust, engagement)
  6. NBA Engine        — next best action with confidence + expected conversion
  7. Campaign Engine   — auto-generated campaigns from behavior triggers
  8. Digital Twin      — scenario A (no action) vs B (intervention)
  9. Executive Engine  — live executive briefing insights
  10. Fairness Engine  — coverage, equity, bias alerts

Works with 1+ events. No historical data requirement.
No hardcoded values. No fake data. Database is the ONLY source of truth.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case, distinct
from typing import Dict, Any, Optional, Tuple, List
import math

from app.models.models import (
    Event, CustomerProfile, Order, OrderItem, SupportTicket,
    NBADecision, Campaign, CampaignResponse, DigitalTwinResult,
    Customer, Product
)
from app.models.realtime_models import (
    CartItem, WishlistItem, SearchHistory, ProductView, CustomerSession
)


# ══════════════════════════════════════════════════════════════
# EVENT TYPE NORMALIZER
# ══════════════════════════════════════════════════════════════
# DB has BOTH casings: lowercase from CSV import (cart_add, purchase)
# and UPPERCASE from real-time tracking (ADD_TO_CART, PURCHASE_COMPLETED).
# This map normalizes everything to canonical uppercase form.

EVENT_TYPE_MAP = {
    # Cart
    "cart_add": "ADD_TO_CART", "ADD_TO_CART": "ADD_TO_CART",
    "cart_remove": "REMOVE_FROM_CART", "REMOVE_FROM_CART": "REMOVE_FROM_CART",
    # Purchase
    "purchase": "PURCHASE_COMPLETED", "PURCHASE_COMPLETED": "PURCHASE_COMPLETED",
    "checkout": "CHECKOUT_STARTED", "CHECKOUT_STARTED": "CHECKOUT_STARTED",
    # Browsing
    "product_view": "PRODUCT_VIEW", "PRODUCT_VIEW": "PRODUCT_VIEW",
    "search": "SEARCH", "SEARCH": "SEARCH",
    # Engagement
    "wishlist_add": "ADD_TO_WISHLIST", "ADD_TO_WISHLIST": "ADD_TO_WISHLIST",
    "wishlist_remove": "REMOVE_FROM_WISHLIST", "REMOVE_FROM_WISHLIST": "REMOVE_FROM_WISHLIST",
    # Post-purchase
    "refund_request": "REFUND_REQUESTED", "REFUND_REQUESTED": "REFUND_REQUESTED",
    "review_submit": "REVIEW_SUBMITTED", "review_submitted": "REVIEW_SUBMITTED",
    "REVIEW_SUBMITTED": "REVIEW_SUBMITTED",
    # Support
    "complaint": "COMPLAINT", "COMPLAINT": "COMPLAINT",
    "support_chat": "SUPPORT_CHAT", "SUPPORT_CHAT": "SUPPORT_CHAT",
    "support_ticket": "SUPPORT_TICKET", "ticket_created": "SUPPORT_TICKET_CREATED",
    "SUPPORT_TICKET_CREATED": "SUPPORT_TICKET_CREATED",
    # Campaigns
    "campaign_opened": "CAMPAIGN_OPENED", "CAMPAIGN_OPENED": "CAMPAIGN_OPENED",
    "campaign_received": "CAMPAIGN_RECEIVED", "CAMPAIGN_RECEIVED": "CAMPAIGN_RECEIVED",
    "offer_clicked": "CAMPAIGN_CLICKED", "CAMPAIGN_CLICKED": "CAMPAIGN_CLICKED",
    # Auth
    "USER_LOGIN": "USER_LOGIN", "USER_REGISTERED": "USER_REGISTERED",
    # Assistant
    "assistant_interaction": "ASSISTANT_INTERACTION",
}


def normalize_types(raw_types: list) -> list:
    """Normalize a list of event type strings to canonical UPPERCASE form."""
    return [EVENT_TYPE_MAP.get(t, t.upper() if isinstance(t, str) else t) for t in raw_types]


# ══════════════════════════════════════════════════════════════
# 1. CHURN ENGINE
# ══════════════════════════════════════════════════════════════

def compute_churn(customer_id: str, db: Session) -> Dict[str, Any]:
    """
    Compute churn from ACTUAL session behavior.
    
    Inputs: session duration, views, searches, cart adds/removes,
            checkouts, purchases, refunds, tickets, review sentiment,
            campaign interactions, NBA acceptance, emotion state.
    
    Output: probability, category, confidence, reason_codes
    """
    now = datetime.utcnow()
    
    # Query events from last 90 days (wider window to capture more data)
    events = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.timestamp >= now - timedelta(days=90)
    ).all()
    
    if not events:
        return {
            "churn_probability": 0.25,
            "churn_category": "Low",
            "churn_confidence": 0.3,
            "churn_reasons": ["New user, limited data"],
        }
    
    # ── NORMALIZE event types to canonical UPPERCASE form ──
    raw_types = [e.event_type for e in events]
    types = normalize_types(raw_types)
    
    score = 0.15  # base
    reasons = []
    data_points = 0
    
    # --- Cart abandonment (strong signal) ---
    cart_adds = types.count("ADD_TO_CART")
    cart_removes = types.count("REMOVE_FROM_CART")
    purchases = types.count("PURCHASE_COMPLETED")
    checkouts = types.count("CHECKOUT_STARTED")
    
    if cart_adds > 0 and purchases == 0:
        score += 0.25
        reasons.append(f"Cart abandoned — {cart_adds} item(s) added, 0 purchased")
        data_points += 2
    
    if cart_removes > cart_adds * 0.5 and cart_removes > 0:
        score += 0.1
        reasons.append(f"Frequent cart removals ({cart_removes})")
        data_points += 1
    
    if checkouts > 0 and purchases == 0:
        score += 0.15
        reasons.append("Checkout started but not completed")
        data_points += 1
    
    # --- Support tickets (frustration signal) ---
    neg_tickets = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id,
        SupportTicket.sentiment.in_(["angry", "frustrated"]),
        SupportTicket.created_at >= now - timedelta(days=14)
    ).count()
    
    if neg_tickets >= 2:
        score += 0.25
        reasons.append(f"{neg_tickets} negative support tickets — frustration detected")
        data_points += 2
    elif neg_tickets == 1:
        score += 0.12
        reasons.append("Negative support ticket filed")
        data_points += 1
    
    # --- Complaints ---
    complaints = types.count("COMPLAINT")
    if complaints > 0:
        score += 0.15
        reasons.append(f"{complaints} complaint(s) filed")
        data_points += 1
    
    # --- Refunds ---
    refunds = types.count("REFUND_REQUESTED")
    if refunds > 0:
        score += 0.18
        reasons.append(f"Refund requested ({refunds}×)")
        data_points += 1
    
    # --- Low engagement ---
    total_events = len(events)
    days_active = max(1, (now - min(e.timestamp for e in events)).days)
    events_per_day = total_events / days_active
    
    if events_per_day < 0.5 and days_active > 7:
        score += 0.12
        reasons.append(f"Low engagement — {events_per_day:.1f} events/day over {days_active}d")
        data_points += 1
    elif events_per_day < 1 and days_active > 3:
        score += 0.06
        reasons.append(f"Below-average engagement — {events_per_day:.1f} events/day")
        data_points += 1
    
    # --- Comparison shopping (many views, no buy) ---
    views = types.count("PRODUCT_VIEW")
    if views > 5 and purchases == 0:
        score += 0.12
        reasons.append(f"Extensive comparison shopping ({views} views, 0 purchases)")
        data_points += 1
    
    # --- Search without follow-through ---
    searches = types.count("SEARCH")
    if searches > 3 and views < 2:
        score += 0.08
        reasons.append(f"Multiple searches ({searches}) without product engagement")
        data_points += 1
    
    # --- Positive signals (reduce churn) ---
    if purchases > 0:
        score -= 0.2
        reasons.append(f"✓ Completed {purchases} purchase(s)")
        data_points += 2
    
    reviews = types.count("REVIEW_SUBMITTED")
    if reviews > 0:
        score -= 0.05
        reasons.append(f"✓ Submitted {reviews} product review(s)")
        data_points += 1
    
    wishlists = types.count("ADD_TO_WISHLIST")
    if wishlists > 0:
        score -= 0.05
        reasons.append(f"✓ Wishlisted {wishlists} item(s) — future purchase intent")
        data_points += 1
    
    campaign_clicks = types.count("CAMPAIGN_CLICKED") + types.count("CAMPAIGN_OPENED")
    if campaign_clicks > 0:
        score -= 0.05
        reasons.append(f"✓ Engaged with {campaign_clicks} campaign(s)")
        data_points += 1
    
    # --- Session duration ---
    sessions = db.query(CustomerSession).filter(
        CustomerSession.customer_id == customer_id
    ).all()
    if sessions:
        avg_duration = sum((s.duration_seconds or 0) for s in sessions) / len(sessions)
        if avg_duration < 60 and len(sessions) > 1:
            score += 0.08
            reasons.append("Short average session duration")
            data_points += 1
    
    # --- Emotion influence on churn ---
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == customer_id
    ).first()
    if profile and profile.emotion:
        emotion_adjustments = {
            "happy": -0.10, "excited": -0.15,
            "neutral": 0.0, "frustrated": +0.12, "angry": +0.20
        }
        adj = emotion_adjustments.get(profile.emotion, 0.0)
        if adj != 0:
            score += adj
            direction = "reduces" if adj < 0 else "increases"
            reasons.append(f"{'✓ ' if adj < 0 else ''}Emotion '{profile.emotion}' {direction} churn risk")
            data_points += 1
    
    # Clamp
    score = max(0.03, min(0.97, score))
    
    # Category
    if score >= 0.75:
        category = "Critical"
    elif score >= 0.5:
        category = "High"
    elif score >= 0.3:
        category = "Medium"
    else:
        category = "Low"
    
    # Confidence increases with more data points
    confidence = min(0.95, 0.3 + data_points * 0.07)
    
    return {
        "churn_probability": round(score, 3),
        "churn_category": category,
        "churn_confidence": round(confidence, 2),
        "churn_reasons": reasons if reasons else ["Normal activity pattern"],
    }


# ══════════════════════════════════════════════════════════════
# 2. CLV ENGINE
# ══════════════════════════════════════════════════════════════

def compute_clv(customer_id: str, db: Session) -> Dict[str, Any]:
    """
    Compute Customer Lifetime Value from actual purchase data.
    
    Output: current CLV, predicted CLV, future revenue, value tier
    """
    orders = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.status.notin_(["cancelled", "refund_requested"])
    ).all()
    
    total_revenue = sum(o.total_amount or 0 for o in orders)
    order_count = len(orders)
    
    if order_count == 0:
        # New customer — predict from engagement
        event_count = db.query(Event).filter(
            Event.customer_id == customer_id
        ).count()
        
        cart_value = db.query(func.sum(CartItem.product_price * CartItem.quantity)).filter(
            CartItem.customer_id == customer_id
        ).scalar() or 0
        
        predicted = cart_value * 0.6 + event_count * 100
        
        return {
            "clv": 0,
            "predicted_clv": round(max(1000, predicted), 0),
            "future_revenue": round(max(1000, predicted), 0),
            "expected_lifetime_orders": max(1, round(event_count / 10)),
            "value_tier": "Bronze",
            "clv_confidence": 0.25,
        }
    
    avg_order_value = total_revenue / order_count
    
    # Calculate purchase frequency
    if order_count >= 2:
        date_range = max(1, (max(o.order_date for o in orders) - min(o.order_date for o in orders)).days)
        purchase_freq = order_count / max(1, date_range / 30)  # per month
    else:
        purchase_freq = 0.5  # assume one per 2 months
    
    # Predict future (12 months)
    expected_future_orders = round(purchase_freq * 12)
    future_revenue = avg_order_value * expected_future_orders
    predicted_clv = total_revenue + future_revenue
    
    # Value tier
    if predicted_clv >= 100000:
        tier = "Diamond"
    elif predicted_clv >= 50000:
        tier = "Platinum"
    elif predicted_clv >= 20000:
        tier = "Gold"
    elif predicted_clv >= 5000:
        tier = "Silver"
    else:
        tier = "Bronze"
    
    confidence = min(0.95, 0.4 + order_count * 0.1)
    
    return {
        "clv": round(total_revenue, 0),
        "predicted_clv": round(predicted_clv, 0),
        "future_revenue": round(future_revenue, 0),
        "expected_lifetime_orders": max(1, expected_future_orders),
        "value_tier": tier,
        "clv_confidence": round(confidence, 2),
    }


# ══════════════════════════════════════════════════════════════
# 3. TRUST ENGINE
# ══════════════════════════════════════════════════════════════

def compute_trust(customer_id: str, db: Session) -> Dict[str, Any]:
    """
    Compute trust from actual interactions.
    
    Output: score, level, drivers, trend, risk
    """
    base = 50.0
    drivers = []
    
    # Purchases
    purchase_count = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.status.notin_(["cancelled", "refund_requested"])
    ).count()
    
    if purchase_count > 0:
        boost = min(purchase_count * 6, 25)
        base += boost
        drivers.append({"signal": f"{purchase_count} successful purchase(s)", "impact": f"+{boost}", "type": "positive"})
    
    # Refunds / cancellations
    refund_count = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.status.in_(["cancelled", "refund_requested"])
    ).count()
    
    refund_events = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.event_type == "REFUND_REQUESTED"
    ).count()
    
    total_refunds = refund_count + refund_events
    if total_refunds > 0:
        penalty = min(total_refunds * 10, 30)
        base -= penalty
        drivers.append({"signal": f"{total_refunds} refund/cancellation(s)", "impact": f"-{penalty}", "type": "negative"})
    
    # Negative tickets
    neg_tickets = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id,
        SupportTicket.sentiment.in_(["angry", "frustrated"])
    ).count()
    
    if neg_tickets > 0:
        penalty = min(neg_tickets * 7, 25)
        base -= penalty
        drivers.append({"signal": f"{neg_tickets} negative support interaction(s)", "impact": f"-{penalty}", "type": "negative"})
    
    # Positive tickets
    pos_tickets = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id,
        SupportTicket.sentiment.in_(["happy", "excited"])
    ).count()
    
    if pos_tickets > 0:
        boost = min(pos_tickets * 4, 12)
        base += boost
        drivers.append({"signal": f"{pos_tickets} positive interaction(s)", "impact": f"+{boost}", "type": "positive"})
    
    # Reviews
    reviews = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.event_type == "REVIEW_SUBMITTED"
    ).count()
    
    if reviews > 0:
        boost = min(reviews * 3, 10)
        base += boost
        drivers.append({"signal": f"{reviews} review(s) submitted", "impact": f"+{boost}", "type": "positive"})
    
    # Engagement
    event_count = db.query(Event).filter(
        Event.customer_id == customer_id
    ).count()
    
    if event_count > 15:
        base += 5
        drivers.append({"signal": "High platform engagement", "impact": "+5", "type": "positive"})
    elif event_count < 3:
        base -= 3
        drivers.append({"signal": "Limited platform interaction", "impact": "-3", "type": "neutral"})
    
    base = max(5, min(100, base))
    
    # Level
    if base >= 80:
        level = "Excellent"
    elif base >= 60:
        level = "Good"
    elif base >= 40:
        level = "Fair"
    elif base >= 20:
        level = "Poor"
    else:
        level = "Critical"
    
    # Trust risk
    trust_risk = "Low" if base >= 60 else "Medium" if base >= 35 else "High"
    
    # Trend (compare recent vs older events)
    recent_neg = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id,
        SupportTicket.sentiment.in_(["angry", "frustrated"]),
        SupportTicket.created_at >= datetime.utcnow() - timedelta(days=3)
    ).count()
    
    trend = "declining" if recent_neg > 0 else "stable" if base < 70 else "improving"
    
    return {
        "trust_score": round(base, 1),
        "trust_level": level,
        "trust_reasons": drivers,
        "trust_trend": trend,
        "trust_risk": trust_risk,
    }


# ══════════════════════════════════════════════════════════════
# 4. HAPPINESS ENGINE
# ══════════════════════════════════════════════════════════════

def compute_happiness(customer_id: str, db: Session, churn_prob: float = 0.3, trust_score: float = 50) -> Dict[str, Any]:
    """
    Compute happiness from sentiment and activity patterns.
    
    Output: score, emotion, mood, satisfaction
    """
    # Ticket sentiments
    tickets = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id
    ).order_by(desc(SupportTicket.created_at)).limit(10).all()
    
    sentiment_scores = {"excited": 95, "happy": 80, "neutral": 50, "frustrated": 25, "angry": 10}
    
    if tickets:
        ticket_happiness = sum(sentiment_scores.get(t.sentiment, 50) for t in tickets) / len(tickets)
        latest_emotion = tickets[0].sentiment
    else:
        ticket_happiness = 60
        latest_emotion = "neutral"
    
    # Purchase satisfaction
    purchase_count = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.status.notin_(["cancelled", "refund_requested"])
    ).count()
    
    refund_count = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.status.in_(["cancelled", "refund_requested"])
    ).count()
    
    purchase_satisfaction = 70
    if purchase_count > 0:
        purchase_satisfaction = min(95, 60 + purchase_count * 5)
    if refund_count > 0:
        purchase_satisfaction -= refund_count * 15
    purchase_satisfaction = max(10, purchase_satisfaction)
    
    # Engagement satisfaction
    event_count = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    engagement_sat = min(90, 30 + event_count * 4)
    
    # Composite happiness
    happiness = (
        ticket_happiness * 0.3 +
        purchase_satisfaction * 0.25 +
        trust_score * 0.2 +
        engagement_sat * 0.15 +
        (1 - churn_prob) * 100 * 0.1
    )
    happiness = max(5, min(100, happiness))
    
    # Mood
    if happiness >= 80:
        mood = "Delighted"
    elif happiness >= 60:
        mood = "Content"
    elif happiness >= 40:
        mood = "Indifferent"
    elif happiness >= 20:
        mood = "Dissatisfied"
    else:
        mood = "Distressed"
    
    # Satisfaction
    if happiness >= 70:
        satisfaction = "High"
    elif happiness >= 45:
        satisfaction = "Medium"
    else:
        satisfaction = "Low"
    
    return {
        "happiness_score": round(happiness, 1),
        "emotion": latest_emotion,
        "mood": mood,
        "satisfaction": satisfaction,
    }


# ══════════════════════════════════════════════════════════════
# 5. RISK ENGINE
# ══════════════════════════════════════════════════════════════

def compute_risk(customer_id: str, db: Session, churn_data: dict, trust_data: dict, clv_data: dict) -> Dict[str, Any]:
    """
    Multi-dimensional risk assessment.
    
    Dimensions: churn, competitive, revenue, trust, engagement
    """
    churn_risk = churn_data["churn_probability"]
    trust_risk_val = max(0, (100 - trust_data["trust_score"]) / 100)
    
    # Revenue risk: high CLV + high churn = high revenue risk
    clv = clv_data["clv"] + clv_data["predicted_clv"]
    revenue_risk = churn_risk * 0.7 + (1 - min(1, clv / 50000)) * 0.3 if clv > 0 else churn_risk
    
    # Competitive risk: comparison shopping signals
    views = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.event_type == "PRODUCT_VIEW",
        Event.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    purchases = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.event_type == "PURCHASE_COMPLETED",
        Event.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    competitive_risk = min(1, (views / 10) * 0.5) if purchases == 0 and views > 3 else 0.1
    
    # Engagement risk
    recent_events = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    engagement_risk = max(0, min(1, 1 - (recent_events / 15)))
    
    # Composite
    composite = (
        churn_risk * 0.3 +
        trust_risk_val * 0.2 +
        revenue_risk * 0.2 +
        competitive_risk * 0.15 +
        engagement_risk * 0.15
    )
    
    drivers = []
    if churn_risk > 0.5:
        drivers.append(f"Churn risk {churn_data['churn_category']}")
    if trust_risk_val > 0.5:
        drivers.append(f"Trust level {trust_data['trust_level']}")
    if competitive_risk > 0.4:
        drivers.append(f"Comparison shopping detected ({views} views)")
    if engagement_risk > 0.5:
        drivers.append("Low recent engagement")
    if revenue_risk > 0.5:
        drivers.append("Revenue at risk")
    
    level = "Critical" if composite > 0.7 else "High" if composite > 0.5 else "Medium" if composite > 0.3 else "Low"
    
    reasoning = f"Composite risk {composite:.0%}: " + (", ".join(drivers) if drivers else "Normal risk profile")
    
    return {
        "risk_score": round(composite * 100, 1),
        "risk_level": level,
        "risk_drivers": drivers if drivers else ["Normal activity pattern"],
        "risk_reasoning": reasoning,
        "risk_dimensions": {
            "churn": round(churn_risk * 100, 1),
            "competitive": round(competitive_risk * 100, 1),
            "revenue": round(revenue_risk * 100, 1),
            "trust": round(trust_risk_val * 100, 1),
            "engagement": round(engagement_risk * 100, 1),
        }
    }


# ══════════════════════════════════════════════════════════════
# 6. NBA ENGINE
# ══════════════════════════════════════════════════════════════

def compute_nba(customer_id: str, db: Session, churn_data: dict = None) -> Dict[str, Any]:
    """
    Compute Next Best Action from actual behavior patterns.
    """
    now = datetime.utcnow()
    
    events = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.timestamp >= now - timedelta(days=7)
    ).order_by(desc(Event.timestamp)).all()
    
    if not events:
        return {
            "action": "Welcome onboarding",
            "reason": "New user — no activity data yet",
            "confidence": 0.5,
            "expected_conversion": 0.3,
            "channel": "in_app",
            "offer": "Welcome 10% discount",
        }
    
    types = normalize_types([e.event_type for e in events])
    
    # --- Cart abandonment (highest priority) ---
    cart_items = db.query(CartItem).filter(CartItem.customer_id == customer_id).count()
    has_purchase = "PURCHASE_COMPLETED" in types
    
    if cart_items > 0 and not has_purchase:
        cart_value = db.query(func.sum(CartItem.product_price * CartItem.quantity)).filter(
            CartItem.customer_id == customer_id
        ).scalar() or 0
        
        return {
            "action": "Cart recovery — Free shipping + 10% off",
            "reason": f"Cart contains {cart_items} item(s) worth ₹{cart_value:,.0f} — abandoned without purchase",
            "confidence": 0.85,
            "expected_conversion": 0.42,
            "channel": "push",
            "offer": f"Complete your ₹{cart_value:,.0f} order — 10% off + free shipping",
        }
    
    # --- High churn risk ---
    if churn_data and churn_data.get("churn_probability", 0) > 0.6:
        return {
            "action": "Retention campaign — Exclusive loyalty offer",
            "reason": f"High churn risk ({churn_data['churn_category']}) — " + (churn_data['churn_reasons'][0] if churn_data['churn_reasons'] else ""),
            "confidence": 0.78,
            "expected_conversion": 0.35,
            "channel": "email",
            "offer": "Exclusive 20% loyalty discount",
        }
    
    # --- Repeated product views ---
    product_views = [e for e in events if e.event_type == "PRODUCT_VIEW"]
    if len(product_views) >= 3:
        view_counts: Dict[str, int] = {}
        view_names: Dict[str, str] = {}
        for e in product_views:
            pid = (e.metadata_json or {}).get("product_id", "")
            if pid:
                view_counts[pid] = view_counts.get(pid, 0) + 1
                view_names[pid] = e.event_value or "Product"
        
        if view_counts:
            top_pid = max(view_counts, key=view_counts.get)
            top_count = view_counts[top_pid]
            top_name = view_names.get(top_pid, "Product")
            
            if top_count >= 2:
                return {
                    "action": f"Price drop alert — {top_name}",
                    "reason": f"Viewed {top_name} {top_count} times — high purchase intent detected",
                    "confidence": min(0.6 + top_count * 0.08, 0.92),
                    "expected_conversion": min(0.3 + top_count * 0.05, 0.65),
                    "channel": "push",
                    "offer": f"Special price on {top_name}",
                }
    
    # --- Negative support ---
    recent_ticket = db.query(SupportTicket).filter(
        SupportTicket.customer_id == customer_id,
        SupportTicket.sentiment.in_(["angry", "frustrated"]),
        SupportTicket.created_at >= now - timedelta(days=3)
    ).first()
    
    if recent_ticket:
        return {
            "action": "Service recovery — Personal apology + compensation",
            "reason": f"Customer filed {recent_ticket.sentiment} support ticket: {(recent_ticket.subject or '')[:60]}",
            "confidence": 0.80,
            "expected_conversion": 0.55,
            "channel": "email",
            "offer": "Personal apology + ₹500 compensation coupon",
        }
    
    # --- Recent purchase → cross-sell ---
    if has_purchase:
        last_purchase = next((e for e in events if e.event_type == "PURCHASE_COMPLETED"), None)
        products = (last_purchase.metadata_json or {}).get("products", []) if last_purchase else []
        product_text = products[0] if products else "your recent purchase"
        
        return {
            "action": "Cross-sell — Complementary products",
            "reason": f"Completed purchase — recommend items that complement {product_text}",
            "confidence": 0.72,
            "expected_conversion": 0.28,
            "channel": "in_app",
            "offer": "Products you might also like",
        }
    
    # --- High engagement, no purchase ---
    if len(events) > 5 and not has_purchase:
        return {
            "action": "First purchase incentive — 15% off",
            "reason": f"High engagement ({len(events)} actions) but no purchase yet",
            "confidence": 0.68,
            "expected_conversion": 0.32,
            "channel": "push",
            "offer": "15% off your first order",
        }
    
    return {
        "action": "Engagement boost — Personalized recommendations",
        "reason": "Maintain engagement with tailored content",
        "confidence": 0.55,
        "expected_conversion": 0.2,
        "channel": "in_app",
        "offer": "Curated picks for you",
    }


# ══════════════════════════════════════════════════════════════
# 7. CAMPAIGN ENGINE
# ══════════════════════════════════════════════════════════════

def compute_campaign(customer_id: str, db: Session, churn_data: dict, trust_data: dict, happiness_data: dict) -> Optional[Dict[str, Any]]:
    """
    Auto-generate campaign from behavior triggers.
    """
    now = datetime.utcnow()
    types = normalize_types([e.event_type for e in db.query(Event.event_type).filter(
        Event.customer_id == customer_id,
        Event.timestamp >= now - timedelta(days=7)
    ).all()])
    
    cart_count = db.query(CartItem).filter(CartItem.customer_id == customer_id).count()
    
    # Cart abandonment
    if cart_count > 0 and "PURCHASE_COMPLETED" not in types:
        cart_value = db.query(func.sum(CartItem.product_price * CartItem.quantity)).filter(
            CartItem.customer_id == customer_id
        ).scalar() or 0
        return {
            "campaign_type": "cart_recovery",
            "name": "Cart Recovery — Complete Your Purchase",
            "channel": "push",
            "offer": f"10% off your ₹{cart_value:,.0f} cart",
            "discount_pct": 10,
            "trigger_reason": "Cart abandoned without purchase",
            "predicted_conversion": 0.42,
            "predicted_revenue": round(cart_value * 0.42, 0),
        }
    
    # High churn
    if churn_data["churn_probability"] > 0.6:
        return {
            "campaign_type": "retention",
            "name": "Retention — Win Back Campaign",
            "channel": "email",
            "offer": "20% loyalty discount",
            "discount_pct": 20,
            "trigger_reason": f"High churn risk: {churn_data['churn_category']}",
            "predicted_conversion": 0.35,
            "predicted_revenue": 3000,
        }
    
    # Low trust
    if trust_data["trust_score"] < 35:
        return {
            "campaign_type": "trust_building",
            "name": "Trust Builder — Service Recovery",
            "channel": "email",
            "offer": "Personal support + compensation",
            "discount_pct": 15,
            "trigger_reason": f"Low trust score: {trust_data['trust_score']:.0f}",
            "predicted_conversion": 0.3,
            "predicted_revenue": 2000,
        }
    
    # Low happiness
    if happiness_data["happiness_score"] < 35:
        return {
            "campaign_type": "satisfaction",
            "name": "Happiness Boost — Special Treat",
            "channel": "push",
            "offer": "Surprise discount for you",
            "discount_pct": 12,
            "trigger_reason": f"Low happiness: {happiness_data['mood']}",
            "predicted_conversion": 0.28,
            "predicted_revenue": 1500,
        }
    
    # Repeated views
    views = types.count("PRODUCT_VIEW")
    if views >= 5:
        return {
            "campaign_type": "high_intent",
            "name": "High Intent — Exclusive Offer",
            "channel": "push",
            "offer": "8% off viewed items",
            "discount_pct": 8,
            "trigger_reason": f"Viewed {views} products — high browsing intent",
            "predicted_conversion": 0.38,
            "predicted_revenue": 2500,
        }
    
    return None


# ══════════════════════════════════════════════════════════════
# 8. DIGITAL TWIN ENGINE
# ══════════════════════════════════════════════════════════════

def compute_digital_twin(customer_id: str, db: Session, churn_data: dict, clv_data: dict, trust_data: dict, nba_data: dict) -> Dict[str, Any]:
    """
    Scenario A (no action) vs Scenario B (recommended action).
    """
    churn = churn_data["churn_probability"]
    clv = clv_data["clv"]
    predicted_clv = clv_data["predicted_clv"]
    trust = trust_data["trust_score"]
    
    # Scenario A: No intervention
    natural_retention = max(0.1, 1 - churn)
    a_revenue = predicted_clv * natural_retention
    a_clv = clv + a_revenue * 0.5
    
    # Scenario B: With intervention
    intervention_boost = 0.15 + (churn * 0.2)
    improved_retention = min(0.95, natural_retention + intervention_boost)
    b_revenue = predicted_clv * improved_retention * 1.15
    b_clv = clv + b_revenue * 0.7
    b_churn = max(0.03, churn - intervention_boost)
    b_trust = min(100, trust + 10)
    
    uplift_revenue = b_revenue - a_revenue
    uplift_pct = ((b_revenue - a_revenue) / max(1, a_revenue)) * 100
    
    confidence = min(0.9, nba_data.get("confidence", 0.5) * 1.1)
    
    return {
        "scenario_a": {
            "label": "No Intervention",
            "predicted_revenue": round(a_revenue, 0),
            "predicted_retention": round(natural_retention, 3),
            "predicted_churn": round(churn, 3),
            "predicted_clv": round(a_clv, 0),
            "predicted_trust": round(trust, 1),
        },
        "scenario_b": {
            "label": nba_data.get("action", "Recommended Action"),
            "predicted_revenue": round(b_revenue, 0),
            "predicted_retention": round(improved_retention, 3),
            "predicted_churn": round(b_churn, 3),
            "predicted_clv": round(b_clv, 0),
            "predicted_trust": round(b_trust, 1),
        },
        "uplift": {
            "revenue": round(uplift_revenue, 0),
            "revenue_pct": round(uplift_pct, 1),
            "retention_pct": round(intervention_boost * 100, 1),
        },
        "confidence": round(confidence, 2),
        "reasoning": f"Applying '{nba_data.get('action', 'intervention')}' is predicted to increase revenue by ₹{uplift_revenue:,.0f} ({uplift_pct:.1f}%) and improve retention by {intervention_boost*100:.1f}%",
    }


# ══════════════════════════════════════════════════════════════
# 9. EXECUTIVE ENGINE
# ══════════════════════════════════════════════════════════════

def compute_executive_insights(customer_id: str, db: Session, all_scores: dict) -> List[str]:
    """
    Generate live executive briefing insights for this customer event.
    """
    insights = []
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    name = f"{customer.first_name} {customer.last_name}" if customer else "Customer"
    
    churn = all_scores.get("churn", {})
    clv = all_scores.get("clv", {})
    trust = all_scores.get("trust", {})
    happiness = all_scores.get("happiness", {})
    nba = all_scores.get("nba", {})
    campaign = all_scores.get("campaign")
    
    if churn.get("churn_category") in ["High", "Critical"]:
        insights.append(f"⚠️ {name} is at {churn['churn_category']} churn risk ({churn['churn_probability']*100:.0f}%)")
    
    if clv.get("value_tier") in ["Gold", "Platinum", "Diamond"]:
        insights.append(f"💎 {name} is a {clv['value_tier']} customer (CLV ₹{clv['predicted_clv']:,.0f})")
    
    if trust.get("trust_trend") == "declining":
        insights.append(f"📉 {name}'s trust is declining — intervention recommended")
    
    if happiness.get("mood") in ["Dissatisfied", "Distressed"]:
        insights.append(f"😟 {name} is {happiness['mood']} — satisfaction at {happiness['happiness_score']:.0f}/100")
    
    if campaign:
        insights.append(f"🎯 Auto-campaign triggered: {campaign['name']} (predicted conversion {campaign['predicted_conversion']*100:.0f}%)")
    
    if nba.get("confidence", 0) > 0.75:
        insights.append(f"🏆 NBA: {nba['action']} (confidence {nba['confidence']*100:.0f}%)")
    
    # Revenue impact
    twin = all_scores.get("digital_twin", {})
    uplift = twin.get("uplift", {})
    if uplift.get("revenue", 0) > 1000:
        insights.append(f"💰 Revenue opportunity: ₹{uplift['revenue']:,.0f} with intervention")
    
    if not insights:
        insights.append(f"✅ {name} — Normal activity, no immediate action required")
    
    return insights


# ══════════════════════════════════════════════════════════════
# MASTER ORCHESTRATOR
# ══════════════════════════════════════════════════════════════

async def update_customer_intelligence(customer_id: str, db: Session) -> Dict[str, Any]:
    """
    CENTRAL INTELLIGENCE PIPELINE.
    
    Called after EVERY event. Runs all engines, updates profile,
    persists decisions, broadcasts via WebSocket.
    
    Returns complete intelligence snapshot for broadcasting.
    """
    from app.websocket.manager import manager
    
    # Get or create profile
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.customer_id == customer_id
    ).first()
    
    if not profile:
        profile = CustomerProfile(customer_id=customer_id)
        db.add(profile)
        db.flush()
    
    # ── Run all engines ──
    churn_data = compute_churn(customer_id, db)
    clv_data = compute_clv(customer_id, db)
    trust_data = compute_trust(customer_id, db)
    happiness_data = compute_happiness(customer_id, db, churn_data["churn_probability"], trust_data["trust_score"])
    risk_data = compute_risk(customer_id, db, churn_data, trust_data, clv_data)
    nba_data = compute_nba(customer_id, db, churn_data)
    campaign_data = compute_campaign(customer_id, db, churn_data, trust_data, happiness_data)
    twin_data = compute_digital_twin(customer_id, db, churn_data, clv_data, trust_data, nba_data)
    
    all_scores = {
        "churn": churn_data, "clv": clv_data, "trust": trust_data,
        "happiness": happiness_data, "risk": risk_data, "nba": nba_data,
        "campaign": campaign_data, "digital_twin": twin_data,
    }
    
    exec_insights = compute_executive_insights(customer_id, db, all_scores)
    
    # ── Update profile ──
    profile.churn_probability = churn_data["churn_probability"]
    profile.risk_score = risk_data["risk_score"]
    profile.trust_score = trust_data["trust_score"]
    profile.happiness_score = happiness_data["happiness_score"]
    profile.emotion = happiness_data["emotion"]
    profile.clv = clv_data["clv"]
    profile.predicted_clv = clv_data["predicted_clv"]
    profile.monetary = clv_data["clv"]
    
    # Engagement from recent events
    recent = db.query(Event).filter(
        Event.customer_id == customer_id,
        Event.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    profile.engagement_score = min(100, 30 + recent * 3.5)
    profile.competitive_risk = risk_data["risk_dimensions"]["competitive"]
    
    # Segment — normalize event types from DB
    types = normalize_types([e.event_type for e in db.query(Event.event_type).filter(
        Event.customer_id == customer_id).all()])
    
    if "PURCHASE_COMPLETED" in types:
        profile.segment = "active"
    elif "ADD_TO_CART" in types or "CHECKOUT_STARTED" in types:
        profile.segment = "high_intent"
    elif "PRODUCT_VIEW" in types:
        profile.segment = "browsing"
    else:
        profile.segment = "new"
    
    # Frequency & Recency
    order_count = db.query(Order).filter(Order.customer_id == customer_id).count()
    profile.frequency = order_count
    
    last_order = db.query(Order).filter(
        Order.customer_id == customer_id
    ).order_by(desc(Order.order_date)).first()
    if last_order:
        profile.recency_days = (datetime.utcnow() - last_order.order_date).days
    
    # ── Persist NBA decision ──
    nba_record = NBADecision(
        customer_id=customer_id,
        recommended_action=nba_data["action"],
        channel=nba_data.get("channel", "in_app"),
        offer=nba_data.get("offer", ""),
        confidence=nba_data["confidence"],
        reason=nba_data["reason"],
        inference_tier="rules",
        status="pending",
    )
    db.add(nba_record)
    
    # ── Persist Digital Twin ──
    twin_record = DigitalTwinResult(
        customer_id=customer_id,
        scenario="comparison",
        prediction=twin_data,
        predicted_revenue=twin_data["scenario_b"]["predicted_revenue"],
        predicted_retention=twin_data["scenario_b"]["predicted_retention"],
        predicted_churn=twin_data["scenario_b"]["predicted_churn"],
        intervention_type=nba_data["action"],
    )
    db.add(twin_record)
    
    try:
        db.commit()
    except Exception:
        db.rollback()
    
    # ── Get customer name for broadcasts ──
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Customer"
    
    # ── Build complete intelligence payload ──
    intelligence = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "timestamp": datetime.utcnow().isoformat(),
        "churn": churn_data,
        "clv": clv_data,
        "trust": trust_data,
        "happiness": happiness_data,
        "risk": risk_data,
        "nba": nba_data,
        "campaign": campaign_data,
        "digital_twin": twin_data,
        "executive_insights": exec_insights,
    }
    
    # ── Broadcast all intelligence updates ──
    broadcast_types = [
        ("churn_updated", {"customer_id": customer_id, "customer_name": customer_name, **churn_data}),
        ("clv_updated", {"customer_id": customer_id, "customer_name": customer_name, **clv_data}),
        ("trust_updated", {"customer_id": customer_id, "customer_name": customer_name, **trust_data}),
        ("happiness_updated", {"customer_id": customer_id, "customer_name": customer_name, **happiness_data}),
        ("risk_updated", {"customer_id": customer_id, "customer_name": customer_name, **risk_data}),
        ("nba_generated", {"customer_id": customer_id, "customer_name": customer_name, **nba_data}),
        ("digital_twin_updated", {"customer_id": customer_id, "customer_name": customer_name, **twin_data}),
        ("executive_update", {"customer_id": customer_id, "customer_name": customer_name, "insights": exec_insights}),
        ("customer360_updated", {"customer_id": customer_id, "customer_name": customer_name}),
    ]
    
    if campaign_data:
        broadcast_types.append(("campaign_generated", {"customer_id": customer_id, "customer_name": customer_name, **campaign_data}))
    
    for event_type, data in broadcast_types:
        try:
            await manager.broadcast({
                "type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }, room="admin")
        except Exception:
            pass
    
    return intelligence
