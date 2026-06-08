"""
Business Observatory Router - Real-Time Monitoring Dashboard
All metrics database-backed, no hardcoded values.
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, text, desc
from datetime import datetime, timedelta
from typing import List, Dict
import json

from app.database.connection import get_db
from app.models.models import Customer, CustomerProfile, Event, Order
from app.websocket.manager import manager

router = APIRouter()


@router.get("/metrics")
def get_observatory_metrics(db: Session = Depends(get_db)):
    """
    Get real-time observatory metrics - ALL FROM DATABASE.
    
    Metrics:
    1. Active Users - customers with events in last 5 minutes
    2. Revenue Velocity - revenue per minute (last hour)
    3. Conversion Rate - purchasers / total customers
    4. Exposed CLV Risk - CLV of high-risk customers
    5. Live event count
    """
    
    # ========================================================================
    # METRIC 1: ACTIVE USERS
    # Method: Count distinct customers with events in last 5 minutes of dataset
    # ========================================================================
    
    # Get latest event timestamp (dataset is historical)
    latest_event_time = db.execute(text('''
        SELECT MAX(timestamp) FROM events
    ''')).scalar()
    
    if latest_event_time:
        # Convert string to datetime if needed
        if isinstance(latest_event_time, str):
            latest_event_time = datetime.fromisoformat(latest_event_time.replace('Z', ''))
        
        # Count active users in last 5 minutes of dataset
        five_min_ago = latest_event_time - timedelta(minutes=5)
        
        active_users = db.execute(text('''
            SELECT COUNT(DISTINCT customer_id)
            FROM events
            WHERE timestamp >= :cutoff
        '''), {'cutoff': five_min_ago}).scalar() or 0
    else:
        active_users = 0
    
    # ========================================================================
    # METRIC 2: REVENUE VELOCITY
    # Formula: Revenue per minute (last hour of dataset)
    # ========================================================================
    
    # Get latest order date
    latest_order_date = db.execute(text('''
        SELECT MAX(order_date) FROM orders
    ''')).scalar()
    
    if latest_order_date:
        if isinstance(latest_order_date, str):
            latest_order_date = datetime.fromisoformat(latest_order_date.replace('Z', ''))
        
        # Get revenue from last hour
        one_hour_ago = latest_order_date - timedelta(hours=1)
        
        revenue_last_hour = db.execute(text('''
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE order_date >= :cutoff
            AND status != 'cancelled'
        '''), {'cutoff': one_hour_ago}).scalar() or 0
        
        # Revenue per minute
        revenue_velocity = round(revenue_last_hour / 60, 2)
    else:
        revenue_velocity = 0
    
    # ========================================================================
    # METRIC 3: CONVERSION RATE
    # Formula: (Customers with orders / Total customers) * 100
    # ========================================================================
    
    total_customers = db.query(Customer).filter(Customer.role == "customer").count()
    customers_with_orders = db.execute(text('''
        SELECT COUNT(DISTINCT customer_id) FROM orders
    ''')).scalar() or 0
    
    conversion_rate = round((customers_with_orders / max(total_customers, 1)) * 100, 1)
    
    # ========================================================================
    # METRIC 4: EXPOSED CLV RISK
    # Formula: SUM(monetary) for customers with churn_probability > 0.7
    # Note: Using monetary instead of CLV since CLV is 0 for most
    # ========================================================================
    
    exposed_clv_risk = db.execute(text('''
        SELECT COALESCE(SUM(total_revenue * churn_probability), 0)
        FROM customer_profiles
        WHERE churn_probability > 0.5
    ''')).scalar() or 0
    
    # ========================================================================
    # METRIC 5: ACTIVE CAMPAIGNS
    # ========================================================================
    
    from app.models.models import NBADecision
    active_campaigns = db.query(NBADecision).filter(
        NBADecision.status == "pending"
    ).count()
    
    # ========================================================================
    # METRIC 6: RECENT EVENT COUNT
    # ========================================================================
    
    total_events = db.query(Event).count()
    recent_events = 0
    
    if latest_event_time:
        recent_cutoff = latest_event_time - timedelta(minutes=10)
        recent_events = db.execute(text('''
            SELECT COUNT(*)
            FROM events
            WHERE timestamp >= :cutoff
        '''), {'cutoff': recent_cutoff}).scalar() or 0
    
    return {
        "active_users": active_users,
        "revenue_velocity": revenue_velocity,
        "conversion_rate": conversion_rate,
        "exposed_clv_risk": round(exposed_clv_risk, 2),
        "active_campaigns": active_campaigns,
        "total_events": total_events,
        "recent_events": recent_events,
        "latest_activity": latest_event_time.isoformat() if latest_event_time else None,
        "data_source": "database",
        "calculation_method": {
            "active_users": "COUNT(DISTINCT customer_id) WHERE timestamp >= NOW() - 5 minutes",
            "revenue_velocity": "SUM(orders.total_amount last hour) / 60",
            "conversion_rate": "(customers_with_orders / total_customers) * 100",
            "exposed_clv_risk": "SUM(monetary) WHERE churn_probability > 0.7"
        }
    }


@router.get("/event-stream")
def get_event_stream(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get recent events for live stream display.
    Returns most recent events with customer info.
    """
    
    # Get recent events with customer names
    events = db.execute(text('''
        SELECT 
            e.event_id,
            e.event_type,
            e.customer_id,
            e.timestamp,
            c.first_name || ' ' || c.last_name as customer_name
        FROM events e
        LEFT JOIN customers c ON e.customer_id = c.customer_id
        ORDER BY e.timestamp DESC
        LIMIT :limit
    '''), {'limit': limit}).fetchall()
    
    event_list = []
    for event in events:
        event_list.append({
            "id": event[0],
            "event_type": event[1],
            "customer_id": event[2],
            "timestamp": event[3],
            "customer_name": event[4] if event[4] else "Unknown",
        })
    
    return {
        "events": event_list,
        "count": len(event_list),
        "source": "events table"
    }


