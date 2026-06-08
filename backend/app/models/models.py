"""All SQLAlchemy models for OmniPulse AI — 14 tables."""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


def gen_id():
    return str(uuid.uuid4())


# ── TABLE 1: CUSTOMERS ──────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String, primary_key=True, default=gen_id)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    gender = Column(String(20))
    age = Column(Integer)
    city = Column(String(100))
    country = Column(String(100), default="India")
    registration_date = Column(DateTime, default=datetime.utcnow)
    preferred_language = Column(String(20), default="en")
    status = Column(String(20), default="active")
    role = Column(String(20), default="customer")  # customer | admin | marketer
    avatar_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="customer", lazy="dynamic")
    events = relationship("Event", back_populates="customer", lazy="dynamic")
    tickets = relationship("SupportTicket", back_populates="customer", lazy="dynamic")
    profile = relationship("CustomerProfile", back_populates="customer", uselist=False)
    nba_decisions = relationship("NBADecision", back_populates="customer", lazy="dynamic")
    journeys = relationship("Journey", back_populates="customer", lazy="dynamic")
    messages = relationship("Message", back_populates="customer", lazy="dynamic")


# ── TABLE 2: PRODUCTS ───────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True, default=gen_id)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    stock = Column(Integer, default=100)
    rating = Column(Float, default=4.0)
    review_count = Column(Integer, default=0)
    image_url = Column(String(500))
    brand = Column(String(100))
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order_items = relationship("OrderItem", back_populates="product")


# ── TABLE 3: ORDERS ─────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(30), default="pending")  # pending | confirmed | shipped | delivered | cancelled
    payment_method = Column(String(50), default="card")
    shipping_address = Column(Text)
    order_date = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all,delete-orphan")


# ── TABLE 4: ORDER_ITEMS ────────────────────────────────────────
class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_item_id = Column(String, primary_key=True, default=gen_id)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ── TABLE 5: EVENTS ─────────────────────────────────────────────
class Event(Base):
    __tablename__ = "events"
    
    event_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_value = Column(String(255))
    metadata_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    customer = relationship("Customer", back_populates="events")


# ── TABLE 6: SUPPORT_TICKETS ────────────────────────────────────
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    ticket_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    sentiment = Column(String(20))  # happy | neutral | frustrated | angry | excited
    sentiment_score = Column(Float)
    status = Column(String(20), default="open")  # open | in_progress | resolved | closed
    priority = Column(String(20), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    customer = relationship("Customer", back_populates="tickets")


# ── TABLE 7: CAMPAIGNS ──────────────────────────────────────────
class Campaign(Base):
    __tablename__ = "campaigns"
    
    campaign_id = Column(String, primary_key=True, default=gen_id)
    campaign_name = Column(String(255), nullable=False)
    description = Column(Text)
    audience = Column(JSON, default=dict)
    channel = Column(String(50))  # email | sms | push | offer
    offer = Column(String(255))
    discount_pct = Column(Float, default=0)
    status = Column(String(20), default="draft")  # draft | active | paused | completed
    variant = Column(String(10))  # A | B | C
    budget = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    responses = relationship("CampaignResponse", back_populates="campaign", lazy="dynamic")


# ── TABLE 8: CAMPAIGN_RESPONSES ──────────────────────────────────
class CampaignResponse(Base):
    __tablename__ = "campaign_responses"
    
    response_id = Column(String, primary_key=True, default=gen_id)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)
    revenue = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    campaign = relationship("Campaign", back_populates="responses")


# ── TABLE 9: CUSTOMER_PROFILES ───────────────────────────────────
class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    
    customer_id = Column(String, ForeignKey("customers.customer_id"), primary_key=True)
    customer_name = Column(String(200))                # cached full name
    risk_score = Column(Float, default=0.0)            # 0–100
    trust_score = Column(Float, default=50.0)          # 0–100
    happiness_score = Column(Float, default=50.0)      # 0–100
    clv = Column(Float, default=0.0)                   # lifetime value in INR
    predicted_clv = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)         # actual revenue from orders
    churn_probability = Column(Float, default=0.0)     # 0–1
    persona = Column(String(50))                       # Weekend Shopper, Premium Buyer, etc.
    emotion = Column(String(20), default="neutral")
    segment = Column(String(50))                       # high_value, medium, low, at_risk
    journey_stage = Column(String(50))                 # active, loyal, at_risk, consideration, inactive
    engagement_score = Column(Float, default=50.0)
    competitive_risk = Column(Float, default=0.0)
    recency_days = Column(Integer, default=0)
    frequency = Column(Integer, default=0)
    monetary = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="profile")


# ── TABLE 10: NBA_DECISIONS ─────────────────────────────────────
class NBADecision(Base):
    __tablename__ = "nba_decisions"
    
    decision_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    recommended_action = Column(String(255), nullable=False)
    channel = Column(String(50))
    offer = Column(String(255))
    tone = Column(String(50))
    timing = Column(String(50))
    message = Column(Text)
    confidence = Column(Float, default=0.0)
    reason = Column(Text)
    inference_tier = Column(String(20))  # rules | ml | gemini
    signals_used = Column(JSON, default=list)
    expected_outcome = Column(JSON, default=dict)
    status = Column(String(20), default="pending")  # pending | delivered | accepted | ignored
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="nba_decisions")


# ── TABLE 11: JOURNEYS ──────────────────────────────────────────
class Journey(Base):
    __tablename__ = "journeys"
    
    journey_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    journey_type = Column(String(50))  # churn_rescue | onboarding | re_engagement | loyalty
    journey_stage = Column(String(50))
    journey_status = Column(String(20), default="active")  # active | completed | cancelled
    steps = Column(JSON, default=list)
    current_step = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    customer = relationship("Customer", back_populates="journeys")


# ── TABLE 12: MESSAGES ──────────────────────────────────────────
class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    channel = Column(String(30))  # email | sms | push | in_app
    subject = Column(String(255))
    content = Column(Text)
    tone = Column(String(30))
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="messages")


# ── TABLE 13: DIGITAL_TWIN_RESULTS ──────────────────────────────
class DigitalTwinResult(Base):
    __tablename__ = "digital_twin_results"
    
    simulation_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    scenario = Column(String(50))  # no_action | intervention
    prediction = Column(JSON, default=dict)
    predicted_revenue = Column(Float, default=0)
    predicted_retention = Column(Float, default=0)
    predicted_churn = Column(Float, default=0)
    intervention_type = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)


# ── TABLE 14: EXECUTIVE_SUMMARIES ────────────────────────────────
class ExecutiveSummary(Base):
    __tablename__ = "executive_summaries"
    
    summary_id = Column(String, primary_key=True, default=gen_id)
    summary_text = Column(Text, nullable=False)
    metrics = Column(JSON, default=dict)
    highlights = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    generated_at = Column(DateTime, default=datetime.utcnow)


# ── TABLE 15: COPILOT_CONVERSATIONS ──────────────────────────────
class CopilotConversation(Base):
    __tablename__ = "copilot_conversations"
    
    id = Column(String, primary_key=True, default=gen_id)
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String(20), nullable=False)        # "user" | "assistant"
    content = Column(Text, nullable=False)
    references = Column(JSON, default=list)
    context_used = Column(String(50))                 # intent type that triggered the query
    created_at = Column(DateTime, default=datetime.utcnow)
