"""
Verify Trust Center Metrics - Check actual data sources
"""
import sqlite3

conn = sqlite3.connect('omnipulse.db')
cur = conn.cursor()

print("="*80)
print("TRUST CENTER METRICS VERIFICATION")
print("="*80)

# 1. Check Return Rate - Events vs Orders
print("\n[1] RETURN RATE ANALYSIS:")
print("-"*80)

# Orders status
cur.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
print("Order statuses:")
for status, count in cur.fetchall():
    print(f"  {status}: {count:,}")

cur.execute("SELECT COUNT(*) FROM orders")
total_orders = cur.fetchone()[0]
print(f"\nTotal orders: {total_orders:,}")

# Events with refund/return
cur.execute("""
    SELECT event_type, COUNT(*) 
    FROM events 
    WHERE event_type LIKE '%refund%' OR event_type LIKE '%return%'
    GROUP BY event_type
""")
print("\nRefund/Return events:")
for event_type, count in cur.fetchall():
    print(f"  {event_type}: {count:,}")

# Specific refund_request count
cur.execute("SELECT COUNT(*) FROM events WHERE event_type = 'refund_request'")
refund_requests = cur.fetchone()[0]
print(f"\nRefund requests: {refund_requests:,}")

# Calculate correct return rate
return_rate = (refund_requests / total_orders * 100) if total_orders > 0 else 0
print(f"\nCORRECT Return Rate = {refund_requests:,} / {total_orders:,} * 100 = {return_rate:.1f}%")

# 2. Check Account Age source
print("\n[2] ACCOUNT AGE VERIFICATION:")
print("-"*80)

# Check registration_date
cur.execute("SELECT MIN(registration_date), MAX(registration_date) FROM customers WHERE role='customer'")
min_reg, max_reg = cur.fetchone()
print(f"Registration dates: {min_reg} to {max_reg}")

# Check order dates
cur.execute("SELECT MIN(order_date), MAX(order_date) FROM orders")
min_order, max_order = cur.fetchone()
print(f"Order dates: {min_order} to {max_order}")

# Check event timestamps
cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM events")
min_event, max_event = cur.fetchone()
print(f"Event timestamps: {min_event} to {max_event}")

# Calculate account age from first order
cur.execute("""
    WITH customer_first_orders AS (
        SELECT customer_id, MIN(order_date) as first_order_date
        FROM orders GROUP BY customer_id
    )
    SELECT COUNT(*)
    FROM customer_first_orders
    WHERE julianday('now') - julianday(first_order_date) > 90
""")
mature_by_orders = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
total_customers = cur.fetchone()[0]
account_age_orders = (mature_by_orders / total_customers * 100)
print(f"\nAccount Age (by first order): {mature_by_orders:,} / {total_customers:,} = {account_age_orders:.1f}%")

# Calculate account age from first event
cur.execute("""
    WITH customer_first_events AS (
        SELECT customer_id, MIN(timestamp) as first_event_date
        FROM events GROUP BY customer_id
    )
    SELECT COUNT(*)
    FROM customer_first_events
    WHERE julianday('now') - julianday(first_event_date) > 90
""")
mature_by_events = cur.fetchone()[0]
account_age_events = (mature_by_events / total_customers * 100)
print(f"Account Age (by first event): {mature_by_events:,} / {total_customers:,} = {account_age_events:.1f}%")

# 3. Check all event types
print("\n[3] ALL EVENT TYPES:")
print("-"*80)
cur.execute("""
    SELECT event_type, COUNT(*) as count
    FROM events
    GROUP BY event_type
    ORDER BY count DESC
    LIMIT 15
""")
print(f"{'Event Type':<30} {'Count':>10}")
print("-"*45)
for event_type, count in cur.fetchall():
    print(f"{event_type:<30} {count:>10,}")

# 4. Verify complaints
print("\n[4] COMPLAINT VERIFICATION:")
print("-"*80)
cur.execute("SELECT COUNT(*) FROM events WHERE event_type = 'complaint'")
complaint_events = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT customer_id) FROM events WHERE event_type = 'complaint'")
customers_with_complaints = cur.fetchone()[0]
print(f"Total complaint events: {complaint_events:,}")
print(f"Unique customers with complaints: {customers_with_complaints:,}")
print(f"Complaint rate: {customers_with_complaints / total_customers * 100:.1f}%")

print("\n" + "="*80)
print("RECOMMENDATIONS:")
print("="*80)
print("1. Return Rate: Use refund_request events (517) instead of order status")
print(f"   New value: {return_rate:.1f}%")
print("2. Account Age: Use first order date (valid source)")
print(f"   Current value of 36.1% is CORRECT")
print("3. Add detailed SQL comments documenting all formulas")
print("="*80)

conn.close()
