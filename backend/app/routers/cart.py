"""
Shopping Cart, Wishlist & Checkout API
=========================================

Complete ecommerce flow with real-time broadcasting:
- Add/remove/update cart items → broadcast to admin
- Add/remove wishlist items → broadcast to admin  
- Checkout & place order → broadcast to admin
- All persisted to database
- All create events
- All trigger AI intelligence updates
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.realtime_models import CartItem, WishlistItem
from app.models.models import Product, Order, OrderItem, Event, Customer, CustomerProfile
from app.utils.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter()


# ── Request Models ─────────────────────────────────────────────
class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = 1


class UpdateCartRequest(BaseModel):
    cart_item_id: str
    quantity: int


class CheckoutRequest(BaseModel):
    shipping_address: Optional[str] = None
    payment_method: str = "card"


class WishlistRequest(BaseModel):
    product_id: str


class ReviewRequest(BaseModel):
    product_id: str
    rating: int
    comment: str = ""


class RefundRequest(BaseModel):
    order_id: str
    reason: str = ""


# ── Get Cart ───────────────────────────────────────────────────
@router.get("/")
def get_cart(db: Session = Depends(get_db), current_user: Customer = Depends(get_current_user)):
    cart_items = db.query(CartItem, Product).join(
        Product, CartItem.product_id == Product.product_id
    ).filter(
        CartItem.customer_id == current_user.customer_id
    ).all()
    
    items = []
    subtotal = 0.0
    
    for cart_item, product in cart_items:
        item_total = product.price * cart_item.quantity
        subtotal += item_total
        
        items.append({
            "cart_item_id": cart_item.cart_item_id,
            "product_id": product.product_id,
            "product_name": product.name,
            "product_image": product.image_url,
            "product_price": product.price,
            "original_price": product.original_price,
            "quantity": cart_item.quantity,
            "item_total": round(item_total, 2),
            "category": product.category,
            "brand": product.brand,
            "stock": product.stock
        })
    
    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "total": round(subtotal, 2),
        "item_count": len(items)
    }


# ── Add to Cart ────────────────────────────────────────────────
@router.post("/add")
async def add_to_cart(
    request: AddToCartRequest,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.product_id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < request.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.customer_id == current_user.customer_id,
        CartItem.product_id == request.product_id
    ).first()
    
    if existing:
        existing.quantity += request.quantity
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        message = f"Updated quantity to {existing.quantity}"
    else:
        cart_item = CartItem(
            customer_id=current_user.customer_id,
            product_id=request.product_id,
            product_name=product.name,
            product_price=product.price,
            quantity=request.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        message = "Added to cart"
    
    # Create ADD_TO_CART event
    event = Event(
        customer_id=current_user.customer_id,
        event_type="ADD_TO_CART",
        event_value=product.name,
        metadata_json={
            "product_id": request.product_id,
            "quantity": request.quantity,
            "price": product.price,
            "category": product.category,
            "brand": product.brand
        },
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    # Get cart total for notification
    cart_total = db.query(func.sum(CartItem.product_price * CartItem.quantity)).filter(
        CartItem.customer_id == current_user.customer_id
    ).scalar() or 0
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    # Broadcast to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "ADD_TO_CART",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": product.name,
        "message": f"🛒 {customer_name} added {product.name} to cart",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "product_id": request.product_id,
            "product_name": product.name,
            "price": product.price,
            "quantity": request.quantity,
            "category": product.category,
            "cart_value": round(cart_total, 2)
        }
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Cart add error: {e}")
    
    return {
        "message": message,
        "product_name": product.name,
        "quantity": request.quantity
    }


# ── Update Cart Item Quantity ──────────────────────────────────
@router.put("/update")
async def update_cart_item(
    request: UpdateCartRequest,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.cart_item_id == request.cart_item_id,
        CartItem.customer_id == current_user.customer_id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
    if product and product.stock < request.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart_item.quantity = request.quantity
    cart_item.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Cart updated", "quantity": request.quantity}


# ── Remove from Cart ───────────────────────────────────────────
@router.delete("/remove/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: str,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.cart_item_id == cart_item_id,
        CartItem.customer_id == current_user.customer_id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    product_name = cart_item.product_name
    product_id = cart_item.product_id
    
    db.delete(cart_item)
    
    # Track event
    event = Event(
        customer_id=current_user.customer_id,
        event_type="REMOVE_FROM_CART",
        event_value=product_name,
        metadata_json={"product_id": product_id},
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    # Broadcast to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "REMOVE_FROM_CART",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": product_name,
        "message": f"🛒 {customer_name} removed {product_name} from cart",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"product_id": product_id, "product_name": product_name}
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Cart remove error: {e}")
    
    return {"message": "Removed from cart", "product_name": product_name}


# ── Clear Cart ─────────────────────────────────────────────────
@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    db.query(CartItem).filter(
        CartItem.customer_id == current_user.customer_id
    ).delete()
    db.commit()
    return {"message": "Cart cleared"}


# ── Checkout (Place Order) ─────────────────────────────────────
@router.post("/checkout")
async def checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    # Get cart items
    cart_items = db.query(CartItem, Product).join(
        Product, CartItem.product_id == Product.product_id
    ).filter(
        CartItem.customer_id == current_user.customer_id
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_amount = 0.0
    order_items_data = []
    
    for cart_item, product in cart_items:
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}. Only {product.stock} available."
            )
        
        item_total = product.price * cart_item.quantity
        total_amount += item_total
        
        order_items_data.append({
            "product_id": product.product_id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "price": product.price,
            "category": product.category,
        })
    
    # Create CHECKOUT_STARTED event
    checkout_start_event = Event(
        customer_id=current_user.customer_id,
        event_type="CHECKOUT_STARTED",
        event_value=f"₹{round(total_amount, 2):,.0f}",
        metadata_json={"items_count": len(order_items_data), "total": round(total_amount, 2)},
        timestamp=datetime.utcnow()
    )
    db.add(checkout_start_event)
    
    # Create order
    order = Order(
        customer_id=current_user.customer_id,
        total_amount=round(total_amount, 2),
        status="confirmed",
        payment_method=request.payment_method,
        shipping_address=request.shipping_address or f"{current_user.city or 'India'}",
        order_date=datetime.utcnow()
    )
    db.add(order)
    db.flush()
    
    # Create order items and update inventory
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_item)
        
        product = db.query(Product).filter(Product.product_id == item_data["product_id"]).first()
        if product:
            product.stock = max(0, product.stock - item_data["quantity"])
    
    # Clear cart
    db.query(CartItem).filter(
        CartItem.customer_id == current_user.customer_id
    ).delete()
    
    # Create PURCHASE_COMPLETED event
    purchase_event = Event(
        customer_id=current_user.customer_id,
        event_type="PURCHASE_COMPLETED",
        event_value=f"₹{round(total_amount, 2):,.0f}",
        metadata_json={
            "order_id": order.order_id,
            "total_amount": round(total_amount, 2),
            "items_count": len(order_items_data),
            "products": [item["product_name"] for item in order_items_data],
            "payment_method": request.payment_method,
        },
        timestamp=datetime.utcnow()
    )
    db.add(purchase_event)
    
    db.commit()
    db.refresh(order)
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    # Broadcast CHECKOUT to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "CHECKOUT_STARTED",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": f"₹{round(total_amount, 2):,.0f}",
        "message": f"🧾 {customer_name} started checkout",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"total": round(total_amount, 2), "items": len(order_items_data)}
    }, room="admin")
    
    # Broadcast PURCHASE_COMPLETED to admin
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "PURCHASE_COMPLETED",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": f"₹{round(total_amount, 2):,.0f}",
        "message": f"💰 {customer_name} completed purchase — ₹{round(total_amount, 2):,.0f}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "order_id": order.order_id,
            "total_amount": round(total_amount, 2),
            "items_count": len(order_items_data),
            "products": [item["product_name"] for item in order_items_data],
        }
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Checkout error: {e}")
    
    return {
        "message": "Order placed successfully",
        "order_id": order.order_id,
        "total_amount": round(total_amount, 2),
        "items_count": len(order_items_data),
        "status": order.status
    }


# ══════════════════════════════════════════════════════════════
# WISHLIST ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.get("/wishlist")
def get_wishlist(db: Session = Depends(get_db), current_user: Customer = Depends(get_current_user)):
    """Get customer's wishlist with product details."""
    items = db.query(WishlistItem, Product).join(
        Product, WishlistItem.product_id == Product.product_id
    ).filter(
        WishlistItem.customer_id == current_user.customer_id
    ).all()
    
    return {
        "items": [
            {
                "wishlist_item_id": wi.wishlist_item_id,
                "product_id": p.product_id,
                "product_name": p.name,
                "product_image": p.image_url,
                "product_price": p.price,
                "original_price": p.original_price,
                "category": p.category,
                "brand": p.brand,
                "rating": p.rating,
                "stock": p.stock,
                "added_at": wi.added_at.isoformat() if wi.added_at else None,
            }
            for wi, p in items
        ],
        "count": len(items)
    }


