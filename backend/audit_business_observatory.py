"""Business Observatory Audit - Phase 1"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()

print("=" * 80)
print("BUSINESS OBSERVATORY - BACKEND AUDIT")
print("=" * 80)

# Event Statistics
print("\n1. EVENT DATA AVAILABILITY")
print("-" * 80)

total_events = c.execute('SELECT COUNT(*) FROM events').fetchone()[0]
print(f"Total events: {total_events:,}")

event_types = c.execute('SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC').fetchall()
print(f"\nEvent type distribution:")
for event_type, count in event_types:
    print(f"  {event_type}: {count:,}")

# Recent activity
print(f"\n2. RECENT ACTIVITY (Last 24 hours)")
print("-" * 80)

# Note: All timestamps are historical, so we'll analyze the dataset's timeframe
latest_event = c.execute('SELECT MAX(timestamp) FROM events').fetchone()[0]
earliest_event = c.execute('SELECT MIN(timestamp) FROM events').fetchone()[0]

print(f"Dataset timeframe: {earliest_event} to {latest_event}")

# Active users calculation
print(f"\n3. ACTIVE USERS CALCULATION")
print("-" * 80)

# Method A: Users with recent activity (last hour of dataset)
# SQLite doesn't support INTERVAL, use datetime() instead
active_recent = c.execute('''
    SELECT COUNT(DISTINCT customer_id)
    FROM events
    WHERE timestamp >= datetime((SELECT MAX(timestamp) FROM events), '-1 hour')
''').fetchone()[0]

print(f"Method A (last hour of dataset): {active_recent} users")

# Method B: Users with events in last day of dataset
active_day = c.execute('''
    SELECT COUNT(DISTINCT customer_id)
    FROM events
    WHERE DATE(timestamp) = (SELECT DATE(MAX(timestamp)) FROM events)
''').fetchone()[0]

print(f"Method B (last day of dataset): {active_day} users")

# Revenue Velocity
print(f"\n4. REVENUE VELOCITY CALCULATION")
print("-" * 80)

# Get orders in last hour of dataset
latest_order = c.execute('SELECT MAX(order_date) FROM orders').fetchone()[0]
print(f"Latest order: {latest_order}")

recent_revenue = c.execute('''
    SELECT COALESCE(SUM(total_amount), 0), COUNT(*)
    FROM orders
    WHERE order_date >= datetime((SELECT MAX(order_date) FROM orders), '-1 hour')
    AND status != 'cancelled'
''').fetchone()

revenue_last_hour = recent_revenue[0]
orders_last_hour = recent_revenue[1]

print(f"Revenue in last hour of dataset: ₹{revenue_last_hour:,.2f}")
print(f"Orders in last hour: {orders_last_hour}")
print(f"Revenue per minute: ₹{revenue_last_hour/60:,.2f}/min")

# Conversion Rate
print(f"\n5. CONVERSION RATE CALCULATION")
print("-" * 80)

total_customers = c.execute('SELECT COUNT(*) FROM customers WHERE role = "customer"').fetchone()[0]
customers_with_orders = c.execute('SELECT COUNT(DISTINCT customer_id) FROM orders').fetchone()[0]

conversion_rate = (customers_with_orders / total_customers * 100) if total_customers > 0 else 0

print(f"Total customers: {total_customers:,}")
print(f"Customers with orders: {customers_with_orders:,}")
print(f"Conversion rate: {conversion_rate:.2f}%")

# Exposed CLV Risk
print(f"\n6. EXPOSED CLV RISK CALCULATION")
print("-" * 80)

exposed_clv = c.execute('''
    SELECT COALESCE(SUM(clv), 0), COUNT(*)
    FROM customer_profiles
    WHERE churn_probability > 0.70
''').fetchone()

exposed_clv_value = exposed_clv[0]
high_risk_count = exposed_clv[1]

print(f"High-risk customers (>70% churn): {high_risk_count:,}")
print(f"CLV exposed: ₹{exposed_clv_value:,.2f}")

# Alternative calculation using monetary
exposed_monetary = c.execute('''
    SELECT COALESCE(SUM(monetary), 0)
    FROM customer_profiles
    WHERE churn_probability > 0.70
''').fetchone()[0]

print(f"Monetary exposed (alternative): ₹{exposed_monetary:,.2f}")

# Live Stream Data
print(f"\n7. LIVE STREAM DATA SIMULATION")
print("-" * 80)

# Get recent events for stream (without metadata column)
recent_events = c.execute('''
    SELECT event_type, customer_id, timestamp
    FROM events
    ORDER BY timestamp DESC
    LIMIT 10
''').fetchall()

print("Recent events (for live stream):")
for event_type, customer_id, timestamp in recent_events:
    print(f"  [{timestamp}] {event_type} - {customer_id}")

# Summary Report
print(f"\n" + "=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)

metrics = [
    ("Active Users", f"{active_day:,}", "events table", "COUNT(DISTINCT customer_id) last day", "REAL"),
    ("Revenue Velocity", f"₹{revenue_last_hour/60:,.2f}/min", "orders table", "SUM(total_amount)/60", "REAL"),
    ("Conversion Rate", f"{conversion_rate:.2f}%", "customers + orders", "purchasers/total_customers", "REAL"),
    ("Exposed CLV Risk", f"₹{exposed_monetary:,.2f}", "customer_profiles", "SUM(monetary) WHERE churn>0.7", "REAL"),
    ("Event Feed", f"{total_events:,} events", "events table", "ORDER BY timestamp DESC", "REAL"),
    ("Live Stream Data", f"{len(recent_events)} recent", "events table", "Real-time query", "REAL"),
]

print("\nMetric Report:")
print(f"{'Metric':<20} {'Value':<20} {'Source':<25} {'Calculation':<40} {'Type':<10}")
print("-" * 115)
for metric, value, source, calc, mtype in metrics:
    print(f"{metric:<20} {value:<20} {source:<25} {calc:<40} {mtype:<10}")

print(f"\n✅ ALL METRICS ARE DATABASE-BACKED")
print(f"⚠️  NOTE: Dataset is historical, not real-time")
print(f"   Latest data: {latest_order}")
print(f"   For real-time: Need to generate live events or use simulation")

conn.close()
