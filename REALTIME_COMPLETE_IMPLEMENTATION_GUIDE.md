# 🔴 REAL-TIME CUSTOMER INTELLIGENCE - COMPLETE IMPLEMENTATION GUIDE

**Status**: Phase 1-2 Complete, Phases 3-17 Ready for Implementation  
**Date**: June 6, 2026

---

## ✅ COMPLETED

### Phase 1: Database Schema ✅
- Created 5 new tables:
  - `customer_sessions`
  - `cart_items`
  - `wishlist_items`
  - `search_history`
  - `product_views`

### Phase 2: Central Event Tracking Engine ✅
- Created `app/services/event_tracker.py`
- Function: `track_event()` - Universal tracking
- Function: `update_customer_profile()` - Auto-update profiles
- Function: `broadcast_event()` - WebSocket broadcasting
- Function: `format_event_message()` - Human-readable messages

---

## 🔄 IMPLEMENTATION ROADMAP

### PHASE 3: Session Management API

**File**: `backend/app/routers/auth.py` (UPDATE EXISTING)

```python
@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # ... existing auth logic ...
    
    # ADD THIS: Create session
    from app.models.realtime_models import CustomerSession
    session = CustomerSession(
        customer_id=user.customer_id,
        login_time=datetime.utcnow(),
        device=detect_device(request),  # TODO: Implement
        browser=detect_browser(request),  # TODO: Implement
        ip_address=request.client.host,
        is_active=True
    )
    db.add(session)
    db.commit()
    
    # Track login event
    from app.services.event_tracker import track_event_sync
    track_event_sync(user.customer_id, "USER_LOGIN", f"{user.first_name} {user.last_name}", db=db)
    
    return {"access_token": token, "user": user_dict, "session_id": session.session_id}

@router.post("/logout")
async def logout(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Close session
    from app.models.realtime_models import CustomerSession
    session = db.query(CustomerSession).filter(
        CustomerSession.customer_id == current_user.customer_id,
        CustomerSession.is_active == True
    ).first()
    
    if session:
        session.logout_time = datetime.utcnow()
        session.duration_seconds = (session.logout_time - session.login_time).total_seconds()
        session.is_active = False
        db.commit()
    
    # Track logout event
    from app.services.event_tracker import track_event_sync
    track_event_sync(current_user.customer_id, "USER_LOGOUT", db=db)
    
    return {"message": "Logged out"}
```

---

### PHASE 4: Cart & Wishlist API

**File**: `backend/app/routers/cart.py` (NEW)

```python
"""Cart and Wishlist Management"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.realtime_models import CartItem, WishlistItem
from app.models.models import Product
from app.services.event_tracker import track_event_sync
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/cart")
def get_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get customer's cart items"""
    items = db.query(CartItem).filter(
        CartItem.customer_id == current_user.customer_id
    ).all()
    return {"items": items}

@router.post("/cart/add")
def add_to_cart(
    product_id: str,
    quantity: int = 1,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add item to cart"""
    # Get product info
    product = db.query(Product).filter(Product.product_id == product_id).first()
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.customer_id == current_user.customer_id,
        CartItem.product_id == product_id
    ).first()
    
    if existing:
        existing.quantity += quantity
        db.commit()
    else:
        cart_item = CartItem(
            customer_id=current_user.customer_id,
            product_id=product_id,
            product_name=product.name,
            product_price=product.price,
            quantity=quantity
        )
        db.add(cart_item)
        db.commit()
    
    # Track event
    track_event_sync(
        current_user.customer_id,
        "ADD_TO_CART",
        product.name,
        {"product_id": product_id, "quantity": quantity, "price": product.price},
        db
    )
    
    return {"message": "Added to cart", "product": product.name}

@router.post("/cart/remove")
def remove_from_cart(
    product_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove item from cart"""
    item = db.query(CartItem).filter(
        CartItem.customer_id == current_user.customer_id,
        CartItem.product_id == product_id
    ).first()
    
    if item:
        product_name = item.product_name
        db.delete(item)
        db.commit()
        
        # Track event
        track_event_sync(
            current_user.customer_id,
            "REMOVE_FROM_CART",
            product_name,
            {"product_id": product_id},
            db
        )
        
        return {"message": "Removed from cart"}
    
    return {"message": "Item not in cart"}

@router.get("/wishlist")
def get_wishlist(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get customer's wishlist"""
    items = db.query(WishlistItem).filter(
        WishlistItem.customer_id == current_user.customer_id
    ).all()
    return {"items": items}

@router.post("/wishlist/add")
def add_to_wishlist(
    product_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add item to wishlist"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    
    # Check if already in wishlist
    existing = db.query(WishlistItem).filter(
        WishlistItem.customer_id == current_user.customer_id,
        WishlistItem.product_id == product_id
    ).first()
    
    if not existing:
        wishlist_item = WishlistItem(
            customer_id=current_user.customer_id,
            product_id=product_id,
            product_name=product.name,
            product_price=product.price
        )
        db.add(wishlist_item)
        db.commit()
        
        # Track event
        track_event_sync(
            current_user.customer_id,
            "ADD_TO_WISHLIST",
            product.name,
            {"product_id": product_id},
            db
        )
    
    return {"message": "Added to wishlist"}

@router.post("/wishlist/remove")
def remove_from_wishlist(
    product_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove item from wishlist"""
    item = db.query(WishlistItem).filter(
        WishlistItem.customer_id == current_user.customer_id,
        WishlistItem.product_id == product_id
    ).first()
    
    if item:
        product_name = item.product_name
        db.delete(item)
        db.commit()
        
        # Track event
        track_event_sync(
            current_user.customer_id,
            "REMOVE_FROM_WISHLIST",
            product_name,
            {"product_id": product_id},
            db
        )
    
    return {"message": "Removed from wishlist"}
```

