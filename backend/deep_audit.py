import sqlite3
c = sqlite3.connect('omnipulse.db')

# Check event types for high-churn customers
print("=== Events for top-5 churn customers ===")
top5 = c.execute("SELECT customer_id FROM customer_profiles ORDER BY churn_probability DESC LIMIT 5").fetchall()
for cid_row in top5:
    cid = cid_row[0]
    events = c.execute("SELECT event_type, COUNT(*) FROM events WHERE customer_id=? GROUP BY event_type", (cid,)).fetchall()
    total = sum(cnt for _, cnt in events)
    print(f"\n  {cid}: {total} total events")
    for et, cnt in events:
        print(f"    {et}: {cnt}")

# Check the event_type casing issue - the compute_churn looks for ADD_TO_CART but seed uses cart_add
print("\n=== Event type casing ===")
types = c.execute("SELECT DISTINCT event_type FROM events ORDER BY event_type").fetchall()
for t in types:
    print(f"  '{t[0]}'")

# Check RFM = 0 issue
print("\n=== RFM values (all zero?) ===")
rfm = c.execute("SELECT recency_days, frequency, monetary FROM customer_profiles LIMIT 10").fetchall()
for r in rfm:
    print(f"  recency={r[0]} frequency={r[1]} monetary={r[2]}")

# Check customer names  
print("\n=== Customer name patterns ===")
sample = c.execute("SELECT customer_id, first_name, last_name FROM customers WHERE role='customer' ORDER BY RANDOM() LIMIT 20").fetchall()
for r in sample:
    print(f"  {r[0]}: {r[1]} {r[2]}")

c.close()
