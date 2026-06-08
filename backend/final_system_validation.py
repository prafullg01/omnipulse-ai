"""
OMNIPULSE AI - FINAL SYSTEM VALIDATION
Generate comprehensive report with exact counts and dashboard status
"""
import pandas as pd
from sqlalchemy import create_engine, text
import json
from datetime import datetime

DATABASE_URL = "sqlite:///omnipulse.db"
engine = create_engine(DATABASE_URL)

print("="*80)
print("OMNIPULSE AI - FINAL SYSTEM VALIDATION REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# ============================================================================
# DATABASE COUNTS
# ============================================================================
print("\n" + "="*80)
print("DATABASE COUNTS")
print("="*80)

counts_queries = {
    'Customer Count': "SELECT COUNT(*) FROM customers WHERE role='customer'",
    'Customer Profile Count': "SELECT COUNT(*) FROM customer_profiles",
    'Journey Count': "SELECT COUNT(*) FROM journeys",
    'NBA Decision Count': "SELECT COUNT(*) FROM nba_decisions",
    'Campaign Count': "SELECT COUNT(*) FROM campaigns",
    'Campaign Response Count': "SELECT COUNT(*) FROM campaign_responses",
    'Order Count': "SELECT COUNT(*) FROM orders",
    'Order Item Count': "SELECT COUNT(*) FROM order_items",
    'Event Count': "SELECT COUNT(*) FROM events",
    'Product Count': "SELECT COUNT(*) FROM products",
    'Support Ticket Count': "SELECT COUNT(*) FROM support_tickets",
    'Message Count': "SELECT COUNT(*) FROM messages"
}

for label, query in counts_queries.items():
    result = pd.read_sql(text(query), engine)
    count = result.iloc[0, 0]
    status = "OK" if count > 0 else "EMPTY"
    print(f"  [{status:5}] {label:30} {count:>8,}")

# ============================================================================
# CHURN DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("CHURN DISTRIBUTION")
print("="*80)

churn_dist = pd.read_sql(text("""
    SELECT 
        CASE 
            WHEN churn_probability < 0.3 THEN 'Low Risk'
            WHEN churn_probability < 0.6 THEN 'Medium Risk'
            WHEN churn_probability < 0.75 THEN 'High Risk'
            ELSE 'Critical Risk'
        END as risk_level,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY risk_level
    ORDER BY 
        CASE risk_level
            WHEN 'Low Risk' THEN 1
            WHEN 'Medium Risk' THEN 2
            WHEN 'High Risk' THEN 3
            WHEN 'Critical Risk' THEN 4
        END
"""), engine)

print(f"\n  {'Risk Level':<20} {'Count':>8}  {'Percentage':>10}")
print("  " + "-"*42)
for _, row in churn_dist.iterrows():
    print(f"  {row['risk_level']:<20} {row['count']:>8,}  {row['percentage']:>9.1f}%")

# ============================================================================
# EMOTION DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("EMOTION DISTRIBUTION")
print("="*80)

emotion_dist = pd.read_sql(text("""
    SELECT emotion, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY emotion
    ORDER BY count DESC
"""), engine)

print(f"\n  {'Emotion':<20} {'Count':>8}  {'Percentage':>10}")
print("  " + "-"*42)
for _, row in emotion_dist.iterrows():
    print(f"  {row['emotion'].capitalize():<20} {row['count']:>8,}  {row['percentage']:>9.1f}%")

# ============================================================================
# TRUST DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("TRUST DISTRIBUTION")
print("="*80)

trust_dist = pd.read_sql(text("""
    SELECT 
        CASE 
            WHEN trust_score < 40 THEN 'Low Trust'
            WHEN trust_score < 70 THEN 'Medium Trust'
            ELSE 'High Trust'
        END as trust_level,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY trust_level
    ORDER BY 
        CASE trust_level
            WHEN 'Low Trust' THEN 1
            WHEN 'Medium Trust' THEN 2
            WHEN 'High Trust' THEN 3
        END
"""), engine)

print(f"\n  {'Trust Level':<20} {'Count':>8}  {'Percentage':>10}")
print("  " + "-"*42)
for _, row in trust_dist.iterrows():
    print(f"  {row['trust_level']:<20} {row['count']:>8,}  {row['percentage']:>9.1f}%")

# ============================================================================
# PERSONA DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("PERSONA DISTRIBUTION")
print("="*80)

persona_dist = pd.read_sql(text("""
    SELECT persona, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY persona
    ORDER BY count DESC
"""), engine)

print(f"\n  {'Persona':<20} {'Count':>8}  {'Percentage':>10}")
print("  " + "-"*42)
for _, row in persona_dist.iterrows():
    print(f"  {row['persona']:<20} {row['count']:>8,}  {row['percentage']:>9.1f}%")

# ============================================================================
# SEGMENT DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("SEGMENT DISTRIBUTION")
print("="*80)

segment_dist = pd.read_sql(text("""
    SELECT segment, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY segment
    ORDER BY count DESC
"""), engine)

print(f"\n  {'Segment':<20} {'Count':>8}  {'Percentage':>10}")
print("  " + "-"*42)
for _, row in segment_dist.iterrows():
    print(f"  {row['segment']:<20} {row['count']:>8,}  {row['percentage']:>9.1f}%")

# ============================================================================
# JOURNEY DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("JOURNEY STAGE DISTRIBUTION")
print("="*80)

journey_dist = pd.read_sql(text("""
    SELECT journey_stage, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY journey_stage
    ORDER BY count DESC
"""), engine)

print(f"\n  {'Journey Stage':<20} {'Count':>8}  {'Percentage':>10}")
print("  " + "-"*42)
for _, row in journey_dist.iterrows():
    print(f"  {row['journey_stage'].capitalize():<20} {row['count']:>8,}  {row['percentage']:>9.1f}%")

# ============================================================================
# CAMPAIGN METRICS
# ============================================================================
print("\n" + "="*80)
print("CAMPAIGN METRICS")
print("="*80)

campaign_metrics = pd.read_sql(text("""
    SELECT 
        c.campaign_name,
        COUNT(cr.response_id) as total_sent,
        SUM(CASE WHEN cr.opened THEN 1 ELSE 0 END) as opened,
        SUM(CASE WHEN cr.clicked THEN 1 ELSE 0 END) as clicked,
        SUM(CASE WHEN cr.converted THEN 1 ELSE 0 END) as converted,
        ROUND(SUM(cr.revenue), 2) as total_revenue,
        ROUND(SUM(CASE WHEN cr.opened THEN 1 ELSE 0 END) * 100.0 / COUNT(cr.response_id), 1) as open_rate,
        ROUND(SUM(CASE WHEN cr.clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(cr.response_id), 1) as click_rate,
        ROUND(SUM(CASE WHEN cr.converted THEN 1 ELSE 0 END) * 100.0 / COUNT(cr.response_id), 1) as conversion_rate
    FROM campaigns c
    LEFT JOIN campaign_responses cr ON c.campaign_id = cr.campaign_id
    GROUP BY c.campaign_id, c.campaign_name
"""), engine)

if len(campaign_metrics) > 0:
    print(f"\n  {'Campaign':<30} {'Sent':>8} {'Opened':>8} {'Clicked':>8} {'Converted':>8} {'Revenue':>12}")
    print("  " + "-"*90)
    for _, row in campaign_metrics.iterrows():
        print(f"  {row['campaign_name'][:28]:<30} {int(row['total_sent']):>8} {int(row['opened']):>8} {int(row['clicked']):>8} {int(row['converted']):>8} ${row['total_revenue']:>10,.2f}")
    
    print(f"\n  Campaign Performance:")
    for _, row in campaign_metrics.iterrows():
        print(f"    {row['campaign_name']}: Open Rate {row['open_rate']}%, Click Rate {row['click_rate']}%, Conversion {row['conversion_rate']}%")
else:
    print("\n  [WARNING] No campaigns found")

# ============================================================================
# NBA RECOMMENDATIONS SUMMARY
# ============================================================================
print("\n" + "="*80)
print("NBA RECOMMENDATIONS SUMMARY")
print("="*80)

nba_summary = pd.read_sql(text("""
    SELECT 
        recommended_action,
        COUNT(*) as count,
        ROUND(AVG(confidence), 2) as avg_confidence
    FROM nba_decisions
    GROUP BY recommended_action
    ORDER BY count DESC
"""), engine)

if len(nba_summary) > 0:
    print(f"\n  {'Recommended Action':<30} {'Count':>8}  {'Avg Confidence':>15}")
    print("  " + "-"*58)
    for _, row in nba_summary.iterrows():
        print(f"  {row['recommended_action']:<30} {row['count']:>8,}  {row['avg_confidence']:>14.2f}")
else:
    print("\n  [WARNING] No NBA decisions found")

# ============================================================================
# DASHBOARD STATUS MATRIX
# ============================================================================
print("\n" + "="*80)
print("DASHBOARD STATUS MATRIX")
print("="*80)

# Check each dashboard module
dashboards = {
    'Churn Center': {
        'criteria': 'customer_profiles with churn_probability',
        'query': "SELECT COUNT(*) FROM customer_profiles WHERE churn_probability IS NOT NULL",
        'threshold': 5000
    },
    'Emotion Center': {
        'criteria': 'customer_profiles with emotion',
        'query': "SELECT COUNT(*) FROM customer_profiles WHERE emotion IS NOT NULL",
        'threshold': 5000
    },
    'Trust Center': {
        'criteria': 'customer_profiles with trust_score',
        'query': "SELECT COUNT(*) FROM customer_profiles WHERE trust_score IS NOT NULL",
        'threshold': 5000
    },
    'NBA Center': {
        'criteria': 'nba_decisions with recommendations',
        'query': "SELECT COUNT(*) FROM nba_decisions",
        'threshold': 5000
    },
    'Campaign Builder': {
        'criteria': 'campaigns created',
        'query': "SELECT COUNT(*) FROM campaigns",
        'threshold': 1
    },
    'ROI Center': {
        'criteria': 'campaign_responses with revenue',
        'query': "SELECT COUNT(*) FROM campaign_responses WHERE revenue > 0",
        'threshold': 1
    },
    'Customer 360': {
        'criteria': 'customer_profiles complete',
        'query': "SELECT COUNT(*) FROM customer_profiles WHERE persona IS NOT NULL",
        'threshold': 5000
    },
    'Journey Engine': {
        'criteria': 'journeys created',
        'query': "SELECT COUNT(*) FROM journeys",
        'threshold': 100
    },
    'Analytics Engine': {
        'criteria': 'orders and events',
        'query': "SELECT COUNT(*) FROM orders WHERE status != 'cancelled'",
        'threshold': 1000
    }
}

print(f"\n  {'Dashboard Module':<25} {'Status':>10}  {'Data Source':<40}")
print("  " + "-"*80)

for module, config in dashboards.items():
    result = pd.read_sql(text(config['query']), engine)
    count = result.iloc[0, 0]
    
    if count >= config['threshold']:
        status = "GREEN"
        symbol = "✓"
    elif count > 0:
        status = "YELLOW"
        symbol = "~"
    else:
        status = "RED"
        symbol = "X"
    
    print(f"  {module:<25} [{status:>6}]  {config['criteria']:<40}")

# ============================================================================
# DATA QUALITY METRICS
# ============================================================================
print("\n" + "="*80)
print("DATA QUALITY METRICS")
print("="*80)

# Check for NULL values in critical fields
quality_checks = {
    'Customers with orders': "SELECT COUNT(DISTINCT customer_id) FROM orders",
    'Customers with events': "SELECT COUNT(DISTINCT customer_id) FROM events",
    'Customers with profiles': "SELECT COUNT(*) FROM customer_profiles",
    'Orders with items': "SELECT COUNT(DISTINCT order_id) FROM order_items",
    'Campaigns with responses': "SELECT COUNT(DISTINCT campaign_id) FROM campaign_responses",
    'NBA decisions active': "SELECT COUNT(*) FROM nba_decisions WHERE status='pending'"
}

print(f"\n  {'Metric':<35} {'Count':>10}")
print("  " + "-"*48)

for metric, query in quality_checks.items():
    result = pd.read_sql(text(query), engine)
    count = result.iloc[0, 0]
    print(f"  {metric:<35} {count:>10,}")

# ============================================================================
# SYSTEM HEALTH SUMMARY
# ============================================================================
print("\n" + "="*80)
print("SYSTEM HEALTH SUMMARY")
print("="*80)

# Calculate overall system health
customer_count = pd.read_sql(text("SELECT COUNT(*) FROM customers WHERE role='customer'"), engine).iloc[0, 0]
profile_count = pd.read_sql(text("SELECT COUNT(*) FROM customer_profiles"), engine).iloc[0, 0]
nba_count = pd.read_sql(text("SELECT COUNT(*) FROM nba_decisions"), engine).iloc[0, 0]
campaign_count = pd.read_sql(text("SELECT COUNT(*) FROM campaigns"), engine).iloc[0, 0]
journey_count = pd.read_sql(text("SELECT COUNT(*) FROM journeys"), engine).iloc[0, 0]

profile_coverage = (profile_count / customer_count * 100) if customer_count > 0 else 0
nba_coverage = (nba_count / customer_count * 100) if customer_count > 0 else 0

print(f"\n  Total Customers:              {customer_count:>8,}")
print(f"  Profile Coverage:             {profile_coverage:>7.1f}%")
print(f"  NBA Coverage:                 {nba_coverage:>7.1f}%")
print(f"  Active Campaigns:             {campaign_count:>8,}")
print(f"  Active Journeys:              {journey_count:>8,}")

# Overall status
if profile_coverage >= 95 and nba_coverage >= 95 and campaign_count >= 5:
    overall_status = "OPERATIONAL"
    symbol = "OK"
elif profile_coverage >= 80 and campaign_count >= 1:
    overall_status = "FUNCTIONAL"
    symbol = "~"
else:
    overall_status = "INCOMPLETE"
    symbol = "X"

print(f"\n  Overall System Status:        [{symbol}] {overall_status}")

print("\n" + "="*80)
print("END OF VALIDATION REPORT")
print("="*80)

# Save report to file
report_data = {
    'generated_at': datetime.now().isoformat(),
    'counts': {label: int(pd.read_sql(text(query), engine).iloc[0, 0]) for label, query in counts_queries.items()},
    'distributions': {
        'churn': churn_dist.to_dict('records'),
        'emotion': emotion_dist.to_dict('records'),
        'trust': trust_dist.to_dict('records'),
        'persona': persona_dist.to_dict('records'),
        'segment': segment_dist.to_dict('records'),
        'journey': journey_dist.to_dict('records')
    },
    'system_health': {
        'total_customers': int(customer_count),
        'profile_coverage': float(profile_coverage),
        'nba_coverage': float(nba_coverage),
        'campaign_count': int(campaign_count),
        'journey_count': int(journey_count),
        'overall_status': overall_status
    }
}

with open('system_validation_report.json', 'w') as f:
    json.dump(report_data, f, indent=2)

print("\n[REPORT SAVED] system_validation_report.json")
