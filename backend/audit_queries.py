"""Quick database audit queries for production verification"""
import sqlite3

conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()

print("=" * 80)
print("ISSUE #1: REVENUE AT RISK VS POTENTIAL REVENUE LOSS")
print("=" * 80)

# High-risk customer count
high_risk = c.execute('SELECT COUNT(*) FROM customer_profiles WHERE churn_probability > 0.7').fetchone()[0]
print(f'\n1. High-risk customers (churn > 0.7): {high_risk:,}')

# Get high-risk IDs
high_risk_ids = [r[0] for r in c.execute('SELECT customer_id FROM customer_profiles WHERE churn_probability > 0.7').fetchall()]

# Revenue from high-risk customers who have orders
placeholders = ','.join(['?'] * len(high_risk_ids))
revenue_historical = c.execute(
    f'SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id IN ({placeholders}) AND status != "cancelled"',
    high_risk_ids
).fetchone()[0]
print(f'2. Historical revenue from high-risk: ₹{revenue_historical:,.2f}')

# Average order value
avg_order = c.execute('SELECT AVG(total_amount) FROM orders WHERE status != "cancelled"').fetchone()[0]
print(f'3. Average order value: ₹{avg_order:,.2f}')

# High-risk non-purchasers
all_customer_ids_with_orders = set(r[0] for r in c.execute('SELECT DISTINCT customer_id FROM orders').fetchall())
high_risk_non_purchasers = len([cid for cid in high_risk_ids if cid not in all_customer_ids_with_orders])
print(f'4. High-risk non-purchasers: {high_risk_non_purchasers:,}')

# Potential revenue at risk
potential_rar = high_risk_non_purchasers * avg_order
print(f'5. Potential revenue (non-purchasers × avg): ₹{potential_rar:,.2f}')

# TOTAL Revenue At Risk
total_rar = revenue_historical + potential_rar
print(f'\n>>> REVENUE AT RISK (backend formula): ₹{total_rar:,.2f}')
print(f'    = ₹{revenue_historical:,.2f} (historical) + ₹{potential_rar:,.2f} (potential)')

# Potential Revenue Loss
potential_loss = high_risk * avg_order
print(f'\n>>> POTENTIAL REVENUE LOSS (backend formula): ₹{potential_loss:,.2f}')
print(f'    = {high_risk:,} (high-risk count) × ₹{avg_order:,.2f} (avg order)')

print(f'\n>>> ARE THEY THE SAME? {total_rar == potential_loss}')
print(f'>>> DIFFERENCE: ₹{abs(total_rar - potential_loss):,.2f}')

print("\n" + "=" * 80)
print("ISSUE #2: HIGH-RISK CUSTOMER VERIFICATION")
print("=" * 80)

# Verify non-purchaser status
high_risk_with_orders = len([cid for cid in high_risk_ids if cid in all_customer_ids_with_orders])
print(f'\nHigh-risk WITH orders: {high_risk_with_orders:,}')
print(f'High-risk WITHOUT orders: {high_risk_non_purchasers:,}')
print(f'Total high-risk: {high_risk:,}')

# Check CLV and predicted_clv
clv_data = c.execute(
    f'SELECT COUNT(*), SUM(clv), AVG(clv), MAX(clv) FROM customer_profiles WHERE customer_id IN ({placeholders})',
    high_risk_ids
).fetchone()
print(f'\nCLV for high-risk customers:')
print(f'  Count with data: {clv_data[0]:,}')
print(f'  Sum: ₹{clv_data[1] or 0:,.2f}')
print(f'  Avg: ₹{clv_data[2] or 0:,.2f}')
print(f'  Max: ₹{clv_data[3] or 0:,.2f}')

print("\n" + "=" * 80)
print("ISSUE #3: CAMPAIGN REVENUE ATTRIBUTION")
print("=" * 80)

# Direct campaign response revenue
campaign_resp_revenue = c.execute(
    'SELECT COALESCE(SUM(revenue), 0) FROM campaign_responses WHERE converted = 1'
).fetchone()[0]
print(f'\n1. Campaign Response Revenue (converted=True): ₹{campaign_resp_revenue:,.2f}')

# Campaign-influenced customers
campaign_events = ['campaign_received', 'campaign_opened', 'offer_clicked']
campaign_customer_ids = set(
    r[0] for r in c.execute(
        'SELECT DISTINCT customer_id FROM events WHERE event_type IN (?, ?, ?)',
        campaign_events
    ).fetchall()
)
print(f'2. Customers with campaign interactions: {len(campaign_customer_ids):,}')

