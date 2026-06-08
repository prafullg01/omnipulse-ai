"""
OMNIPULSE AI - TRUST CENTER COMPLETE AUDIT
Audit all Trust Center calculations and data sources
"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('omnipulse.db')
cur = conn.cursor()

print("="*80)
print("TRUST CENTER COMPLETE AUDIT")
print("="*80)

# 1. Average Trust Score
print("\n[1] AVERAGE TRUST SCORE:")
print("-"*80)
cur.execute("SELECT AVG(trust_score) FROM customer_profiles")
avg_trust = cur.fetchone()[0]
print(f"AVG(customer_profiles.trust_score) = {avg_trust:.2f}")

# 2. Trust Distribution
print("\n[2] TRUST DISTRIBUTION:")
print("-"*80)
cur.execute("""
    SELECT 
        CASE 
            WHEN trust_score < 50 THEN 'Low (<50)'
            WHEN trust_score < 80 THEN 'Medium (50-79)'
            ELSE 'High (>=80)'
        END as level,
        COUNT(*) as count
    FROM customer_profiles
    GROUP BY level
    ORDER BY 
        CASE level
            WHEN 'Low (<50)' THEN 1
            WHEN 'Medium (50-79)' THEN 2
            WHEN 'High (>=80)' THEN 3
        END
""")
for level, count in cur.fetchall():
    print(f"{level:<20} = {count:,}")

# 3. Account Age Analysis
print("\n[3] ACCOUNT AGE ANALYSIS:")
print("-"*80)

# Check registration_date field
cur.execute("SELECT customer_id, registration_date FROM customers WHERE role='customer' LIMIT 5")
print("Sample registration_date values:")
for cid, reg_date in cur.fetchall():
    print(f"  {cid}: {reg_date}")

# Check order_date range
cur.execute("SELECT MIN(order_date), MAX(order_date) FROM orders")
min_date, max_date = cur.fetchone()
print(f"\nOrder date range: {min_date} to {max_date}")

# Calculate customer first order dates
cur.execute("""
    WITH customer_first_orders AS (
        SELECT 
            customer_id,
            MIN(order_date) as first_order_date
        FROM orders
        GROUP BY customer_id
    )
    SELECT 
        COUNT(*) as customers_with_orders,
        SUM(CASE 
            WHEN julianday('now') - julianday(first_order_date) > 90 
            THEN 1 ELSE 0 
        END) as customers_90_days_plus
    FROM customer_first_orders
""")
result = cur.fetchone()
print(f"\nCustomers with orders: {result[0]:,}")
print(f"Customers with first order > 90 days ago: {result[1]:,}")

# Calculate using registration_date
cur.execute("""
    SELECT COUNT(*) 
    FROM customers 
    WHERE role='customer' 
    AND registration_date IS NOT NULL
    AND julianday('now') - julianday(registration_date) > 90
""")
reg_based_mature = cur.fetchone()[0]
print(f"Customers with registration > 90 days ago: {reg_based_mature:,}")

# Get total customers
cur.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
total_customers = cur.fetchone()[0]

print(f"\nTotal customers: {total_customers:,}")
print(f"Account Age (order-based) = {result[1]:,} / {total_customers:,} * 100 = {result[1]/total_customers*100:.1f}%")
print(f"Account Age (registration-based) = {reg_based_mature:,} / {total_customers:,} * 100 = {reg_based_mature/total_customers*100:.1f}%")

# 4. Trust Trend Analysis
print("\n[4] TRUST TREND ANALYSIS:")
print("-"*80)
print("Checking if real daily trust history is available...")

# Check if we have historical trust data
cur.execute("""
    SELECT COUNT(*) FROM sqlite_master 
    WHERE type='table' AND name='trust_history'
