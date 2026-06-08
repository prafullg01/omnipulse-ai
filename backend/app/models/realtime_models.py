"""
Real-Time Activity Tracking Models
====================================

Additional models for real-time customer activity tracking:
- Customer Sessions (login/logout tracking)
- Cart Items (persistent cart)
- Wishlist Items (persistent wishlist)
- Search History (search tracking)
- Product Views (view tracking)
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


def gen_id():
    return str(uuid.uuid4())


# ── CUSTOMER SESSIONS ──────────────────────────────────────────
class CustomerSession(Base):
    """
    Tracks customer login/logout sessions.
    
    Purpose:
    - Know who is currently active
    - Track session duration
    - Track device/browser info
    - Calculate active users in real-time
    """
    __tablename__ = "customer_sessions"
    
    session_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    logout_time = Column(DateTime)
    duration_seconds = Column(Integer)  # Calculated on logout
    device = Column(String(100))  # mobile, desktop, tablet
    browser = Column(String(100))  # chrome, firefox, safari
    ip_address = Column(String(50))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── CART ITEMS ─────────────────────────────────────────────────
class CartItem(Base):
    """
    Persistent shopping cart.
    
    Purpose:
    - Track what customers add to cart
    - Persist cart across sessions
    - Calculate cart abandonment
    - Track cart value
    """
    __tablename__ = "cart_items"
    
    cart_item_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    product_name = Column(String(255))  # Denormalized for quick display
    product_price = Column(Float)  # Snapshot at time of addition
    quantity = Column(Integer, default=1, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── WISHLIST ITEMS ─────────────────────────────────────────────
class WishlistItem(Base):
    """
    Persistent wishlist.
    
    Purpose:
    - Track customer interests
    - Generate recommendations
    - Send wishlist reminders
    - Track conversion from wishlist to cart
    """
    __tablename__ = "wishlist_items"
    
    wishlist_item_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    product_name = Column(String(255))  # Denormalized
    product_price = Column(Float)  # Snapshot
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Track if wishlist item converted to purchase
    purchased = Column(Boolean, default=False)
    purchased_at = Column(DateTime)


# ── SEARCH HISTORY ─────────────────────────────────────────────
class SearchHistory(Base):
    """
    Customer search tracking.
    
    Purpose:
    - Understand what customers are looking for
    - Improve search relevance
    - Generate search-based recommendations
    - Track popular searches
    """
    __tablename__ = "search_history"
    
    search_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    search_query = Column(String(255), nullable=False, index=True)
    results_count = Column(Integer, default=0)
    clicked_product_id = Column(String, ForeignKey("products.product_id"))  # Which result they clicked
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


# ── PRODUCT VIEWS ──────────────────────────────────────────────
class ProductView(Base):
    """
    Track which products customers view.
    
    Purpose:
    - Recently viewed products
    - Product popularity tracking
    - Generate view-based recommendations
    - Calculate view-to-purchase conversion
    """
    __tablename__ = "product_views"
    
    view_id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False, index=True)
    product_name = Column(String(255))  # Denormalized
    product_category = Column(String(100))  # Denormalized
    view_duration_seconds = Column(Integer)  # How long they stayed on page
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Track conversion
    added_to_cart = Column(Boolean, default=False)
    purchased = Column(Boolean, default=False)