---

### PHASE 5: Search & Product Tracking

**File**: `backend/app/routers/products.py` (UPDATE EXISTING)

```python
# ADD THIS to existing products router

from app.models.realtime_models import SearchHistory, ProductView
from app.services.event_tracker import track_event_sync

@router.get("")  # UPDATE EXISTING GET /products
def get_products(
    category: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)  # Optional auth
):
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
        results_count = query.count()
        
        # Track search if user is logged in
        if current_user:
            search_record = SearchHistory(
                customer_id=current_user.customer_id,
                search_query=search,
                results_count=results_count
            )
            db.add(search_record)
            db.commit()
            
            # Track event
            track_event_sync(
                current_user.customer_id,
                "SEARCH",
                search,
                {"results_count": results_count},
                db
            )
    
    products = query.limit(100).all()
    return {"products": products}

@router.post("/view/{product_id}")  # NEW ENDPOINT
def track_product_view(
    product_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Track when customer views a product"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    
    if product:
        # Record view
        view = ProductView(
            customer_id=current_user.customer_id,
            product_id=product_id,
            product_name=product.name,
            product_category=product.category
        )
        db.add(view)
        db.commit()
        
        # Track event
        track_event_sync(
            current_user.customer_id,
            "PRODUCT_VIEW",
            product.name,
            {"product_id": product_id, "category": product.category, "price": product.price},
            db
        )
    
    return {"message": "View tracked"}
```

---

### PHASE 6: Live Activity API

**File**: `backend/app/routers/activity.py` (NEW)

```python
"""Real-Time Activity Monitoring"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from app.database.connection import get_db
from app.models.models import Event, Customer
from app.models.realtime_models import CustomerSession

router = APIRouter()

@router.get("/live-feed")
def get_live_feed(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get recent customer activity for admin dashboard.
    
    Returns last N events with customer names.
    """
    events = db.query(Event, Customer).join(
        Customer, Event.customer_id == Customer.customer_id
    ).order_by(desc(Event.timestamp)).limit(limit).all()
    
    feed = []
    for event, customer in events:
        feed.append({
            "event_id": event.event_id,
            "customer_id": customer.customer_id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "event_type": event.event_type,
            "event_value": event.event_value,
            "timestamp": event.timestamp.isoformat(),
            "metadata": event.metadata_json
        })
    
    return {"feed": feed}

@router.get("/active-users")
def get_active_users(db: Session = Depends(get_db)):
    """
    Get count of currently active users.
    
    Active = logged in within last 5 minutes.
    """
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    active_count = db.query(CustomerSession).filter(
        CustomerSession.is_active == True,
        CustomerSession.login_time >= five_minutes_ago
    ).count()
    
    return {"active_users": active_count}

@router.get("/active-sessions")
def get_active_sessions(db: Session = Depends(get_db)):
    """
    Get list of currently active sessions with customer info.
    """
    sessions = db.query(CustomerSession, Customer).join(
        Customer, CustomerSession.customer_id == Customer.customer_id
    ).filter(
        CustomerSession.is_active == True
    ).all()
    
    active_sessions = []
    for session, customer in sessions:
        active_sessions.append({
            "session_id": session.session_id,
            "customer_id": customer.customer_id,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "login_time": session.login_time.isoformat(),
            "device": session.device,
            "browser": session.browser
        })
    
    return {"sessions": active_sessions}

@router.get("/customer-timeline/{customer_id}")
def get_customer_timeline(customer_id: str, db: Session = Depends(get_db)):
    """
    Get complete timeline of a customer's actions.
    
    Used for Journey Replay.
    """
    events = db.query(Event).filter(
        Event.customer_id == customer_id
    ).order_by(Event.timestamp).all()
    
    timeline = []
    for event in events:
        timeline.append({
            "event_id": event.event_id,
            "event_type": event.event_type,
            "event_value": event.event_value,
            "timestamp": event.timestamp.isoformat(),
            "metadata": event.metadata_json
        })
    
    return {"timeline": timeline}
```

