"""
Copilot Service — The AI brain of the Marketer Agent Copilot.

Pipeline:  Question → Intent Detection → DB Context Retrieval → Gemini Prompt → Stream Response → Save Memory

All database access is READ-ONLY via SQLAlchemy ORM.
"""
import os
import re
import json
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

from google import genai
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text

from app.models.models import (
    Customer, CustomerProfile, Order, Event, Campaign, CampaignResponse,
    SupportTicket, NBADecision, Product, CopilotConversation,
)
from app.models.realtime_models import CartItem, WishlistItem, SearchHistory, CustomerSession


# ── Gemini Setup ────────────────────────────────────────────────
_gemini_client = None

def _ensure_gemini():
    global _gemini_client
    if _gemini_client is not None:
        return
    from app.config import get_settings
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env")
    _gemini_client = genai.Client(api_key=api_key)


SYSTEM_PROMPT = """\
You are **OmniPulse AI Copilot** — a senior marketing intelligence assistant connected to a live customer data platform.

Your capabilities:
- Query real-time customer profiles, churn predictions, trust scores, engagement metrics
- Analyze revenue, campaign performance, ROI attribution
- Provide actionable marketing recommendations grounded in data
- Look up individual customers by ID or name

Rules:
1. ALWAYS base answers on the DATABASE CONTEXT provided. Never fabricate numbers.
2. Use ₹ (Indian Rupees) for currency.
3. Format numbers with commas (e.g. ₹4,198,780).
4. Use markdown formatting: **bold** for emphasis, tables for comparisons, bullet lists for recommendations.
5. When showing customer data, use markdown tables.
6. Be concise but thorough. Aim for 150-300 words unless the user asks for detail.
7. If the database context doesn't contain enough information to answer, say so honestly.
8. End responses with 1-2 actionable next steps when appropriate.
9. Never reveal raw SQL queries or internal system details to the user.
10. Address the user as a marketing professional.
"""


# ── Intent Detection ────────────────────────────────────────────

INTENT_PATTERNS = {
    "churn": [
        r"\bchurn\b", r"\bleaving\b", r"\bat.?risk\b", r"\bhigh.?risk\b",
        r"\bretention\b", r"\blose\b", r"\blosing\b", r"\bdefect\b",
    ],
    "revenue": [
        r"\brevenue\b", r"\bsales\b", r"\bincome\b", r"\bearning\b",
        r"\bmoney\b", r"\bspend\b", r"\border value\b", r"\bGMV\b",
    ],
    "campaign": [
        r"\bcampaign\b", r"\bmarketing\b", r"\bROI\b", r"\bconversion\b",
        r"\bemail marketing\b", r"\bsend\b", r"\bopen rate\b",
    ],
    "customer_lookup": [
        r"\bCUST-\w+\b", r"\bcustomer\s+\d+\b", r"\bshow\s+(me\s+)?customer\b",
        r"\btell\s+(me\s+)?about\s+\w+\b", r"\blook\s*up\b", r"\bprofile\s+of\b",
    ],
    "trust": [
        r"\btrust\b", r"\breliab\b", r"\breturn rate\b", r"\bcomplaint\b",
    ],
    "emotion": [
        r"\bemotion\b", r"\bsentiment\b", r"\bhappiness\b", r"\bhappy\b",
        r"\bangry\b", r"\bfrustrat\b", r"\bsatisf\b",
    ],
    "product": [
        r"\bproduct\b", r"\bcatalog\b", r"\bitem\b", r"\bcategory\b",
        r"\bbest.?sell\b", r"\btop\s+product\b",
    ],
    "cart": [
        r"\bcart\b", r"\babandon\b", r"\bcheckout\b", r"\bwishlist\b",
    ],
    "fairness": [
        r"\bfairness\b", r"\bbias\b", r"\bequity\b", r"\bgender\b",
        r"\bdemograph\b", r"\bdiversit\b",
    ],
    "nba": [
        r"\bNBA\b", r"\bnext.?best.?action\b", r"\brecommendation\b",
        r"\bintervention\b", r"\boffer\b",
    ],
    "session": [
        r"\bsession\b", r"\bonline\b", r"\bactive\s+user\b",
        r"\blogged\s+in\b", r"\blive\s+user\b",
    ],
}


