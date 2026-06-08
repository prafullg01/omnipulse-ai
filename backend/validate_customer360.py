"""
OMNIPULSE AI - VALIDATE CUSTOMER 360
Verify that customer_profiles has all required Customer 360 attributes
"""
import pandas as pd
from sqlalchemy import create_engine, text
import json

DATABASE_URL = "sqlite:///omnipulse.db"
engine = create_engine(DATABASE_URL)

print("="*80)
print("OMNIPULSE AI - CUSTOMER 360 VALIDATION")
print("="*80)

# ============================================================================
# CHECK 1: Column Schema
# ============================================================================
print("\n[CHECK 1] Verifying column schema...")
print("-"*80)

required_columns = [
    # Basic Customer Info
    'customer_id', 'customer_name', 'age', 'gender', 'city', 'state', 'income',
    # Order Metrics
    'total_orders', 'total_revenue', 'average_order_value', 'days_since_last_order',
    # Intelligence Metrics
    'trust_score', 'churn_probability', 'happiness_score', 'engagement_score',
    'risk_score', 'clv', 'predicted_clv', 'competitive_risk',
    # Segmentation
    'persona', 'emotion', 'segment', 'journey_stage',
    # Additional
    'favorite_category', 'favorite_product', 'nba_action', 'last_interaction',
    # RFM
    'recency_days', 'frequency', 'monetary'
]

# Get actual columns
columns_query = text("PRAGMA table_info(customer_profiles)")
columns_df = pd.read_sql(columns_query, engine)
actual_columns = columns_df['name'].tolist()

print(f"  Required columns: {len(required_columns)}")
print(f"  Actual columns: {len(actual_columns)}")

missing_columns = [col for col in required_columns if col not in actual_columns]
extra_columns = [col for col in actual_columns if col not in required_columns]

if missing_columns:
    print(f"\n  [WARNING] Missing columns: {', '.join(missing_columns)}")
else:
    print(f"\n  [OK] All required columns present")

if extra_columns:
    print(f"  [INFO] Extra columns: {', '.join(extra_columns)}")

# ============================================================================
# CHECK 2: Data Population
# ============================================================================
print("\n[CHECK 2] Checking data population...")
print("-"*80)

# Count profiles
profile_count = pd.read_sql(text("SELECT COUNT(*) as count FROM customer_profiles"), engine)
total_profiles = profile_count['count'][0]
print(f"  Total profiles: {total_profiles}")

# Check NULL counts for key fields
null_check_query = text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) as null_names,
        SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) as null_ages,
        SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as null_genders,
        SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) as null_cities,
        SUM(CASE WHEN income IS NULL THEN 1 ELSE 0 END) as null_incomes,
        SUM(CASE WHEN total_orders IS NULL THEN 1 ELSE 0 END) as null_orders,
        SUM(CASE WHEN total_revenue IS NULL THEN 1 ELSE 0 END) as null_revenue,
        SUM(CASE WHEN nba_action IS NULL THEN 1 ELSE 0 END) as null_nba,
        SUM(CASE WHEN persona IS NULL THEN 1 ELSE 0 END) as null_persona,
        SUM(CASE WHEN emotion IS NULL THEN 1 ELSE 0 END) as null_emotion,
        SUM(CASE WHEN segment IS NULL THEN 1 ELSE 0 END) as null_segment
    FROM customer_profiles
""")

null_check = pd.read_sql(null_check_query, engine).iloc[0]

print("\n  NULL Value Analysis:")
null_fields = [
    ('Customer Name', null_check['null_names']),
    ('Age', null_check['null_ages']),
    ('Gender', null_check['null_genders']),
    ('City', null_check['null_cities']),
    ('Income', null_check['null_incomes']),
    ('Total Orders', null_check['null_orders']),
    ('Total Revenue', null_check['null_revenue']),
    ('NBA Action', null_check['null_nba']),
    ('Persona', null_check['null_persona']),
    ('Emotion', null_check['null_emotion']),
    ('Segment', null_check['null_segment']),
]

all_populated = True
for field_name, null_count in null_fields:
    status = "[OK]" if null_count == 0 else "[WARN]"
    percentage = (null_count / total_profiles * 100) if total_profiles > 0 else 0
    print(f"    {status} {field_name:20} {null_count:>5} nulls ({percentage:>5.1f}%)")
    if null_count > 0:
        all_populated = False

# ============================================================================
# CHECK 3: Sample Data Inspection
# ============================================================================
print("\n[CHECK 3] Sample Customer 360 records...")
print("-"*80)

sample_query = text("""
    SELECT 
        customer_name, age, gender, city, state, income,
        total_orders, total_revenue, average_order_value, days_since_last_order,
        trust_score, churn_probability, happiness_score, engagement_score,
        persona, emotion, segment, journey_stage,
        nba_action
    FROM customer_profiles 
    WHERE customer_name IS NOT NULL
    ORDER BY total_revenue DESC
    LIMIT 3