# Revenue from campaign-influenced customers
if campaign_customer_ids:
    placeholders2 = ','.join(['?'] * len(campaign_customer_ids))
    campaign_influenced_revenue = c.execute(
        f'SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id IN ({placeholders2}) AND status != "cancelled"',
        list(campaign_customer_ids)
    ).fetchone()[0]
    print(f'3. Revenue from campaign-influenced customers: ₹{campaign_influenced_revenue:,.2f}')
    
    final_campaign_revenue = max(campaign_resp_revenue, campaign_influenced_revenue)
    print(f'\n>>> FINAL CAMPAIGN REVENUE (max of both): ₹{final_campaign_revenue:,.2f}')
    print(f'>>> METHOD USED: {"Direct responses" if campaign_resp_revenue > campaign_influenced_revenue else "Campaign-influenced orders"}')
else:
    print('>>> FINAL CAMPAIGN REVENUE: ₹{campaign_resp_revenue:,.2f}')

print("\n" + "=" * 80)
print("ISSUE #6: CITY DATA CORRUPTION")
print("=" * 80)

# Check for binary/corrupted city values
total_customers = c.execute('SELECT COUNT(*) FROM customer_profiles').fetchone()[0]
print(f'\nTotal customer profiles: {total_customers:,}')

# Various corruption patterns
null_city = c.execute('SELECT COUNT(*) FROM customer_profiles WHERE city IS NULL OR city = ""').fetchone()[0]
short_city = c.execute('SELECT COUNT(*) FROM customer_profiles WHERE LENGTH(city) < 3').fetchone()[0]
binary_city = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE city LIKE 'b%' AND LENGTH(city) < 10").fetchone()[0]

print(f'NULL or empty city: {null_city:,}')
print(f'City length < 3 chars: {short_city:,}')
print(f'Suspected binary (starts with b, len<10): {binary_city:,}')

# Sample of actual city values
print('\nSample city values (first 20):')
cities = c.execute('SELECT DISTINCT city FROM customer_profiles LIMIT 20').fetchall()
for i, (city,) in enumerate(cities, 1):
    print(f'  {i}. {repr(city)}')

print("\n" + "=" * 80)
print("ISSUE #8: MODEL CONSISTENCY - CHURN THRESHOLDS")
print("=" * 80)

# Check various churn thresholds used in the system
thresholds = {
    'High Risk (>0.7)': c.execute('SELECT COUNT(*) FROM customer_profiles WHERE churn_probability > 0.7').fetchone()[0],
    'High Risk (>0.6)': c.execute('SELECT COUNT(*) FROM customer_profiles WHERE churn_probability > 0.6').fetchone()[0],
    'High Risk (>0.75)': c.execute('SELECT COUNT(*) FROM customer_profiles WHERE churn_probability > 0.75').fetchone()[0],
    'High Risk (>0.8)': c.execute('SELECT COUNT(*) FROM customer_profiles WHERE churn_probability > 0.8').fetchone()[0],
}

for label, count in thresholds.items():
    print(f'{label}: {count:,} customers')

print("\n" + "=" * 80)
print("FAIRNESS METRICS VERIFICATION")
print("=" * 80)

# Check NBA decisions for fairness calculation
nba_total = c.execute('SELECT COUNT(*) FROM nba_decisions').fetchone()[0]
print(f'\nTotal NBA decisions: {nba_total:,}')

# Gender distribution
gender_dist = c.execute('''
    SELECT cp.gender, COUNT(*) 
    FROM nba_decisions nd 
    JOIN customer_profiles cp ON nd.customer_id = cp.customer_id 
    GROUP BY cp.gender
''').fetchall()
print('\nGender distribution in NBA:')
for gender, count in gender_dist:
    print(f'  {gender}: {count:,} ({count/nba_total*100:.1f}%)')

# Age distribution
age_dist = c.execute('''
    SELECT cp.age_group, COUNT(*) 
    FROM nba_decisions nd 
    JOIN customer_profiles cp ON nd.customer_id = cp.customer_id 
    GROUP BY cp.age_group
''').fetchall()
print('\nAge distribution in NBA:')
for age, count in age_dist:
    print(f'  {age}: {count:,} ({count/nba_total*100:.1f}%)')

conn.close()
print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
