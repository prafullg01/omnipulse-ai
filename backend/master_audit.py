"""
COMPREHENSIVE DATABASE AUDIT
Checks all values mentioned in the master audit prompt.
"""
import sqlite3
import json

conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()

print("=" * 80)
print("OMNIPULSE DATABASE AUDIT")
print("=" * 80)

# 1. Churn probability distribution
print("\n--- CHURN PROBABILITY DISTRIBUTION ---")
r = c.execute("""
    SELECT 
        MIN(churn_probability) as min_churn,
        AVG(churn_probability) as avg_churn,
        MAX(churn_probability) as max_churn,
        COUNT(DISTINCT ROUND(churn_probability, 2)) as unique_values
    FROM customer_profiles
""").fetchone()
print(f"  Min: {r[0]:.4f}")
print(f"  Avg: {r[1]:.4f}")
print(f"  Max: {r[2]:.4f}")
print(f"  Unique values (2dp): {r[3]}")

# Check if many are exactly 0.92
r92 = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE ABS(churn_probability - 0.92) < 0.001").fetchone()[0]
print(f"  Customers with churn ~0.92: {r92}")

# Top 20 churn values
print("\n  Top 20 churn probabilities:")
top = c.execute("SELECT customer_id, churn_probability, trust_score, engagement_score, emotion FROM customer_profiles ORDER BY churn_probability DESC LIMIT 20").fetchall()
for row in top:
    print(f"    {row[0]}: churn={row[1]:.4f} trust={row[2]:.1f} engagement={row[3]:.1f} emotion={row[4]}")

# 2. CLV distribution
print("\n--- CLV DISTRIBUTION ---")
r = c.execute("""
    SELECT 
        MIN(clv) as min_clv,
        AVG(clv) as avg_clv,
        MAX(clv) as max_clv,
        COUNT(*) FILTER (WHERE clv = 0) as zero_count,
        COUNT(*) FILTER (WHERE clv > 0) as nonzero_count,
        COUNT(*) as total
    FROM customer_profiles
""").fetchone()
print(f"  Min: {r[0]}")
print(f"  Avg: {r[1]}")
print(f"  Max: {r[2]}")
# SQLite doesn't support FILTER, use subqueries
zero_clv = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE clv = 0 OR clv IS NULL").fetchone()[0]
nonzero_clv = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE clv > 0").fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM customer_profiles").fetchone()[0]
print(f"  CLV = 0: {zero_clv}")
print(f"  CLV > 0: {nonzero_clv}")
print(f"  Total: {total}")

# predicted_clv
print("\n--- PREDICTED CLV ---")
r = c.execute("SELECT MIN(predicted_clv), AVG(predicted_clv), MAX(predicted_clv) FROM customer_profiles").fetchone()
print(f"  Min: {r[0]}")
print(f"  Avg: {r[1]}")
print(f"  Max: {r[2]}")
pred_zero = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE predicted_clv = 0 OR predicted_clv IS NULL").fetchone()[0]
print(f"  predicted_clv = 0/NULL: {pred_zero}")

# 3. Emotion distribution
print("\n--- EMOTION DISTRIBUTION ---")
r = c.execute("SELECT emotion, COUNT(*) FROM customer_profiles GROUP BY emotion ORDER BY COUNT(*) DESC").fetchall()
for row in r:
    print(f"  {row[0]}: {row[1]}")

# 4. Trust score distribution
print("\n--- TRUST SCORE DISTRIBUTION ---")
r = c.execute("SELECT MIN(trust_score), AVG(trust_score), MAX(trust_score) FROM customer_profiles").fetchone()
print(f"  Min: {r[0]:.1f}  Avg: {r[1]:.1f}  Max: {r[2]:.1f}")
# Check if many are 47
t47 = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE ABS(trust_score - 47) < 1").fetchone()[0]
print(f"  Trust ~47: {t47}")

# 5. Engagement score
print("\n--- ENGAGEMENT SCORE ---")
r = c.execute("SELECT MIN(engagement_score), AVG(engagement_score), MAX(engagement_score) FROM customer_profiles").fetchone()
print(f"  Min: {r[0]:.1f}  Avg: {r[1]:.1f}  Max: {r[2]:.1f}")

# 6. Customer names
print("\n--- CUSTOMER NAMES ---")
r = c.execute("SELECT first_name, last_name FROM customers WHERE role='customer' LIMIT 10").fetchall()
for row in r:
    print(f"  {row[0]} {row[1]}")
# Check for 'CustomerNNNN' pattern
fake_names = c.execute("SELECT COUNT(*) FROM customers WHERE first_name LIKE 'Customer%'").fetchone()[0]
print(f"  Names matching 'Customer*': {fake_names}")
real_names = c.execute("SELECT COUNT(*) FROM customers WHERE first_name NOT LIKE 'Customer%' AND role='customer'").fetchone()[0]
print(f"  Real names: {real_names}")

# Also check customer_profiles.customer_name
print("\n--- CUSTOMER_PROFILES.CUSTOMER_NAME ---")
r = c.execute("SELECT customer_name FROM customer_profiles WHERE customer_name IS NOT NULL LIMIT 10").fetchall()
for row in r:
    print(f"  {row[0]}")
null_names = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE customer_name IS NULL OR customer_name = ''").fetchone()[0]
print(f"  NULL/empty customer_name: {null_names}")

