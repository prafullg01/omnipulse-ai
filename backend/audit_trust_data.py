"""
OMNIPULSE AI - TRUST CENTER DATA AUDIT
Get actual database facts for Trust Center validation
"""
import sqlite3

conn = sqlite3.connect('omnipulse.db')
cur = conn.cursor()

print("="*80)
print("TRUST CENTER DATABASE AUDIT")
print("="*80)

# Trust Distribution
print("\n[1] Trust Distribution (Actual Database):")
print("-"*80)
cur.execute("""
    SELECT 
        CASE 
            WHEN trust_score < 50 THEN 'Low'
            WHEN trust_score < 80 THEN 'Medium'
            ELSE 'High'
        END as level,
        COUNT(*) as count
    FROM customer_profiles
    GROUP BY level
    ORDER BY 
        CASE level
            WHEN 'Low' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'High' THEN 3
        END
""")
results = cur.fetchall()
total = sum(row[1] for row in results)
print(f"{'Level':<15} {'Count':>8}  {'Percentage':>10}")
print("-"*40)
for level, count in results:
    pct = (count / total * 100) if total > 0 else 0
    print(f"{level:<15} {count:>8,}  {pct:>9.1f}%")
print(f"{'TOTAL':<15} {total:>8,}  {100.0:>9.1f}%")

# Order Statistics
print("\n[2] Order Statistics:")
print("-"*80)
cur.execute("SELECT COUNT(*) FROM orders")
total_orders = cur.fetchone()[0]
print(f"Total orders: {total_orders:,}")

cur.execute("SELECT COUNT(*) FROM orders WHERE status='delivered'")
delivered_orders = cur.fetchone()[0]
print(f"Delivered orders: {delivered_orders:,}")

cur.execute("SELECT COUNT(*) FROM orders WHERE status='cancelled'")
cancelled_orders = cur.fetchone()[0]
print(f"Cancelled orders: {cancelled_orders:,}")

cur.execute("SELECT COUNT(DISTINCT status) FROM orders")
print(f"Unique statuses: {cur.fetchone()[0]}")

cur.execute("SELECT DISTINCT status FROM orders")
print(f"Order statuses: {[row[0] for row in cur.fetchall()]}")

# Customer Statistics
print("\n[3] Customer Statistics:")
print("-"*80)
cur.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
total_customers = cur.fetchone()[0]
print(f"Total customers: {total_customers:,}")

cur.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
customers_with_orders = cur.fetchone()[0]
print(f"Customers with orders: {customers_with_orders:,}")

purchase_history_pct = (customers_with_orders / total_customers * 100) if total_customers > 0 else 0
print(f"Purchase History %: {purchase_history_pct:.1f}%")

# Engagement
print("\n[4] Engagement Statistics:")
print("-"*80)
cur.execute("SELECT AVG(engagement_score) FROM customer_profiles")
avg_engagement = cur.fetchone()[0]
print(f"Average engagement score: {avg_engagement:.1f}")

# Events/Complaints
print("\n[5] Events & Complaints:")
print("-"*80)
cur.execute("SELECT COUNT(*) FROM events")
total_events = cur.fetchone()[0]
print(f"Total events: {total_events:,}")

cur.execute("SELECT COUNT(*) FROM events WHERE event_type LIKE '%complaint%'")
complaint_events = cur.fetchone()[0]
print(f"Complaint events: {complaint_events:,}")

cur.execute("SELECT COUNT(DISTINCT customer_id) FROM events WHERE event_type LIKE '%complaint%'")
customers_with_complaints = cur.fetchone()[0]
print(f"Customers with complaints: {customers_with_complaints:,}")

complaint_rate = (customers_with_complaints / total_customers * 100) if total_customers > 0 else 0
print(f"Complaint rate: {complaint_rate:.1f}%")

# Support Tickets
cur.execute("SELECT COUNT(*) FROM support_tickets")
total_tickets = cur.fetchone()[0]
print(f"Total support tickets: {total_tickets:,}")

cur.execute("SELECT COUNT(*) FROM support_tickets WHERE sentiment IN ('angry', 'frustrated')")
negative_tickets = cur.fetchone()[0]
print(f"Negative tickets: {negative_tickets:,}")

# Account Age
print("\n[6] Account Age Statistics:")
print("-"*80)
cur.execute("""
    SELECT COUNT(*) 
    FROM customers 
    WHERE role='customer' 
    AND registration_date < datetime('now', '-90 days')
""")
mature_accounts = cur.fetchone()[0]
print(f"Accounts > 90 days: {mature_accounts:,}")

account_age_pct = (mature_accounts / total_customers * 100) if total_customers > 0 else 0
print(f"Account Age %: {account_age_pct:.1f}%")

# Low Trust Customers
print("\n[7] Low Trust Customers:")
print("-"*80)
cur.execute("""
    SELECT COUNT(*) 
    FROM customer_profiles 
    WHERE trust_score < 50
""")
low_trust_count = cur.fetchone()[0]
print(f"Low trust customers: {low_trust_count:,}")

cur.execute("""
    SELECT c.customer_id, c.first_name, c.last_name, p.trust_score
    FROM customer_profiles p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE p.trust_score < 50
    ORDER BY p.trust_score ASC
    LIMIT 5
""")
print("\nSample Low Trust Customers:")
print(f"{'Customer ID':<15} {'Name':<30} {'Trust Score':>12}")
print("-"*60)
for row in cur.fetchall():
    print(f"{row[0]:<15} {row[1]} {row[2]:<20} {row[3]:>12.1f}")

# Payment Reliability
print("\n[8] Payment Reliability Calculation:")
print("-"*80)
payment_reliability = (delivered_orders / total_orders * 100) if total_orders > 0 else 0
print(f"Payment Reliability = {delivered_orders:,} / {total_orders:,} * 100 = {payment_reliability:.1f}%")

# Return Rate
print("\n[9] Return Rate Calculation:")
print("-"*80)
return_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
print(f"Return Rate = {cancelled_orders:,} / {total_orders:,} * 100 = {return_rate:.1f}%")

print("\n" + "="*80)
print("TRUST DRIVERS SUMMARY (CORRECT VALUES)")
print("="*80)
print(f"Purchase History:     {purchase_history_pct:.1f}%")
print(f"Payment Reliability:  {payment_reliability:.1f}%")
print(f"Return Rate:          {return_rate:.1f}%")
print(f"Complaint History:    {complaint_rate:.1f}%")
print(f"Engagement Level:     {avg_engagement:.1f}")
print(f"Account Age:          {account_age_pct:.1f}%")

conn.close()

print("\n" + "="*80)
print("AUDIT COMPLETE")
print("="*80)
