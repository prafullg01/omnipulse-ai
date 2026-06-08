"""Digital Twin Lab Audit Script"""
import sqlite3

conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()

print("=" * 80)
print("DIGITAL TWIN LAB - COMPREHENSIVE AUDIT")
print("=" * 80)

# Issue #1: Customer List Size
print("\n1. CUSTOMER LIST AVAILABILITY")
print("-" * 80)

total_customers = c.execute('SELECT COUNT(*) FROM customers WHERE role = "customer"').fetchone()[0]
total_profiles = c.execute('SELECT COUNT(*) FROM customer_profiles').fetchone()[0]

print(f"Total customers: {total_customers:,}")
print(f"Total profiles: {total_profiles:,}")
print(f"Match: {total_customers == total_profiles}")

# Issue #2: CLV Distribution
print("\n2. CLV DISTRIBUTION")
print("-" * 80)

clv_stats = c.execute('''
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN clv > 0 THEN 1 END) as clv_nonzero,
        AVG(clv) as avg_clv,
        MAX(clv) as max_clv,
        MIN(clv) as min_clv
    FROM customer_profiles
''').fetchone()

print(f"Total profiles: {clv_stats[0]:,}")
print(f"CLV > 0: {clv_stats[1]:,} ({clv_stats[1]/clv_stats[0]*100:.1f}%)")
print(f"CLV = 0: {clv_stats[0] - clv_stats[1]:,} ({(clv_stats[0]-clv_stats[1])/clv_stats[0]*100:.1f}%)")
print(f"Avg CLV: ₹{clv_stats[2] or 0:,.2f}")
print(f"Max CLV: ₹{clv_stats[3] or 0:,.2f}")
print(f"Min CLV: ₹{clv_stats[4] or 0:,.2f}")

# Calculate alternative CLV sources
print("\n   Alternative CLV Sources:")

# From orders
orders_based_clv = c.execute('''
    SELECT 
        cp.customer_id,
        cp.clv as profile_clv,
        COALESCE(SUM(o.total_amount), 0) as orders_clv
    FROM customer_profiles cp
    LEFT JOIN orders o ON cp.customer_id = o.customer_id AND o.status != 'cancelled'
    GROUP BY cp.customer_id
    LIMIT 5
''').fetchall()

print("   Sample (first 5 customers):")
for cust_id, prof_clv, ord_clv in orders_based_clv:
    print(f"   {cust_id}: profile_clv=₹{prof_clv:.2f}, orders_clv=₹{ord_clv:.2f}")

# RFM-based estimation
print("\n   RFM-based CLV candidates:")
rfm_customers = c.execute('''
    SELECT 
        customer_id,
        clv,
        recency_days,
        frequency,
        monetary_value,
        churn_probability
    FROM customer_profiles
    WHERE clv = 0
    ORDER BY monetary_value DESC
    LIMIT 5
''').fetchall()

for row in rfm_customers:
    cust_id, clv, recency, freq, monetary, churn = row
    estimated_clv = monetary * (1 - churn) * 2  # Simple estimate
    print(f"   {cust_id}: monetary=₹{monetary:.2f}, estimated_clv=₹{estimated_clv:.2f}")

# Issue #3: Simulation formulas audit
print("\n3. CURRENT SIMULATION FORMULAS")
print("-" * 80)

sample_customer = c.execute('''
    SELECT customer_id, churn_probability, clv, trust_score, happiness_score
    FROM customer_profiles
    WHERE churn_probability > 0.5
    ORDER BY churn_probability DESC
    LIMIT 1
''').fetchone()

if sample_customer:
    cust_id, churn, clv, trust, happiness = sample_customer
    print(f"Sample Customer: {cust_id}")
    print(f"  Churn: {churn:.3f}")
    print(f"  CLV: ₹{clv:.2f}")
    print(f"  Trust: {trust:.1f}")
    print(f"  Happiness: {happiness:.1f}")
    
    # Current formula from backend
    print("\n  Current Backend Formula (from ai_router.py):")
    print(f"    No intervention:")
    print(f"      revenue_30d = {clv} × 0.3 × (1 - {churn}) = ₹{clv * 0.3 * (1 - churn):.2f}")
    print(f"      revenue_90d = {clv} × 0.7 × (1 - min(1, {churn} + 0.30)) = ₹{clv * 0.7 * (1 - min(1, churn + 0.30)):.2f}")
    
    print(f"\n    With intervention (rescue_factor=0.35):")
    rescue = 0.35
    print(f"      revenue_30d = {clv} × 0.4 × (1 - max(0, {churn} - {rescue})) = ₹{clv * 0.4 * (1 - max(0, churn - rescue)):.2f}")
    print(f"      revenue_90d = {clv} × 0.85 × (1 - max(0, {churn} - {rescue} × 0.3)) = ₹{clv * 0.85 * (1 - max(0, churn - rescue * 0.3)):.2f}")
    
    # Issue with zero CLV
    if clv == 0:
        print(f"\n  ⚠️ WARNING: CLV is 0 - all revenue projections will be 0!")
        # Calculate from orders
        orders_total = c.execute(
            'SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id = ? AND status != "cancelled"',
            (cust_id,)
        ).fetchone()[0]
        print(f"  Alternative: Use orders total = ₹{orders_total:.2f}")

