import sqlite3
c = sqlite3.connect("omnipulse.db").cursor()

# How many high-risk customers have CLV > 0?
c.execute("""
    SELECT COUNT(*) FROM customer_profiles
    WHERE churn_probability > 0.6 AND clv > 0
""")
print(f"High-risk (>0.6) WITH clv > 0:   {c.fetchone()[0]}")

c.execute("""
    SELECT COUNT(*) FROM customer_profiles
    WHERE churn_probability > 0.6 AND (clv IS NULL OR clv = 0)
""")
print(f"High-risk (>0.6) WITH clv = 0:   {c.fetchone()[0]}")

# Which customers DO have CLV > 0?
c.execute("""
    SELECT MIN(churn_probability), MAX(churn_probability), COUNT(*)
    FROM customer_profiles WHERE clv > 0
""")
r = c.fetchone()
print(f"\nCustomers with clv > 0:")
print(f"  churn_probability range: {r[0]:.3f} – {r[1]:.3f}  (count: {r[2]})")

# Sample high-risk customers with their CLV
c.execute("""
    SELECT customer_id, churn_probability, clv
    FROM customer_profiles WHERE churn_probability > 0.7
    ORDER BY churn_probability DESC LIMIT 10
""")
print(f"\nTop 10 high-risk customers (churn > 0.7):")
for row in c.fetchall():
    print(f"  {row[0]}  churn={row[1]:.3f}  clv={row[2]:.2f}")

# Sample customers with high CLV
c.execute("""
    SELECT customer_id, churn_probability, clv
    FROM customer_profiles WHERE clv > 0
    ORDER BY clv DESC LIMIT 10
""")
print(f"\nTop 10 customers by CLV:")
for row in c.fetchall():
    print(f"  {row[0]}  churn={row[1]:.3f}  clv={row[2]:.2f}")

# Check for overlap
c.execute("""
    SELECT COUNT(*) FROM customer_profiles
    WHERE churn_probability > 0.6 AND clv > 0
""")
overlap = c.fetchone()[0]
print(f"\nOverlap (high churn AND high CLV): {overlap}")
print("This is the DATA REALITY: customers with CLV > 0 are LOW churn risk.")
print("Customers with HIGH churn have CLV = 0 (never purchased = no CLV).")