""")

samples = pd.read_sql(sample_query, engine)

for idx, profile in samples.iterrows():
    print(f"\n  Sample {idx + 1}:")
    print(f"    Name: {profile['customer_name']}")
    print(f"    Demographics: {profile['age']} years, {profile['gender']}, {profile['city']}, {profile['state']}")
    print(f"    Income: ₹{profile['income']:,.2f}")
    print(f"    Orders: {profile['total_orders']}, Revenue: ₹{profile['total_revenue']:,.2f}, AOV: ₹{profile['average_order_value']:,.2f}")
    print(f"    Days Since Last Order: {profile['days_since_last_order']}")
    print(f"    Intelligence: Trust={profile['trust_score']:.1f}, Churn={profile['churn_probability']:.2f}, Happiness={profile['happiness_score']:.1f}, Engagement={profile['engagement_score']:.1f}")
    print(f"    Segmentation: {profile['persona']}, {profile['emotion']}, {profile['segment']}, {profile['journey_stage']}")
    print(f"    NBA: {profile['nba_action'][:80]}...")

# ============================================================================
# CHECK 4: Distribution Analysis
# ============================================================================
print("\n[CHECK 4] Distribution analysis...")
print("-"*80)

# Order distribution
order_dist = pd.read_sql(text("""
    SELECT 
        CASE 
            WHEN total_orders = 0 THEN 'No Orders'
            WHEN total_orders = 1 THEN '1 Order'
            WHEN total_orders <= 3 THEN '2-3 Orders'
            WHEN total_orders <= 5 THEN '4-5 Orders'
            ELSE '6+ Orders'
        END as order_range,
        COUNT(*) as count
    FROM customer_profiles
    GROUP BY order_range
    ORDER BY 
        CASE order_range
            WHEN 'No Orders' THEN 1
            WHEN '1 Order' THEN 2
            WHEN '2-3 Orders' THEN 3
            WHEN '4-5 Orders' THEN 4
            ELSE 5
        END
"""), engine)

print("\n  Order Distribution:")
for _, row in order_dist.iterrows():
    percentage = (row['count'] / total_profiles * 100) if total_profiles > 0 else 0
    print(f"    {row['order_range']:15} {row['count']:>5} ({percentage:>5.1f}%)")

# Revenue distribution
revenue_dist = pd.read_sql(text("""
    SELECT 
        CASE 
            WHEN total_revenue = 0 THEN '₹0'
            WHEN total_revenue < 1000 THEN '< ₹1K'
            WHEN total_revenue < 5000 THEN '₹1K-5K'
            WHEN total_revenue < 10000 THEN '₹5K-10K'
            ELSE '> ₹10K'
        END as revenue_range,
        COUNT(*) as count
    FROM customer_profiles
    GROUP BY revenue_range
    ORDER BY 
        CASE revenue_range
            WHEN '₹0' THEN 1
            WHEN '< ₹1K' THEN 2
            WHEN '₹1K-5K' THEN 3
            WHEN '₹5K-10K' THEN 4
            ELSE 5
        END
"""), engine)

print("\n  Revenue Distribution:")
for _, row in revenue_dist.iterrows():
    percentage = (row['count'] / total_profiles * 100) if total_profiles > 0 else 0
    print(f"    {row['revenue_range']:15} {row['count']:>5} ({percentage:>5.1f}%)")

# ============================================================================
# CHECK 5: API Compatibility
# ============================================================================
print("\n[CHECK 5] API compatibility check...")
print("-"*80)

# Test query that simulates what API would return
api_query = text("""
    SELECT 
        customer_id,
        customer_name as name,
        age,
        gender,
        city,
        state,
        income,
        total_orders,
        total_revenue,
        average_order_value,
        trust_score,
        churn_probability,
        happiness_score,
        persona,
        emotion,
        segment,
        journey_stage,
        nba_action
    FROM customer_profiles 
    LIMIT 1
""")

api_test = pd.read_sql(api_query, engine)

if len(api_test) > 0:
    print("  [OK] API query successful")
    print(f"  Sample API response fields: {list(api_test.columns)}")
else:
    print("  [ERROR] API query failed")

# ============================================================================
# FINAL VALIDATION RESULT
# ============================================================================
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

validation_results = {
    'total_profiles': int(total_profiles),
    'required_columns_present': len(missing_columns) == 0,
    'all_fields_populated': all_populated,
    'api_compatible': len(api_test) > 0,
    'missing_columns': missing_columns,
    'null_counts': {field: int(count) for field, count in null_fields}
}

print(f"\n  Total Profiles: {validation_results['total_profiles']}")
print(f"  Schema Complete: {'✓ YES' if validation_results['required_columns_present'] else '✗ NO'}")
print(f"  All Fields Populated: {'✓ YES' if validation_results['all_fields_populated'] else '~ PARTIAL'}")
print(f"  API Compatible: {'✓ YES' if validation_results['api_compatible'] else '✗ NO'}")

if validation_results['required_columns_present'] and validation_results['api_compatible']:
    print(f"\n  [SUCCESS] Customer 360 is ready for use!")
    print(f"  - customer_profiles has {len(actual_columns)} columns")
    print(f"  - {total_profiles} customer profiles available")
    print(f"  - API endpoints will return complete Customer 360 data")
else:
    print(f"\n  [WARNING] Some issues need attention")

# Save validation report
with open('customer360_validation_report.json', 'w') as f:
    json.dump(validation_results, f, indent=2)

print(f"\n  Report saved: customer360_validation_report.json")

print("\n" + "="*80)