def detect_intent(message: str) -> str:
    """Classify user message into a domain intent using regex patterns."""
    msg_lower = message.lower()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, msg_lower))
        if score > 0:
            scores[intent] = score

    if not scores:
        return "general"

    # Check for customer lookup with ID
    cust_id_match = re.search(r"CUST-\w+", message, re.IGNORECASE)
    if cust_id_match:
        return "customer_lookup"

    return max(scores, key=scores.get)


def extract_customer_id(message: str) -> Optional[str]:
    """Extract a CUST-XXXXX ID from the message if present."""
    match = re.search(r"(CUST-\w+)", message, re.IGNORECASE)
    return match.group(1).upper() if match else None


# ── Database Context Retrieval ──────────────────────────────────

def get_context(intent: str, message: str, db: Session) -> tuple[str, list[dict]]:
    """
    Query the database for context relevant to the detected intent.
    Returns (context_string, references).
    """
    references = []

    if intent == "churn":
        return _context_churn(db, references)
    elif intent == "revenue":
        return _context_revenue(db, references)
    elif intent == "campaign":
        return _context_campaign(db, references)
    elif intent == "customer_lookup":
        return _context_customer_lookup(message, db, references)
    elif intent == "trust":
        return _context_trust(db, references)
    elif intent == "emotion":
        return _context_emotion(db, references)
    elif intent == "product":
        return _context_product(db, references)
    elif intent == "cart":
        return _context_cart(db, references)
    elif intent == "fairness":
        return _context_fairness(db, references)
    elif intent == "nba":
        return _context_nba(db, references)
    elif intent == "session":
        return _context_session(db, references)
    else:
        return _context_general(db, references)


def _context_churn(db: Session, refs: list) -> tuple[str, list]:
    total = db.query(Customer).filter(Customer.role == "customer").count()

    dist = {
        "low": db.query(CustomerProfile).filter(CustomerProfile.churn_probability < 0.3).count(),
        "medium": db.query(CustomerProfile).filter(CustomerProfile.churn_probability.between(0.3, 0.6)).count(),
        "high": db.query(CustomerProfile).filter(CustomerProfile.churn_probability.between(0.6, 0.8)).count(),
        "critical": db.query(CustomerProfile).filter(CustomerProfile.churn_probability > 0.8).count(),
    }

    top_risk = (
        db.query(CustomerProfile, Customer)
        .join(Customer, CustomerProfile.customer_id == Customer.customer_id)
        .filter(CustomerProfile.churn_probability > 0.6)
        .order_by(desc(CustomerProfile.churn_probability))
        .limit(15)
        .all()
    )

    rows = []
    for p, c in top_risk:
        rows.append(
            f"| {c.customer_id} | {c.first_name} {c.last_name} | {p.churn_probability:.0%} | "
            f"{p.trust_score:.0f} | {p.engagement_score:.0f} | {p.segment or 'N/A'} | {p.emotion or 'neutral'} |"
        )

    table = (
        "| Customer ID | Name | Churn Prob | Trust | Engagement | Segment | Emotion |\n"
        "|---|---|---|---|---|---|---|\n"
        + "\n".join(rows)
    )

    ctx = (
        f"CHURN ANALYSIS:\n"
        f"Total customers: {total:,}\n"
        f"Distribution: Low={dist['low']:,} | Medium={dist['medium']:,} | High={dist['high']:,} | Critical={dist['critical']:,}\n"
        f"High+Critical: {dist['high'] + dist['critical']:,} ({(dist['high'] + dist['critical'])/max(total,1)*100:.1f}%)\n\n"
        f"Top 15 Highest-Risk Customers:\n{table}"
    )
    refs.append({"type": "churn_center", "label": "View Churn Center"})
    return ctx, refs