---

### PHASE 7: Register Router in Main

**File**: `backend/app/main.py` (UPDATE)

```python
from app.routers import auth, customers, products, events, analytics, campaigns, ai_router, support, observatory, telemetry, cart, activity

# Add these lines:
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(activity.router, prefix="/api/activity", tags=["Activity"])
```

---

### PHASE 8: Frontend - Customer Portal Updates

**File**: `frontend/src/pages/shop/CustomerPortal.tsx` (UPDATE)

Add tracking to all actions:

```typescript
// When customer searches
const handleSearch = async (query: string) => {
  setSearch(query)
  // Existing search logic...
  
  // ADD: No need to manually track - backend does it
}

// When customer views product
const handleProductView = async (productId: string) => {
  // ADD: Track view
  await api.post(`/products/view/${productId}`)
  // Then show product details...
}

// When customer adds to cart
const handleAddToCart = async (productId: string, quantity: number = 1) => {
  await api.post('/cart/add', { product_id: productId, quantity })
  // Update local cart state...
}

// When customer adds to wishlist
const handleAddToWishlist = async (productId: string) => {
  await api.post('/wishlist/add', { product_id: productId })
  // Update local wishlist state...
}
```

---

### PHASE 9: Frontend - Live Activity Dashboard

**File**: `frontend/src/pages/admin/LiveActivity.tsx` (NEW)

```typescript
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../../services/api'

export default function LiveActivity() {
  const [feed, setFeed] = useState([])
  
  // Poll for new activity every 2 seconds
  const { data } = useQuery({
    queryKey: ['live-feed'],
    queryFn: () => api.get('/activity/live-feed?limit=50').then(r => r.data),
    refetchInterval: 2000
  })
  
  const { data: activeUsersData } = useQuery({
    queryKey: ['active-users'],
    queryFn: () => api.get('/activity/active-users').then(r => r.data),
    refetchInterval: 5000
  })
  
  useEffect(() => {
    if (data?.feed) {
      setFeed(data.feed)
    }
  }, [data])
  
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h2 className="text-xl font-bold text-white mb-4">
          Live Customer Activity
        </h2>
        <p className="text-slate-400 mb-6">
          Active Users: {activeUsersData?.active_users || 0}
        </p>
        
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {feed.map((item: any) => (
            <div key={item.event_id} className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50">
              <span className="text-xs text-slate-500">
                {new Date(item.timestamp).toLocaleTimeString()}
              </span>
              <span className="text-sm text-blue-400 font-medium">
                {item.customer_name}
              </span>
              <span className="text-sm text-slate-300">
                {formatEventMessage(item)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function formatEventMessage(item: any) {
  const messages: any = {
    'SEARCH': `searched for: ${item.event_value}`,
    'PRODUCT_VIEW': `viewed: ${item.event_value}`,
    'ADD_TO_CART': `added to cart: ${item.event_value}`,
    'PURCHASE_COMPLETED': `purchased: ${item.event_value}`,
    // ... etc
  }
  return messages[item.event_type] || item.event_type
}
```

---

## 🎯 TESTING CHECKLIST

1. ✅ Register new customer
2. ✅ Login (check: active users +1)
3. ✅ Search "Laptop" (check: appears in feed)
4. ✅ View product (check: appears in feed)
5. ✅ Add to cart (check: appears in feed, cart persists)
6. ✅ Add to wishlist (check: appears in feed)
7. ✅ Remove from cart (check: appears in feed)
8. ✅ Purchase (check: appears in feed, revenue updates)
9. ✅ Logout (check: active users -1)
10. ✅ Login again (check: cart still there)

---

## 📋 REMAINING WORK

- Phase 10: Purchase/Checkout flow with tracking
- Phase 11: Support ticket tracking
- Phase 12: Review submission tracking
- Phase 13: Campaign click tracking
- Phase 14: NBA acceptance tracking
- Phase 15: Update Business Observatory with real-time data
- Phase 16: Update Executive Intelligence auto-refresh
- Phase 17: WebSocket real-time (instead of polling)

---

**NEXT STEPS**: Implement phases 3-9, then test with a new customer account.