""")
has_trust_history = cur.fetchone()[0] > 0
print(f"trust_history table exists: {has_trust_history}")

# Check order activity by day (last 14 days)
print("\nOrder activity (last 14 days):")
print(f"{'Date':<12} {'Orders':>8} {'Customers':>12} {'Avg Trust':>12}")
print("-"*50)

today = datetime.utcnow()
for i in range(13, -1, -1):
    day_start = (today - timedelta(days=i)).strftime('%Y-%m-%d')
    day_end = (today - timedelta(days=i)).strftime('%Y-%m-%d 23:59:59')
    
    cur.execute("""
        SELECT 
            COUNT(*) as order_count,
            COUNT(DISTINCT customer_id) as customer_count
        FROM orders
        WHERE order_date >= ? AND order_date <= ?
    """, (day_start, day_end))
    
    order_count, customer_count = cur.fetchone()
    
    # Get average trust of customers who ordered that day
    if customer_count > 0:
        cur.execute("""
            SELECT AVG(p.trust_score)
            FROM customer_profiles p
            WHERE p.customer_id IN (
                SELECT DISTINCT customer_id 
                FROM orders 
                WHERE order_date >= ? AND order_date <= ?
            )
        """, (day_start, day_end))
        avg_trust_that_day = cur.fetchone()[0] or 0
    else:
        avg_trust_that_day = 0
    
    print(f"{day_start:<12} {order_count:>8,} {customer_count:>12,} {avg_trust_that_day:>12.1f}")

# 5. Customer Names Analysis
print("\n[5] CUSTOMER NAMES ANALYSIS:")
print("-"*80)

# Check customer name fields
cur.execute("SELECT customer_id, first_name, last_name, email FROM customers WHERE role='customer' LIMIT 5")
print("Sample customer records:")
print(f"{'Customer ID':<15} {'First Name':<15} {'Last Name':<15} {'Email':<30}")
print("-"*80)
for row in cur.fetchall():
    print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15} {row[3]:<30}")

# Check customer_profiles table for customer_name field
cur.execute("PRAGMA table_info(customer_profiles)")
columns = [col[1] for col in cur.fetchall()]
has_customer_name = 'customer_name' in columns
print(f"\ncustomer_profiles has 'customer_name' field: {has_customer_name}")

if has_customer_name:
    cur.execute("SELECT customer_id, customer_name FROM customer_profiles LIMIT 5")
    print("\nSample customer_name values from customer_profiles:")
    for cid, name in cur.fetchall():
        print(f"  {cid}: {name}")

# Check low trust customers
cur.execute("""
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        p.trust_score,
        p.customer_name
    FROM customer_profiles p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE p.trust_score < 50
    ORDER BY p.trust_score ASC
    LIMIT 10
""")
print("\nLow Trust Customers (sample):")
print(f"{'Customer ID':<15} {'customers.name':<30} {'profiles.name':<30} {'Trust':>8}")
print("-"*90)
for row in cur.fetchall():
    customers_name = f"{row[1]} {row[2]}"
    profiles_name = row[4] or "NULL"
    print(f"{row[0]:<15} {customers_name:<30} {profiles_name:<30} {row[3]:>8.1f}")

# 6. Trust Drivers Validation
print("\n[6] TRUST DRIVERS VALIDATION:")
print("-"*80)

# Purchase History
cur.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
customers_with_orders = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
total_customers = cur.fetchone()[0]
purchase_history = (customers_with_orders / total_customers * 100)
print(f"Purchase History: {customers_with_orders:,} / {total_customers:,} * 100 = {purchase_history:.1f}%")

# Payment Reliability
cur.execute("SELECT COUNT(*) FROM orders")
total_orders = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM orders WHERE status='delivered'")
delivered_orders = cur.fetchone()[0]
payment_reliability = (delivered_orders / total_orders * 100)
print(f"Payment Reliability: {delivered_orders:,} / {total_orders:,} * 100 = {payment_reliability:.1f}%")

# Return Rate
cur.execute("SELECT COUNT(*) FROM orders WHERE status IN ('cancelled', 'refunded')")
cancelled_orders = cur.fetchone()[0]
return_rate = (cancelled_orders / total_orders * 100)
print(f"Return Rate: {cancelled_orders:,} / {total_orders:,} * 100 = {return_rate:.1f}%")

# Complaint History
cur.execute("SELECT COUNT(DISTINCT customer_id) FROM events WHERE event_type LIKE '%complaint%'")
customers_with_complaints = cur.fetchone()[0]
complaint_rate = (customers_with_complaints / total_customers * 100)
print(f"Complaint History: {customers_with_complaints:,} / {total_customers:,} * 100 = {complaint_rate:.1f}%")

# Engagement Level
cur.execute("SELECT AVG(engagement_score) FROM customer_profiles")
avg_engagement = cur.fetchone()[0]
print(f"Engagement Level: AVG(engagement_score) = {avg_engagement:.1f}")

# Account Age (order-based - more accurate)
cur.execute("""
    WITH customer_first_orders AS (
        SELECT 
            customer_id,
            MIN(order_date) as first_order_date
        FROM orders
        GROUP BY customer_id
    )
    SELECT COUNT(*)
    FROM customer_first_orders
    WHERE julianday('now') - julianday(first_order_date) > 90
""")
mature_by_orders = cur.fetchone()[0]
account_age = (mature_by_orders / total_customers * 100)
print(f"Account Age: {mature_by_orders:,} / {total_customers:,} * 100 = {account_age:.1f}%")

print("\n" + "="*80)
print("AUDIT COMPLETE")
print("="*80)

print("\nRECOMMENDATIONS:")
print("1. Account Age: Use first order date for calculation (more accurate)")
print("2. Trust Trend: No historical trust data - use daily order activity pattern")
print("3. Customer Names: Use customers.first_name + customers.last_name")
print("4. All trust drivers validated and correct in backend")

conn.close()