def _context_revenue(db: Session, refs: list) -> tuple[str, list]:
    total_rev = db.query(func.sum(Order.total_amount)).filter(Order.status != "cancelled").scalar() or 0
    total_orders = db.query(Order).filter(Order.status != "cancelled").count()
    unique_buyers = db.query(func.count(func.distinct(Order.customer_id))).scalar() or 0
    avg_order = total_rev / max(total_orders, 1)

    # Revenue at risk
    high_risk_count = db.query(CustomerProfile).filter(CustomerProfile.churn_probability > 0.7).count()
    high_risk_rev = (
        db.query(func.sum(Order.total_amount))
        .filter(
            Order.customer_id.in_(
                db.query(CustomerProfile.customer_id).filter(CustomerProfile.churn_probability > 0.7)
            ),
            Order.status != "cancelled",
        )
        .scalar() or 0
    )

    # Campaign revenue
    campaign_rev = (
        db.query(func.sum(CampaignResponse.revenue))
        .filter(CampaignResponse.converted == True)
        .scalar() or 0
    )

    ctx = (
        f"REVENUE OVERVIEW:\n"
        f"Total Revenue: ₹{total_rev:,.0f}\n"
        f"Total Orders: {total_orders:,}\n"
        f"Unique Buyers: {unique_buyers:,}\n"
        f"Average Order Value: ₹{avg_order:,.0f}\n"
        f"Campaign Revenue (direct conversions): ₹{campaign_rev:,.0f}\n"
        f"High-risk customers (>70% churn): {high_risk_count:,}\n"
        f"Revenue from high-risk customers: ₹{high_risk_rev:,.0f}\n"
        f"Potential revenue at risk: ₹{high_risk_count * avg_order:,.0f} (if non-purchasers churn)\n"
    )
    refs.append({"type": "roi_center", "label": "View ROI Center"})
    return ctx, refs


def _context_campaign(db: Session, refs: list) -> tuple[str, list]:
    campaigns = db.query(Campaign).all()
    rows = []
    for camp in campaigns:
        responses = db.query(CampaignResponse).filter(CampaignResponse.campaign_id == camp.campaign_id).all()
        sends = len(responses)
        opens = sum(1 for r in responses if r.opened)
        clicks = sum(1 for r in responses if r.clicked)
        convs = sum(1 for r in responses if r.converted)
        rev = sum(r.revenue or 0 for r in responses if r.converted)
        cost = sends * 10
        roi = ((rev - cost) / max(cost, 1)) * 100 if cost > 0 else 0
        rows.append(
            f"| {camp.campaign_name[:30]} | {camp.status} | {sends} | "
            f"{opens/max(sends,1)*100:.1f}% | {clicks/max(sends,1)*100:.1f}% | "
            f"{convs/max(sends,1)*100:.1f}% | ₹{rev:,.0f} | {roi:.0f}% |"
        )

    table = (
        "| Campaign | Status | Sends | Open Rate | Click Rate | Conv Rate | Revenue | ROI |\n"
        "|---|---|---|---|---|---|---|---|\n"
        + "\n".join(rows)
    )

    ctx = f"CAMPAIGN PERFORMANCE:\n{table}\n\nNote: Campaign cost estimated at ₹10 per send."
    refs.append({"type": "campaign_center", "label": "View Campaign Center"})
    return ctx, refs


def _context_customer_lookup(message: str, db: Session, refs: list) -> tuple[str, list]:
    cust_id = extract_customer_id(message)

    customer = None
    if cust_id:
        customer = db.query(Customer).filter(Customer.customer_id == cust_id).first()

    # Fallback: search by name
    if not customer:
        words = re.findall(r"[A-Z][a-z]+", message)
        for word in words:
            found = db.query(Customer).filter(
                (Customer.first_name.ilike(f"%{word}%")) | (Customer.last_name.ilike(f"%{word}%"))
            ).first()
            if found:
                customer = found
                break

    if not customer:
        return "No customer found matching the query. Please provide a valid Customer ID (e.g. CUST-001000) or customer name.", refs

    profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == customer.customer_id).first()
    order_count = db.query(Order).filter(Order.customer_id == customer.customer_id, Order.status != "cancelled").count()
    total_spent = db.query(func.sum(Order.total_amount)).filter(
        Order.customer_id == customer.customer_id, Order.status != "cancelled"
    ).scalar() or 0
    event_count = db.query(Event).filter(Event.customer_id == customer.customer_id).count()
    complaint_count = db.query(Event).filter(
        Event.customer_id == customer.customer_id, Event.event_type == "complaint"
    ).count()
    ticket_count = db.query(SupportTicket).filter(SupportTicket.customer_id == customer.customer_id).count()

    # NBA decision
    nba = db.query(NBADecision).filter(
        NBADecision.customer_id == customer.customer_id
    ).order_by(desc(NBADecision.timestamp)).first()

    # Campaign interactions
    campaign_count = db.query(CampaignResponse).filter(
        CampaignResponse.customer_id == customer.customer_id
    ).count()

    ctx = (
        f"CUSTOMER 360 PROFILE:\n"
        f"ID: {customer.customer_id}\n"
        f"Name: {customer.first_name} {customer.last_name}\n"
        f"Email: {customer.email}\n"
        f"Gender: {customer.gender} | Age: {customer.age} | City: {customer.city}\n"
        f"Status: {customer.status}\n\n"
        f"INTELLIGENCE SCORES:\n"
        f"Churn Probability: {profile.churn_probability:.0%}\n"
        f"Trust Score: {profile.trust_score:.1f}/100\n"
        f"Happiness Score: {profile.happiness_score:.1f}/100\n"
        f"Engagement Score: {profile.engagement_score:.1f}/100\n"
        f"Risk Score: {profile.risk_score:.1f}/100\n"
        f"CLV: ₹{profile.clv:,.0f}\n"
        f"Segment: {profile.segment}\n"
        f"Persona: {profile.persona}\n"
        f"Emotion: {profile.emotion}\n\n"
        f"ACTIVITY:\n"
        f"Total Orders: {order_count}\n"
        f"Total Spent: ₹{total_spent:,.0f}\n"
        f"Total Events: {event_count}\n"
        f"Complaints: {complaint_count}\n"
        f"Support Tickets: {ticket_count}\n"
        f"Campaign Interactions: {campaign_count}\n"
        f"RFM: Recency={profile.recency_days}d | Frequency={profile.frequency} | Monetary=₹{profile.monetary:,.0f}\n\n"
    )

    if nba:
        ctx += (
            f"LATEST NBA DECISION:\n"
            f"Action: {nba.recommended_action}\n"
            f"Channel: {nba.channel}\n"
            f"Offer: {nba.offer}\n"
            f"Confidence: {nba.confidence:.0%}\n"
            f"Reason: {nba.reason}\n"
        )

    refs.append({"type": "customer_360", "label": f"View {customer.first_name}'s 360"})
    return ctx, refs