# 7. Support tickets
print("\n--- SUPPORT TICKETS ---")
total_tickets = c.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]
print(f"  Total tickets: {total_tickets}")
if total_tickets > 0:
    r = c.execute("SELECT sentiment, COUNT(*) FROM support_tickets GROUP BY sentiment").fetchall()
    for row in r:
        print(f"  Sentiment '{row[0]}': {row[1]}")

# 8. Events
print("\n--- EVENTS ---")
total_events = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
print(f"  Total events: {total_events}")
r = c.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC LIMIT 15").fetchall()
for row in r:
    print(f"  {row[0]}: {row[1]}")

# 9. Orders per customer
print("\n--- ORDERS ---")
total_orders = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
customers_with_orders = c.execute("SELECT COUNT(DISTINCT customer_id) FROM orders").fetchone()[0]
avg_order = c.execute("SELECT AVG(total_amount) FROM orders WHERE status != 'cancelled'").fetchone()[0]
print(f"  Total orders: {total_orders}")
print(f"  Customers with orders: {customers_with_orders}")
print(f"  Avg order amount: {avg_order:.2f}")

# 10. Revenue by customer (top 10)
print("\n--- TOP 10 CUSTOMERS BY REVENUE ---")
r = c.execute("""
    SELECT o.customer_id, 
           SUM(o.total_amount) as total_rev,
           COUNT(*) as order_count,
           cp.churn_probability,
           cp.clv,
           cp.trust_score
    FROM orders o
    JOIN customer_profiles cp ON o.customer_id = cp.customer_id
    WHERE o.status != 'cancelled'
    GROUP BY o.customer_id
    ORDER BY total_rev DESC
    LIMIT 10
""").fetchall()
for row in r:
    print(f"  {row[0]}: revenue={row[1]:.0f} orders={row[2]} churn={row[3]:.3f} clv={row[4]} trust={row[5]:.1f}")

# 11. Persona/Segment/Journey stage
print("\n--- PERSONA/SEGMENT/JOURNEY DISTRIBUTION ---")
r = c.execute("SELECT persona, COUNT(*) FROM customer_profiles GROUP BY persona ORDER BY COUNT(*) DESC").fetchall()
print("  Personas:")
for row in r:
    print(f"    {row[0]}: {row[1]}")

r = c.execute("SELECT segment, COUNT(*) FROM customer_profiles GROUP BY segment ORDER BY COUNT(*) DESC").fetchall()
print("  Segments:")
for row in r:
    print(f"    {row[0]}: {row[1]}")

r = c.execute("SELECT journey_stage, COUNT(*) FROM customer_profiles GROUP BY journey_stage ORDER BY COUNT(*) DESC").fetchall()
print("  Journey stages:")
for row in r:
    print(f"    {row[0]}: {row[1]}")

# 12. RFM values
print("\n--- RFM VALUES ---")
r = c.execute("""
    SELECT 
        MIN(recency_days), AVG(recency_days), MAX(recency_days),
        MIN(frequency), AVG(frequency), MAX(frequency),
        MIN(monetary), AVG(monetary), MAX(monetary)
    FROM customer_profiles
""").fetchone()
print(f"  Recency: min={r[0]} avg={r[1]:.1f} max={r[2]}")
print(f"  Frequency: min={r[3]} avg={r[4]:.1f} max={r[5]}")
print(f"  Monetary: min={r[6]} avg={r[7]:.1f} max={r[8]}")

# 13. Total revenue and revenue at risk
print("\n--- REVENUE AT RISK CALCULATION ---")
total_rev = c.execute("SELECT SUM(total_amount) FROM orders WHERE status != 'cancelled'").fetchone()[0]
print(f"  Total platform revenue: {total_rev:.2f}")
rar = c.execute("""
    SELECT SUM(cp.total_revenue * cp.churn_probability)
    FROM customer_profiles cp
    WHERE cp.churn_probability > 0.7 AND cp.total_revenue > 0
""").fetchone()[0]
print(f"  Revenue at risk (total_rev * churn for high-risk): {rar}")
rar2 = c.execute("""
    SELECT SUM(o.total_amount * cp.churn_probability)
    FROM orders o
    JOIN customer_profiles cp ON o.customer_id = cp.customer_id
    WHERE cp.churn_probability > 0.7 AND o.status != 'cancelled'
""").fetchone()[0]
print(f"  Revenue at risk (from orders join): {rar2}")

# 14. total_revenue in customer_profiles
print("\n--- CUSTOMER_PROFILES.TOTAL_REVENUE ---")
tr = c.execute("SELECT MIN(total_revenue), AVG(total_revenue), MAX(total_revenue) FROM customer_profiles").fetchone()
print(f"  Min: {tr[0]}  Avg: {tr[1]}  Max: {tr[2]}")
tr_zero = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE total_revenue = 0 OR total_revenue IS NULL").fetchone()[0]
print(f"  total_revenue = 0/NULL: {tr_zero}")

# 15. Competitive risk
print("\n--- COMPETITIVE RISK ---")
cr = c.execute("SELECT MIN(competitive_risk), AVG(competitive_risk), MAX(competitive_risk) FROM customer_profiles").fetchone()
print(f"  Min: {cr[0]}  Avg: {cr[1]}  Max: {cr[2]}")

# 16. Risk score
print("\n--- RISK SCORE ---")
rs = c.execute("SELECT MIN(risk_score), AVG(risk_score), MAX(risk_score) FROM customer_profiles").fetchone()
print(f"  Min: {rs[0]}  Avg: {rs[1]}  Max: {rs[2]}")

conn.close()
print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
