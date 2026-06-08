"""Products Router — Browse, Search, Filter, Detail with real-time tracking.

Every product interaction:
- Product views → event + broadcast
- Search → search_history table + event + broadcast
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.models import Product, Event, Customer
from app.models.realtime_models import SearchHistory, ProductView
from app.routers.auth import get_current_user_optional
from app.utils.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter()


@router.get("")
def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = "created_at",
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    if search:
        q = q.filter(or_(
            Product.name.ilike(f"%{search}%"),
            Product.description.ilike(f"%{search}%"),
            Product.brand.ilike(f"%{search}%"),
        ))
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    
    total = q.count()
    products = q.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "products": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "price": p.price,
                "original_price": p.original_price,
                "rating": p.rating,
                "review_count": p.review_count,
                "image_url": p.image_url,
                "brand": p.brand,
                "stock": p.stock,
            }
            for p in products
        ],
    }


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Product.category).distinct().all()
    return [c[0] for c in cats]


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Customer] = Depends(get_current_user_optional)
):
    p = db.query(Product).filter(Product.product_id == product_id).first()
    if not p:
        return {"error": "Product not found"}
    
    # Track PRODUCT_VIEW event if user is logged in
    if current_user:
        # Create event
        event = Event(
            customer_id=current_user.customer_id,
            event_type="PRODUCT_VIEW",
            event_value=p.name,
            metadata_json={
                "product_id": p.product_id,
                "category": p.category,
                "price": p.price,
                "brand": p.brand
            },
            timestamp=datetime.utcnow()
        )
        db.add(event)
        
        # Create product view record
        pv = ProductView(
            customer_id=current_user.customer_id,
            product_id=p.product_id,
            product_name=p.name,
            product_category=p.category,
            timestamp=datetime.utcnow()
        )
        db.add(pv)
        db.commit()
        
        customer_name = f"{current_user.first_name} {current_user.last_name}"
        
        # Broadcast to admin
        await manager.broadcast({
            "type": "customer_activity",
            "event_type": "PRODUCT_VIEW",
            "customer_id": current_user.customer_id,
            "customer_name": customer_name,
            "event_value": p.name,
            "message": f"👁️ {customer_name} viewed {p.name}",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "product_id": p.product_id,
                "product_name": p.name,
                "category": p.category,
                "price": p.price,
                "brand": p.brand
            }
        }, room="admin")
        
        # Trigger Intelligence Orchestrator
        try:
            from app.services.realtime_ai import update_customer_intelligence
            await update_customer_intelligence(current_user.customer_id, db)
        except Exception as e:
            print(f"[Intelligence] Product view error: {e}")
    
    return {
        "product_id": p.product_id,
        "name": p.name,
        "category": p.category,
        "description": p.description,
        "price": p.price,
        "original_price": p.original_price,
        "rating": p.rating,
        "review_count": p.review_count,
        "image_url": p.image_url,
        "brand": p.brand,
        "stock": p.stock,
        "tags": p.tags,
    }


@router.post("/search")
async def track_search(
    query: str,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Track a search query with persistence and broadcast."""
    
    # Count results
    results = db.query(Product).filter(or_(
        Product.name.ilike(f"%{query}%"),
        Product.description.ilike(f"%{query}%"),
        Product.brand.ilike(f"%{query}%"),
    )).count()
    
    # Save to search_history
    search = SearchHistory(
        customer_id=current_user.customer_id,
        search_query=query,
        results_count=results,
        timestamp=datetime.utcnow()
    )
    db.add(search)
    
    # Create SEARCH event
    event = Event(
        customer_id=current_user.customer_id,
        event_type="SEARCH",
        event_value=query,
        metadata_json={"results_count": results},
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    # Broadcast to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "SEARCH",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": query,
        "message": f"🔍 {customer_name} searched for: {query}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"query": query, "results_count": results}
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Search error: {e}")
    
    return {"query": query, "results_count": results}