def _context_trust(db: Session, refs: list) -> tuple[str, list]:
    avg_trust = db.query(func.avg(CustomerProfile.trust_score)).scalar() or 0
    total_customers = db.query(Customer).filter(Customer.role == "customer").count()
    customers_with_orders = db.query(func.count(func.distinct(Order.customer_id))).scalar() or 0
    total_orders = db.query(Order).count()
    delivered = db.query(Order).filter(Order.status == "delivered").count()
    refunds = db.query(Event).filter(Event.event_type == "refund_request").count()
    complaints = db.query(func.count(func.distinct(Event.customer_id))).filter(Event.event_type == "complaint").scalar() or 0

    ctx = (
        f"TRUST CENTER:\n"
        f"Average Trust Score: {avg_trust:.1f}/100\n"
        f"Purchase History: {customers_with_orders/max(total_customers,1)*100:.1f}% of customers have orders\n"
        f"Payment Reliability: {delivered/max(total_orders,1)*100:.1f}% delivered\n"
        f"Return Rate: {refunds/max(total_orders,1)*100:.1f}%\n"
        f"Complaint Rate: {complaints/max(total_customers,1)*100:.1f}% of customers filed complaints\n"
    )
    refs.append({"type": "trust_center", "label": "View Trust Center"})
    return ctx, refs


def _context_emotion(db: Session, refs: list) -> tuple[str, list]:
    emotion_dist = dict(
        db.query(CustomerProfile.emotion, func.count(CustomerProfile.customer_id))
        .group_by(CustomerProfile.emotion).all()
    )
    avg_happiness = db.query(func.avg(CustomerProfile.happiness_score)).scalar() or 0
    ticket_sentiments = dict(
        db.query(SupportTicket.sentiment, func.count(SupportTicket.ticket_id))
        .group_by(SupportTicket.sentiment).all()
    )

    ctx = (
        f"EMOTION INTELLIGENCE:\n"
        f"Average Happiness: {avg_happiness:.1f}/100\n"
        f"Emotion Distribution: {json.dumps(emotion_dist, indent=2)}\n"
        f"Support Ticket Sentiments: {json.dumps(ticket_sentiments, indent=2)}\n"
    )
    refs.append({"type": "emotion_center", "label": "View Emotion Center"})
    return ctx, refs