# Issue #4: Churn source verification
print("\n4. CHURN PROBABILITY SOURCE")
print("-" * 80)

churn_distribution = c.execute('''
    SELECT 
        CASE
            WHEN churn_probability < 0.3 THEN 'Low (<0.3)'
            WHEN churn_probability < 0.6 THEN 'Medium (0.3-0.6)'
            WHEN churn_probability < 0.8 THEN 'High (0.6-0.8)'
            ELSE 'Critical (>0.8)'
        END as risk_level,
        COUNT(*) as count
    FROM customer_profiles
    GROUP BY risk_level
    ORDER BY MIN(churn_probability)
''').fetchall()

print("Distribution:")
for level, count in churn_distribution:
    print(f"  {level}: {count:,} customers")

# Issue #7: Customer sorting recommendations
print("\n7. RECOMMENDED CUSTOMER SORTING")
print("-" * 80)

print("\nTop 10 by High Risk + High CLV (monetary_value):")
top_risk_value = c.execute('''
    SELECT 
        customer_id,
        churn_probability,
        CASE WHEN clv > 0 THEN clv ELSE monetary_value END as value,
        trust_score,
        recency_days
    FROM customer_profiles
    ORDER BY churn_probability DESC, monetary_value DESC
    LIMIT 10
''').fetchall()

for i, (cust_id, churn, value, trust, recency) in enumerate(top_risk_value, 1):
    print(f"  {i}. {cust_id}: churn={churn:.3f}, value=₹{value:.2f}, trust={trust:.1f}, recency={recency}d")

print("\nTop 10 by Monetary Value:")
top_value = c.execute('''
    SELECT 
        customer_id,
        monetary_value,
        churn_probability,
        frequency,
        recency_days
    FROM customer_profiles
    ORDER BY monetary_value DESC
    LIMIT 10
''').fetchall()

for i, (cust_id, monetary, churn, freq, recency) in enumerate(top_value, 1):
    print(f"  {i}. {cust_id}: monetary=₹{monetary:.2f}, churn={churn:.3f}, orders={freq}, recency={recency}d")

# Issue #6: Simulation drivers
print("\n6. SIMULATION DRIVER DATA AVAILABILITY")
print("-" * 80)

drivers_sample = c.execute('''
    SELECT 
        cp.customer_id,
        cp.churn_probability,
        cp.trust_score,
        cp.happiness_score,
        cp.recency_days,
        cp.engagement_score,
        COUNT(DISTINCT e.event_id) as event_count,
        COUNT(DISTINCT CASE WHEN e.event_type LIKE '%campaign%' THEN e.event_id END) as campaign_events,
        COUNT(DISTINCT CASE WHEN e.event_type = 'complaint' THEN e.event_id END) as complaints
    FROM customer_profiles cp
    LEFT JOIN events e ON cp.customer_id = e.customer_id
    GROUP BY cp.customer_id
    ORDER BY cp.churn_probability DESC
    LIMIT 5
''').fetchall()

print("Sample drivers for top 5 high-risk customers:")
print("  customer_id | churn | trust | happiness | recency | engagement | events | campaigns | complaints")
print("  " + "-" * 100)
for row in drivers_sample:
    print(f"  {row[0]} | {row[1]:.3f} | {row[2]:.1f} | {row[3]:.1f} | {row[4]}d | {row[5]:.1f} | {row[6]} | {row[7]} | {row[8]}")

# Issue #9: Hardcoded constants audit
print("\n9. HARDCODED CONSTANTS IN SIMULATION")
print("-" * 80)

print("Constants found in backend/app/routers/ai_router.py simulate_twin():")
print("  • Default CLV fallback: 1000 (line 316: clv = profile.clv or 1000)")
print("  • No intervention multipliers: 0.3, 0.5, 0.7 (for 30d, 60d, 90d)")
print("  • Churn acceleration: +0.15, +0.30, +0.40")
print("  • Trust decline: -15")
print("  • Retention decline: -0.2")
print("  • Rescue factor: 0.35")
print("  • Intervention multipliers: 0.4, 0.65, 0.85")
print("  • Trust improvement: +10")
print("  • Retention improvement: +0.35")

print("\n⚠️ All revenue calculations depend on CLV, which is 0 for most customers!")

# Summary
print("\n" + "=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)

issues = []
if clv_stats[1] / clv_stats[0] < 0.1:
    issues.append(f"❌ {(clv_stats[0]-clv_stats[1])/clv_stats[0]*100:.1f}% of customers have CLV=0")

if clv_stats[1] == 0:
    issues.append("❌ ALL customers have CLV=0 - simulations will show ₹0 revenue")

issues.append("⚠️ Backend uses hardcoded fallback CLV=1000 (not from database)")
issues.append("⚠️ No API endpoint found for fetching customer list for Digital Twin")
issues.append("⚠️ Simulation formulas use fixed multipliers (not personalized)")

print("\nISSUES FOUND:")
for issue in issues:
    print(f"  {issue}")

print("\nRECOMMENDATIONS:")
print("  1. Create /digital-twin/customers endpoint with sorting")
print("  2. Implement 3-tier CLV fallback (profile → orders → RFM)")
print("  3. Add simulation drivers panel with real data")
print("  4. Personalize simulation multipliers based on customer segment")
print("  5. Add validation report endpoint")

conn.close()