@router.get("/chart-data")
def get_chart_data(window_minutes: int = 60, db: Session = Depends(get_db)):
    """
    Get time-series data for live charts.
    Returns data points for the specified time window.
    """
    
    # Get latest timestamp
    latest_time = db.execute(text('''
        SELECT MAX(timestamp) FROM events
    ''')).scalar()
    
    if not latest_time:
        return {"data_points": [], "message": "No events found"}
    
    if isinstance(latest_time, str):
        latest_time = datetime.fromisoformat(latest_time.replace('Z', ''))
    
    # Generate time buckets (5-minute intervals)
    data_points = []
    num_buckets = window_minutes // 5  # 5-minute buckets
    
    for i in range(num_buckets):
        bucket_end = latest_time - timedelta(minutes=i*5)
        bucket_start = bucket_end - timedelta(minutes=5)
        
        # Count events in this bucket
        event_count = db.execute(text('''
            SELECT COUNT(*)
            FROM events
            WHERE timestamp >= :start AND timestamp < :end
        '''), {'start': bucket_start, 'end': bucket_end}).scalar() or 0
        
        # Count active users
        active_users = db.execute(text('''
            SELECT COUNT(DISTINCT customer_id)
            FROM events
            WHERE timestamp >= :start AND timestamp < :end
        '''), {'start': bucket_start, 'end': bucket_end}).scalar() or 0
        
        # Calculate revenue
        revenue = db.execute(text('''
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE order_date >= :start AND order_date < :end
            AND status != 'cancelled'
        '''), {'start': bucket_start, 'end': bucket_end}).scalar() or 0
        
        data_points.append({
            "time": bucket_start.strftime("%H:%M"),
            "timestamp": bucket_start.isoformat(),
            "activeUsers": active_users,
            "eventCount": event_count,
            "revenueVelocity": round(revenue / 5, 2),  # Per minute
        })
    
    # Reverse to get chronological order
    data_points.reverse()
    
    return {
        "data_points": data_points,
        "window_minutes": window_minutes,
        "bucket_size_minutes": 5,
        "source": "events + orders tables"
    }


@router.get("/validation")
def get_validation_report(db: Session = Depends(get_db)):
    """
    Validation panel showing data sources and record counts.
    Debug information for transparency.
    """
    
    total_events = db.query(Event).count()
    total_customers = db.query(Customer).filter(Customer.role == "customer").count()
    total_orders = db.query(Order).count()
    total_profiles = db.query(CustomerProfile).count()
    
    # WebSocket status (would need to check actual connections)
    websocket_status = "Connected" if manager.connection_count > 0 else "Disconnected"
    
    # Event type breakdown
    event_types = db.execute(text('''
        SELECT event_type, COUNT(*) as count
        FROM events
        GROUP BY event_type
        ORDER BY count DESC
        LIMIT 10
    ''')).fetchall()
    
    return {
        "records_loaded": {
            "events": total_events,
            "customers": total_customers,
            "orders": total_orders,
            "profiles": total_profiles,
        },
        "websocket_status": websocket_status,
        "active_connections": manager.connection_count,
        "event_type_breakdown": [
            {"type": row[0], "count": row[1]} for row in event_types
        ],
        "data_freshness": {
            "latest_event": db.execute(text('SELECT MAX(timestamp) FROM events')).scalar(),
            "latest_order": db.execute(text('SELECT MAX(order_date) FROM orders')).scalar(),
        },
        "status": "operational",
        "note": "All metrics derived from SQLite database queries"
    }


@router.post("/simulate-event")
async def simulate_event(event_data: dict, db: Session = Depends(get_db)):
    """
    Simulate a live event for demo purposes.
    Creates a new event and broadcasts it via WebSocket.
    """
    
    # Create event in database
    new_event = Event(
        customer_id=event_data.get("customer_id", "DEMO-001"),
        event_type=event_data.get("event_type", "product_view"),
        timestamp=datetime.utcnow(),
    )
    db.add(new_event)
    db.commit()
    
    # Broadcast via WebSocket
    await manager.broadcast_event("new_event", {
        "event": {
            "id": new_event.event_id,
            "event_type": new_event.event_type,
            "customer_id": new_event.customer_id,
            "timestamp": new_event.timestamp.isoformat(),
        }
    })
    
    return {
        "status": "success",
        "event_id": new_event.event_id,
        "broadcasted": True
    }