def _context_product(db: Session, refs: list) -> tuple[str, list]:
    total_products = db.query(Product).count()
    categories = dict(
        db.query(Product.category, func.count(Product.product_id))
        .group_by(Product.category).order_by(desc(func.count(Product.product_id))).limit(10).all()
    )
    avg_price = db.query(func.avg(Product.price)).scalar() or 0
    top_rated = (
        db.query(Product).order_by(desc(Product.rating)).limit(5).all()
    )

    rows = "\n".join(
        f"| {p.name[:40]} | {p.category} | ₹{p.price:,.0f} | {p.rating:.1f} |"
        for p in top_rated
    )
    table = "| Product | Category | Price | Rating |\n|---|---|---|---|\n" + rows

    ctx = (
        f"PRODUCT CATALOG:\n"
        f"Total Products: {total_products:,}\n"
        f"Average Price: ₹{avg_price:,.0f}\n"
        f"Top Categories: {json.dumps(categories)}\n\n"
        f"Top 5 Rated Products:\n{table}"
    )
    refs.append({"type": "products", "label": "View Products"})
    return ctx, refs


def _context_cart(db: Session, refs: list) -> tuple[str, list]:
    carts = db.query(func.count(func.distinct(CartItem.customer_id))).scalar() or 0
    total_items = db.query(CartItem).count()
    wishlists = db.query(func.count(func.distinct(WishlistItem.customer_id))).scalar() or 0

    ctx = (
        f"CART & WISHLIST:\n"
        f"Customers with items in cart: {carts}\n"
        f"Total cart items: {total_items}\n"
        f"Customers with wishlist items: {wishlists}\n"
    )
    refs.append({"type": "overview", "label": "View Dashboard"})
    return ctx, refs


def _context_fairness(db: Session, refs: list) -> tuple[str, list]:
    total = db.query(Customer).filter(Customer.role == "customer").count()
    gender_dist = dict(
        db.query(Customer.gender, func.count(Customer.customer_id))
        .filter(Customer.role == "customer").group_by(Customer.gender).all()
    )
    age_dist = {
        "18-25": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(18, 25)).count(),
        "26-35": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(26, 35)).count(),
        "36-45": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(36, 45)).count(),
        "46-55": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(46, 55)).count(),
        "56+": db.query(Customer).filter(Customer.role == "customer", Customer.age > 55).count(),
    }

    ctx = (
        f"FAIRNESS & EQUITY:\n"
        f"Total Customers: {total:,}\n"
        f"Gender Distribution: {json.dumps(gender_dist)}\n"
        f"Age Distribution: {json.dumps(age_dist)}\n"
    )
    refs.append({"type": "fairness_center", "label": "View Fairness Observatory"})
    return ctx, refs


def _context_nba(db: Session, refs: list) -> tuple[str, list]:
    total_nba = db.query(NBADecision).count()
    action_dist = dict(
        db.query(NBADecision.recommended_action, func.count(NBADecision.decision_id))
        .group_by(NBADecision.recommended_action).all()
    )
    channel_dist = dict(
        db.query(NBADecision.channel, func.count(NBADecision.decision_id))
        .group_by(NBADecision.channel).all()
    )
    avg_conf = db.query(func.avg(NBADecision.confidence)).scalar() or 0

    ctx = (
        f"NBA ENGINE:\n"
        f"Total Recommendations: {total_nba:,}\n"
        f"Average Confidence: {avg_conf:.0%}\n"
        f"Action Distribution: {json.dumps(action_dist)}\n"
        f"Channel Distribution: {json.dumps(channel_dist)}\n"
    )
    refs.append({"type": "nba_center", "label": "View NBA Center"})
    return ctx, refs


def _context_session(db: Session, refs: list) -> tuple[str, list]:
    active = db.query(CustomerSession).filter(CustomerSession.is_active == True).count()
    total_events_24h = db.query(Event).filter(
        Event.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).count()

    ctx = (
        f"LIVE SESSIONS:\n"
        f"Active Sessions: {active}\n"
        f"Events (last 24h): {total_events_24h}\n"
    )
    refs.append({"type": "observability", "label": "View Observability"})
    return ctx, refs


def _context_general(db: Session, refs: list) -> tuple[str, list]:
    total_customers = db.query(Customer).filter(Customer.role == "customer").count()
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.status != "cancelled").scalar() or 0
    total_orders = db.query(Order).filter(Order.status != "cancelled").count()
    avg_trust = db.query(func.avg(CustomerProfile.trust_score)).scalar() or 0
    avg_happiness = db.query(func.avg(CustomerProfile.happiness_score)).scalar() or 0
    avg_churn = db.query(func.avg(CustomerProfile.churn_probability)).scalar() or 0
    high_risk = db.query(CustomerProfile).filter(CustomerProfile.churn_probability > 0.7).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()

    ctx = (
        f"PLATFORM OVERVIEW:\n"
        f"Total Customers: {total_customers:,}\n"
        f"Total Revenue: ₹{total_revenue:,.0f}\n"
        f"Total Orders: {total_orders:,}\n"
        f"Average Trust Score: {avg_trust:.1f}/100\n"
        f"Average Happiness Score: {avg_happiness:.1f}/100\n"
        f"Average Churn Risk: {avg_churn:.0%}\n"
        f"High-Risk Customers (>70%): {high_risk:,}\n"
        f"Active Campaigns: {active_campaigns}\n"
    )
    refs.append({"type": "overview", "label": "View Dashboard"})
    return ctx, refs