@router.post("/wishlist/add")
async def add_to_wishlist(
    request: WishlistRequest,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Add product to wishlist."""
    product = db.query(Product).filter(Product.product_id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already in wishlist
    existing = db.query(WishlistItem).filter(
        WishlistItem.customer_id == current_user.customer_id,
        WishlistItem.product_id == request.product_id
    ).first()
    
    if existing:
        return {"message": "Already in wishlist", "product_name": product.name}
    
    wishlist_item = WishlistItem(
        customer_id=current_user.customer_id,
        product_id=request.product_id,
        product_name=product.name,
        product_price=product.price,
    )
    db.add(wishlist_item)
    
    # Create event
    event = Event(
        customer_id=current_user.customer_id,
        event_type="ADD_TO_WISHLIST",
        event_value=product.name,
        metadata_json={
            "product_id": request.product_id,
            "price": product.price,
            "category": product.category
        },
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    # Broadcast
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "ADD_TO_WISHLIST",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": product.name,
        "message": f"❤️ {customer_name} wishlisted {product.name}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"product_id": request.product_id, "product_name": product.name, "price": product.price}
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Wishlist add error: {e}")
    
    return {"message": "Added to wishlist", "product_name": product.name}


@router.delete("/wishlist/remove/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Remove product from wishlist."""
    item = db.query(WishlistItem).filter(
        WishlistItem.customer_id == current_user.customer_id,
        WishlistItem.product_id == product_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    
    product_name = item.product_name
    db.delete(item)
    
    event = Event(
        customer_id=current_user.customer_id,
        event_type="REMOVE_FROM_WISHLIST",
        event_value=product_name,
        metadata_json={"product_id": product_id},
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "REMOVE_FROM_WISHLIST",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": product_name,
        "message": f"💔 {customer_name} removed {product_name} from wishlist",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"product_id": product_id}
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Wishlist remove error: {e}")
    
    return {"message": "Removed from wishlist", "product_name": product_name}


# ══════════════════════════════════════════════════════════════
# REVIEW & REFUND ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.post("/review")
async def submit_review(
    request: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Submit a product review."""
    product = db.query(Product).filter(Product.product_id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product rating (simple running average)
    if product.review_count and product.rating:
        total_rating = product.rating * product.review_count + request.rating
        product.review_count += 1
        product.rating = round(total_rating / product.review_count, 1)
    else:
        product.review_count = 1
        product.rating = request.rating
    
    # Create event
    event = Event(
        customer_id=current_user.customer_id,
        event_type="REVIEW_SUBMITTED",
        event_value=f"{request.rating}★ for {product.name}",
        metadata_json={
            "product_id": request.product_id,
            "rating": request.rating,
            "comment": request.comment,
            "product_name": product.name
        },
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "REVIEW_SUBMITTED",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": f"{request.rating}★ {product.name}",
        "message": f"⭐ {customer_name} reviewed {product.name} — {request.rating}★",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"product_name": product.name, "rating": request.rating}
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Review error: {e}")
    
    return {"message": "Review submitted", "rating": request.rating}


@router.post("/refund")
async def request_refund(
    request: RefundRequest,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Request a refund for an order."""
    from app.models.models import Order
    
    order = db.query(Order).filter(
        Order.order_id == request.order_id,
        Order.customer_id == current_user.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "refund_requested"
    
    # Create event
    event = Event(
        customer_id=current_user.customer_id,
        event_type="REFUND_REQUESTED",
        event_value=f"Order {request.order_id[:8]} — ₹{order.total_amount:,.0f}",
        metadata_json={
            "order_id": request.order_id,
            "amount": order.total_amount,
            "reason": request.reason
        },
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    
    customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    await manager.broadcast({
        "type": "customer_activity",
        "event_type": "REFUND_REQUESTED",
        "customer_id": current_user.customer_id,
        "customer_name": customer_name,
        "event_value": f"₹{order.total_amount:,.0f}",
        "message": f"↩️ {customer_name} requested refund — ₹{order.total_amount:,.0f}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"order_id": request.order_id, "amount": order.total_amount, "reason": request.reason}
    }, room="admin")
    
    # Trigger Intelligence Orchestrator
    try:
        from app.services.realtime_ai import update_customer_intelligence
        await update_customer_intelligence(current_user.customer_id, db)
    except Exception as e:
        print(f"[Intelligence] Refund error: {e}")
    
    return {"message": "Refund requested", "order_id": request.order_id}


# ══════════════════════════════════════════════════════════════
# ORDER HISTORY
# ══════════════════════════════════════════════════════════════

@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.customer_id == current_user.customer_id
    ).order_by(Order.order_date.desc()).all()
    
    order_list = []
    for order in orders:
        items = db.query(OrderItem, Product).join(
            Product, OrderItem.product_id == Product.product_id
        ).filter(
            OrderItem.order_id == order.order_id
        ).all()
        
        order_items = []
        for order_item, product in items:
            order_items.append({
                "product_id": product.product_id,
                "product_name": product.name,
                "product_image": product.image_url,
                "quantity": order_item.quantity,
                "price": order_item.price,
                "subtotal": round(order_item.quantity * order_item.price, 2)
            })
        
        order_list.append({
            "order_id": order.order_id,
            "order_date": order.order_date.isoformat(),
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "shipping_address": order.shipping_address,
            "items": order_items,
            "items_count": len(order_items)
        })
    
    return {"orders": order_list}


@router.get("/orders/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.customer_id == current_user.customer_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = db.query(OrderItem, Product).join(
        Product, OrderItem.product_id == Product.product_id
    ).filter(
        OrderItem.order_id == order.order_id
    ).all()
    
    order_items = []
    for order_item, product in items:
        order_items.append({
            "product_id": product.product_id,
            "product_name": product.name,
            "product_image": product.image_url,
            "category": product.category,
            "brand": product.brand,
            "quantity": order_item.quantity,
            "price": order_item.price,
            "subtotal": round(order_item.quantity * order_item.price, 2)
        })
    
    return {
        "order_id": order.order_id,
        "order_date": order.order_date.isoformat(),
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_method": order.payment_method,
        "shipping_address": order.shipping_address,
        "items": order_items,
        "items_count": len(order_items)
    }
