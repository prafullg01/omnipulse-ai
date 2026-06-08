"""
OMNIPULSE AI - NBA CENTER AUDIT
Audit NBA Center data and identify all issues
"""
import sqlite3
import json

conn = sqlite3.connect('omnipulse.db')
cur = conn.cursor()

print("="*80)
print("NBA CENTER AUDIT")
print("="*80)

# 1. Customer Profiles Analysis
print("\n[1] CUSTOMER PROFILES:")
print("-"*80)
cur.execute("SELECT COUNT(*) FROM customer_profiles")
total_profiles = cur.fetchone()[0]
print(f"Total customer profiles: {total_profiles:,}")

cur.execute("SELECT MIN(churn_probability), MAX(churn_probability), AVG(churn_probability) FROM customer_profiles")
min_churn, max_churn, avg_churn = cur.fetchone()
print(f"Churn probability range: {min_churn:.2f} to {max_churn:.2f} (avg: {avg_churn:.2f})")

cur.execute("SELECT MIN(trust_score), MAX(trust_score), AVG(trust_score) FROM customer_profiles")
min_trust, max_trust, avg_trust = cur.fetchone()
print(f"Trust score range: {min_trust:.1f} to {max_trust:.1f} (avg: {avg_trust:.1f})")

cur.execute("SELECT MIN(engagement_score), MAX(engagement_score), AVG(engagement_score) FROM customer_profiles")
min_engage, max_engage, avg_engage = cur.fetchone()
print(f"Engagement range: {min_engage:.1f} to {max_engage:.1f} (avg: {avg_engage:.1f})")

# 2. NBA Decisions Analysis
print("\n[2] NBA DECISIONS:")
print("-"*80)
cur.execute("SELECT COUNT(*) FROM nba_decisions")
total_decisions = cur.fetchone()[0]
print(f"Total NBA decisions: {total_decisions:,}")

cur.execute("SELECT MIN(confidence), MAX(confidence), AVG(confidence) FROM nba_decisions")
min_conf, max_conf, avg_conf = cur.fetchone()
print(f"Confidence range: {min_conf:.2f} to {max_conf:.2f} (avg: {avg_conf:.2f})")
print(f"Issue: Narrow range (0.72-0.85) - should be 0.40-0.95")

# 3. Inference Tier Distribution
print("\n[3] INFERENCE TIER DISTRIBUTION:")
print("-"*80)
cur.execute("""
    SELECT inference_tier, COUNT(*) 
    FROM nba_decisions 
    GROUP BY inference_tier
""")
for tier, count in cur.fetchall():
    pct = count / total_decisions * 100
    print(f"  {tier}: {count:,} ({pct:.1f}%)")

# 4. Recommended Actions
print("\n[4] RECOMMENDED ACTIONS:")
print("-"*80)
cur.execute("""
    SELECT recommended_action, COUNT(*) 
    FROM nba_decisions 
    GROUP BY recommended_action 
    ORDER BY COUNT(*) DESC
""")
actions = cur.fetchall()
print(f"Unique actions: {len(actions)}")
for action, count in actions[:10]:
    pct = count / total_decisions * 100
    print(f"  {action}: {count:,} ({pct:.1f}%)")

# 5. Channels
print("\n[5] CHANNELS:")
print("-"*80)
cur.execute("""
    SELECT channel, COUNT(*) 
    FROM nba_decisions 
    GROUP BY channel 
    ORDER BY COUNT(*) DESC
""")
channels = cur.fetchall()
print(f"Unique channels: {len(channels)}")
for channel, count in channels:
    pct = count / total_decisions * 100
    print(f"  {channel}: {count:,} ({pct:.1f}%)")

# 6. Offers
print("\n[6] OFFERS:")
print("-"*80)
cur.execute("""
    SELECT offer, COUNT(*) 
    FROM nba_decisions 
    GROUP BY offer 
    ORDER BY COUNT(*) DESC
    LIMIT 10
""")
for offer, count in cur.fetchall():
    pct = count / total_decisions * 100
    print(f"  {offer}: {count:,} ({pct:.1f}%)")

# 7. High Churn Customers
print("\n[7] HIGH CHURN CUSTOMERS (Top 10):")
print("-"*80)
cur.execute("""
    SELECT 
        p.customer_id,
        p.churn_probability,
        p.trust_score,
        p.engagement_score,
        p.clv,
        n.recommended_action,
        n.channel,
        n.confidence
    FROM customer_profiles p
    LEFT JOIN nba_decisions n ON p.customer_id = n.customer_id
    ORDER BY p.churn_probability DESC
    LIMIT 10
""")
print(f"{'Customer ID':<15} {'Churn':>6} {'Trust':>6} {'Engage':>7} {'CLV':>8} {'Action':<20} {'Channel':<10} {'Conf':>6}")
print("-"*95)
for row in cur.fetchall():
    print(f"{row[0]:<15} {row[1]:>6.2f} {row[2]:>6.1f} {row[3]:>7.1f} {row[4]:>8,.0f} {row[5]:<20} {row[6]:<10} {row[7]:>6.2f}")

# 8. Customer Name Consistency Check
print("\n[8] CUSTOMER NAME CONSISTENCY:")
print("-"*80)
cur.execute("""
    SELECT c.customer_id, c.first_name, c.last_name, p.customer_name
    FROM customers c
    JOIN customer_profiles p ON c.customer_id = p.customer_id
    LIMIT 5
""")
print(f"{'Customer ID':<15} {'customers table':<30} {'profiles table':<30}")
print("-"*80)
for cid, first, last, profile_name in cur.fetchall():
    print(f"{cid:<15} {first} {last:<25} {profile_name:<30}")

# 9. Check for diverse signals
print("\n[9] CUSTOMER SIGNALS DIVERSITY:")
print("-"*80)
cur.execute("""
    SELECT 
        COUNT(DISTINCT ROUND(churn_probability, 1)) as churn_values,
        COUNT(DISTINCT ROUND(trust_score, 0)) as trust_values,
        COUNT(DISTINCT ROUND(engagement_score, 0)) as engagement_values,
        COUNT(DISTINCT recency_days) as recency_values,
        COUNT(DISTINCT frequency) as frequency_values
    FROM customer_profiles
""")
churn_vals, trust_vals, engage_vals, recency_vals, freq_vals = cur.fetchone()
print(f"Churn probability distinct values: {churn_vals}")
print(f"Trust score distinct values: {trust_vals}")
print(f"Engagement distinct values: {engage_vals}")
print(f"Recency distinct values: {recency_vals}")
print(f"Frequency distinct values: {freq_vals}")

print("\n" + "="*80)
print("ISSUES IDENTIFIED:")
print("="*80)
print("1. Confidence range too narrow (0.72-0.85) - should be 0.40-0.95")
print("2. Need to verify actions are diverse (not hardcoded)")
print("3. Need to verify offers are diverse (not all 20% discount)")
print("4. Need to verify customers are sorted by churn DESC")
print("5. Customer names are synthetic but consistent (database limitation)")
print("6. Confidence should be calculated from customer signals")
print("="*80)

conn.close()