# ── Conversation Memory ─────────────────────────────────────────

def load_history(conversation_id: str, db: Session, limit: int = 10) -> list[dict]:
    """Load the last `limit` messages for a conversation."""
    messages = (
        db.query(CopilotConversation)
        .filter(CopilotConversation.conversation_id == conversation_id)
        .order_by(desc(CopilotConversation.created_at))
        .limit(limit)
        .all()
    )
    # Return in chronological order
    return [
        {"role": m.role, "content": m.content}
        for m in reversed(messages)
    ]


def save_message(conversation_id: str, role: str, content: str, db: Session,
                 references: list = None, context_used: str = None):
    """Save a single message to the conversation history."""
    msg = CopilotConversation(
        conversation_id=conversation_id,
        role=role,
        content=content,
        references=references or [],
        context_used=context_used,
    )
    db.add(msg)
    db.commit()


# ── Main Chat Pipeline ──────────────────────────────────────────

def chat_sync(message: str, conversation_id: str, db: Session) -> dict:
    """Non-streaming chat. Returns complete response."""
    _ensure_gemini()

    intent = detect_intent(message)
    context_str, references = get_context(intent, message, db)
    history = load_history(conversation_id, db)

    # Build conversation for Gemini
    history_text = ""
    if history:
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:500]}"
            for m in history[-8:]
        )

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- DATABASE CONTEXT ---\n{context_str}\n\n"
    )
    if history_text:
        full_prompt += f"--- CONVERSATION HISTORY ---\n{history_text}\n\n"
    full_prompt += f"--- USER QUESTION ---\n{message}"

    # Save user message
    save_message(conversation_id, "user", message, db, context_used=intent)

    try:
        from app.config import get_settings
        _settings = get_settings()
        response = _gemini_client.models.generate_content(
            model=_settings.GEMINI_MODEL,
            contents=full_prompt,
        )
        answer = response.text
    except Exception as e:
        answer = f"I encountered an issue processing your request. Please try again. (Error: {type(e).__name__})"

    # Save assistant response
    save_message(conversation_id, "assistant", answer, db, references=references, context_used=intent)

    return {
        "answer": answer,
        "references": references,
        "conversation_id": conversation_id,
        "intent": intent,
    }


async def chat_stream(message: str, conversation_id: str, db: Session) -> AsyncGenerator[str, None]:
    """Streaming chat via SSE. Yields JSON-encoded events."""
    _ensure_gemini()

    intent = detect_intent(message)
    context_str, references = get_context(intent, message, db)
    history = load_history(conversation_id, db)

    history_text = ""
    if history:
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:500]}"
            for m in history[-8:]
        )

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- DATABASE CONTEXT ---\n{context_str}\n\n"
    )
    if history_text:
        full_prompt += f"--- CONVERSATION HISTORY ---\n{history_text}\n\n"
    full_prompt += f"--- USER QUESTION ---\n{message}"

    # Save user message
    save_message(conversation_id, "user", message, db, context_used=intent)

    # Yield intent event
    yield f"data: {json.dumps({'type': 'intent', 'intent': intent})}\n\n"

    full_response = ""

    try:
        from app.config import get_settings
        _settings = get_settings()
        response = _gemini_client.models.generate_content_stream(
            model=_settings.GEMINI_MODEL,
            contents=full_prompt,
        )

        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.text})}\n\n"
    except Exception as e:
        error_msg = f"I encountered an issue processing your request. Please try again. ({type(e).__name__})"
        full_response = error_msg
        yield f"data: {json.dumps({'type': 'chunk', 'content': error_msg})}\n\n"

    # Save assistant response
    save_message(conversation_id, "assistant", full_response, db, references=references, context_used=intent)

    # Final done event with references
    yield f"data: {json.dumps({'type': 'done', 'references': references, 'conversation_id': conversation_id})}\n\n"
