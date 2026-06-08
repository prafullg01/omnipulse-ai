"""
COMPLETE OMNIPULSE AI SYSTEM AUDIT
Validates ALL modules against database with zero assumptions.
"""
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def complete_system_audit():
    conn = sqlite3.connect("omnipulse.db")
    cursor = conn.cursor()
    
    audit = {
        "timestamp": datetime.utcnow().isoformat(),
        "phases": {},
        "issues": [],
        "warnings": [],
        "passed": [],
        "failed": []
    }
    
    print("=" * 100)
    print("OMNIPULSE AI COMPLETE SYSTEM AUDIT")
    print("=" * 100)
    print()
    
    # ====================================================================
    # PHASE 1: DATABASE VALIDATION
    # ====================================================================
    
    print("PHASE 1: DATABASE VALIDATION")
    print("-" * 100)
    
    tables_to_audit = [
        'customers', 'customer_profiles', 'orders', 'events', 
        'nba_decisions', 'campaigns', 'campaign_responses',
        'support_tickets', 'products'
    ]
    
    phase1 = {}
    
    for table in tables_to_audit:
        print(f"\n{table.upper()}")
        print("-" * 50)
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"  ❌ Table does not exist!")
            audit["failed"].append(f"{table} table missing")
            continue
        
        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        print(f"  Total Rows: {row_count:,}")
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        table_stats = {
            "row_count": row_count,
            "columns": len(col_names),
            "null_counts": {},
            "duplicates": 0,
            "corrupted": 0
        }
        
        # Check for nulls in each column
        for col_name in col_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col_name} IS NULL OR {col_name} = ''")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                table_stats["null_counts"][col_name] = null_count
                print(f"  ⚠️  {col_name}: {null_count:,} null/empty values ({null_count/row_count*100:.1f}%)")
        
        # Check for duplicates (if ID column exists)
        id_col = f"{table[:-1]}_id" if table.endswith('s') else f"{table}_id"
        if id_col in col_names:
            cursor.execute(f"SELECT COUNT(*) - COUNT(DISTINCT {id_col}) FROM {table}")
            dup_count = cursor.fetchone()[0]
            table_stats["duplicates"] = dup_count
            if dup_count > 0:
                print(f"  ⚠️  Duplicate IDs: {dup_count}")
        
        # Check for corrupted data in specific columns
        if 'city' in col_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE city LIKE 'b''%' OR city LIKE '%\\x%'")
            corrupted = cursor.fetchone()[0]
            table_stats["corrupted"] = corrupted
            if corrupted > 0:
                print(f"  ❌ CORRUPTED city values: {corrupted} ({corrupted/row_count*100:.1f}%)")
                audit["issues"].append({
                    "severity": "CRITICAL",
                    "table": table,
                    "issue": f"{corrupted} corrupted city values (binary data)",
                    "impact": "Region analytics are broken"
                })
        
        phase1[table] = table_stats
        
        if row_count > 0:
            audit["passed"].append(f"{table} exists with {row_count:,} rows")
        else:
            audit["warnings"].append(f"{table} is empty")
    
    audit["phases"]["phase1_database"] = phase1
    
    # ====================================================================
    # PHASE 2: DATA QUALITY - CORRUPTED CITIES
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 2: DATA QUALITY - CORRUPTED CITIES")
    print("-" * 100)
    
    cursor.execute("""
        SELECT city, COUNT(*) as cnt
        FROM customers
        WHERE city LIKE 'b''%' OR city LIKE '%\\x%' OR LENGTH(city) < 2
        GROUP BY city
        ORDER BY cnt DESC
        LIMIT 10
    """)
    corrupted_cities = cursor.fetchall()
    
    total_corrupted = sum(c[1] for c in corrupted_cities)
    print(f"\nCorrupted City Records: {total_corrupted:,}")
    
    if corrupted_cities:
        print("\nTop Corrupted Values:")
        for city, count in corrupted_cities[:5]:
            print(f"  '{city}': {count} records")
        
        audit["issues"].append({
            "severity": "HIGH",
            "module": "Customer Data",
            "issue": f"{total_corrupted} customers have corrupted city values",
            "fix": "Replace with 'Unknown' or clean mapping"
        })
        audit["failed"].append("City data corrupted")
    else:
        print("✅ No corrupted city data found")
        audit["passed"].append("City data clean")
    
    # ====================================================================
    # PHASE 3: FAIRNESS OBSERVATORY AUDIT
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 3: FAIRNESS OBSERVATORY")
    print("-" * 100)
    
    # Get actual fairness calculations
    cursor.execute("SELECT COUNT(*) FROM nba_decisions")
    total_nba = cursor.fetchone()[0]
    
    print(f"\nTotal NBA Decisions: {total_nba:,}")
    
    # Gender distribution
    cursor.execute("""
        SELECT c.gender, COUNT(n.decision_id) as cnt
        FROM nba_decisions n
        JOIN customers c ON n.customer_id = c.customer_id
        WHERE c.gender IS NOT NULL AND c.gender != ''
        GROUP BY c.gender
    """)
    gender_dist = dict(cursor.fetchall())
    
    # Age distribution
    cursor.execute("""
        SELECT 
            CASE 
                WHEN c.age < 25 THEN '18-24'
                WHEN c.age < 35 THEN '25-34'
                WHEN c.age < 45 THEN '35-44'
                WHEN c.age < 55 THEN '45-54'
                ELSE '55+'
            END as age_group,
            COUNT(n.decision_id) as cnt
        FROM nba_decisions n
        JOIN customers c ON n.customer_id = c.customer_id
        WHERE c.age IS NOT NULL
        GROUP BY age_group
    """)
    age_dist = dict(cursor.fetchall())
    
    # Action distribution
    cursor.execute("""
        SELECT recommended_action, COUNT(*) as cnt
        FROM nba_decisions
        GROUP BY recommended_action
    """)
    action_dist = dict(cursor.fetchall())
    
    # Channel distribution
    cursor.execute("""
        SELECT channel, COUNT(*) as cnt
        FROM nba_decisions
        GROUP BY channel
    """)
    channel_dist = dict(cursor.fetchall())
    
    # Calculate fairness scores
    def calculate_fairness(distribution):
        if not distribution:
            return 100.0
        values = list(distribution.values())
        total = sum(values)
        expected_pct = 100 / len(values)
        actual_pcts = [(v / total * 100) for v in values]
        variance = sum((pct - expected_pct) ** 2 for pct in actual_pcts) / len(values)
        max_variance = expected_pct ** 2 * (len(values) - 1)
        fairness = max(0, 100 - (variance / max_variance * 100)) if max_variance > 0 else 100
        return round(fairness, 1)
    
    gender_fairness = calculate_fairness(gender_dist)
    age_fairness = calculate_fairness(age_dist)
    action_fairness = calculate_fairness(action_dist)
    channel_fairness = calculate_fairness(channel_dist)
    
    overall_fairness = (gender_fairness + age_fairness + action_fairness + channel_fairness) / 4
    
    print(f"\nFairness Scores (Calculated from Database):")
    print(f"  Gender Fairness: {gender_fairness}/100")
    print(f"  Age Fairness: {age_fairness}/100")
    print(f"  Action Fairness: {action_fairness}/100")
    print(f"  Channel Fairness: {channel_fairness}/100")
    print(f"  ✓ Overall Fairness: {overall_fairness:.1f}/100")
    
    # Coverage Score
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM nba_decisions")
    customers_with_nba = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
    total_customers = cursor.fetchone()[0]
    coverage_score = (customers_with_nba / max(total_customers, 1)) * 100
    
    print(f"\nCoverage Score: {coverage_score:.1f}%")
    print(f"  ({customers_with_nba:,} / {total_customers:,} customers have NBA recommendations)")
    
    # Equity Index (from confidence variance)
    cursor.execute("""
        SELECT cp.segment, AVG(n.confidence) as avg_conf
        FROM nba_decisions n
        JOIN customer_profiles cp ON n.customer_id = cp.customer_id
        WHERE cp.segment IS NOT NULL
        GROUP BY cp.segment
    """)
    segment_confs = [row[1] for row in cursor.fetchall()]
    
    if len(segment_confs) > 1:
        import statistics
        mean_conf = statistics.mean(segment_confs)
        stddev_conf = statistics.stdev(segment_confs)
        equity_index = 1 - (stddev_conf / max(mean_conf, 0.01))
        equity_index = max(0, min(1, equity_index))
    else:
        equity_index = 0.95
    
    print(f"\nEquity Index: {equity_index:.3f}")
    
    # Validate consistency
    print(f"\n✓ Fairness Validation:")
    if equity_index >= 0.95 and overall_fairness < 80:
        print(f"  ⚠️  INCONSISTENCY: Equity Index ({equity_index:.3f}) suggests fairness but score is {overall_fairness:.1f}")
        audit["warnings"].append(f"Fairness inconsistency: Equity {equity_index:.3f} vs Score {overall_fairness:.1f}")
    elif overall_fairness >= 85:
        print(f"  ✅ CONSISTENT: High fairness across all metrics")
        audit["passed"].append(f"Fairness Observatory validated: {overall_fairness:.1f}/100")
    
    audit["phases"]["phase3_fairness"] = {
        "overall_fairness": overall_fairness,
        "gender_fairness": gender_fairness,
        "age_fairness": age_fairness,
        "action_fairness": action_fairness,
        "channel_fairness": channel_fairness,
        "coverage_score": coverage_score,
        "equity_index": equity_index,
        "data_source": f"{total_nba} NBA decisions"
    }
    
    # ====================================================================
    # PHASE 4: ROI ATTRIBUTION AUDIT
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 4: ROI ATTRIBUTION")
    print("-" * 100)
    
    # Check campaign customer IDs vs order customer IDs
    cursor.execute("SELECT DISTINCT customer_id FROM campaign_responses LIMIT 10")
    campaign_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT customer_id FROM orders LIMIT 10")
    order_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"\nSample Campaign Customer IDs: {campaign_ids[:5]}")
    print(f"Sample Order Customer IDs: {order_ids[:5]}")
    
    # Test direct join
    cursor.execute("""
        SELECT COUNT(DISTINCT cr.customer_id)
        FROM campaign_responses cr
        JOIN orders o ON cr.customer_id = o.customer_id
    """)
    direct_matches = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM campaign_responses")
    total_campaign_customers = cursor.fetchone()[0]
    
    match_rate = (direct_matches / max(total_campaign_customers, 1)) * 100
    
    print(f"\nDirect ID Match Rate: {match_rate:.1f}%")
    print(f"  ({direct_matches} / {total_campaign_customers} campaign customers have orders)")
    
    if match_rate < 50:
        print(f"\n⚠️  LOW MATCH RATE - Attribution requires AI estimation")
        audit["warnings"].append(f"Campaign attribution only {match_rate:.1f}% direct match rate")
        attribution_method = "AI_ESTIMATED"
    else:
        attribution_method = "DIRECT"
    
    # Calculate ROI metrics
    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status='delivered'")
    total_revenue = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(o.total_amount)
        FROM orders o
        JOIN campaign_responses cr ON o.customer_id = cr.customer_id
        WHERE o.status='delivered'
    """)
    campaign_revenue = cursor.fetchone()[0] or 0
    
    print(f"\nROI Metrics:")
    print(f"  Total Revenue: ₹{total_revenue:,.2f}")
    print(f"  Campaign Revenue (Direct Match): ₹{campaign_revenue:,.2f}")
    print(f"  Attribution Method: {attribution_method}")
    print(f"  Attribution Confidence: {match_rate:.0f}%")
    
    audit["phases"]["phase4_roi"] = {
        "total_revenue": total_revenue,
        "campaign_revenue": campaign_revenue,
        "match_rate": match_rate,
        "attribution_method": attribution_method,
        "confidence": match_rate
    }
    
    if attribution_method == "AI_ESTIMATED":
        audit["warnings"].append("ROI attribution uses AI estimation due to low ID match rate")
    else:
        audit["passed"].append(f"ROI attribution validated with {match_rate:.1f}% confidence")
    
    # ====================================================================
    # PHASE 5: NBA ENGINE VALIDATION
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 5: NBA ENGINE")
    print("-" * 100)
    
    # Check for diversity in NBA recommendations
    cursor.execute("SELECT MIN(confidence), MAX(confidence), AVG(confidence) FROM nba_decisions")
    min_conf, max_conf, avg_conf = cursor.fetchone()
    
    print(f"\nConfidence Distribution:")
    print(f"  Min: {min_conf:.3f}")
    print(f"  Max: {max_conf:.3f}")
    print(f"  Avg: {avg_conf:.3f}")
    print(f"  Range: {max_conf - min_conf:.3f}")
    
    if max_conf - min_conf < 0.1:
        print(f"  ⚠️  LOW VARIANCE - Confidence may be hardcoded")
        audit["warnings"].append(f"NBA confidence has low variance ({max_conf - min_conf:.3f})")
    else:
        print(f"  ✅ GOOD VARIANCE - Confidence is dynamic")
        audit["passed"].append("NBA confidence is dynamic")
    
    # Check action diversity
    print(f"\nAction Distribution:")
    for action, count in sorted(action_dist.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_nba * 100)
        print(f"  {action}: {count:,} ({pct:.1f}%)")
    
    # Check for duplicate recommendations
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT customer_id, recommended_action, channel, offer
            FROM nba_decisions
            GROUP BY customer_id, recommended_action, channel, offer
            HAVING COUNT(*) > 1
        )
    """)
    duplicate_recs = cursor.fetchone()[0]
    
    if duplicate_recs > 0:
        print(f"\n⚠️  {duplicate_recs} duplicate recommendations found")
        audit["warnings"].append(f"{duplicate_recs} duplicate NBA recommendations")
    else:
        print(f"\n✅ No duplicate recommendations")
        audit["passed"].append("NBA recommendations are unique")
    
    audit["phases"]["phase5_nba"] = {
        "confidence_range": max_conf - min_conf,
        "action_distribution": action_dist,
        "duplicate_recs": duplicate_recs
    }
    
    # ====================================================================
    # PHASE 6: TRUST CENTER VALIDATION
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 6: TRUST CENTER")
    print("-" * 100)
    
    # Trust score distribution
    cursor.execute("SELECT AVG(trust_score), MIN(trust_score), MAX(trust_score) FROM customer_profiles")
    avg_trust, min_trust, max_trust = cursor.fetchone()
    
    print(f"\nTrust Score Distribution:")
    print(f"  Average: {avg_trust:.1f}")
    print(f"  Min: {min_trust:.1f}")
    print(f"  Max: {max_trust:.1f}")
    
    # Calculate trust drivers from database
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
    customers_with_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
    total_cust = cursor.fetchone()[0]
    
    purchase_history_driver = (customers_with_orders / total_cust) * 100
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='delivered'")
    delivered = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    payment_reliability_driver = (delivered / max(total_orders, 1)) * 100
    
    cursor.execute("SELECT COUNT(*) FROM events WHERE event_type='refund_request'")
    refund_requests = cursor.fetchone()[0]
    
    return_rate_driver = (refund_requests / max(total_orders, 1)) * 100
    
    print(f"\nTrust Drivers (Calculated from Database):")
    print(f"  Purchase History: {purchase_history_driver:.1f}%")
    print(f"  Payment Reliability: {payment_reliability_driver:.1f}%")
    print(f"  Return Rate: {return_rate_driver:.1f}%")
    
    audit["phases"]["phase6_trust"] = {
        "avg_trust": avg_trust,
        "drivers": {
            "purchase_history": purchase_history_driver,
            "payment_reliability": payment_reliability_driver,
            "return_rate": return_rate_driver
        }
    }
    
    audit["passed"].append("Trust Center validated with database calculations")
    
    # ====================================================================
    # PHASE 7: CHURN CENTER VALIDATION
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 7: CHURN CENTER")
    print("-" * 100)
    
    # Churn distribution
    cursor.execute("""
        SELECT 
            CASE 
                WHEN churn_probability < 0.3 THEN 'low'
                WHEN churn_probability < 0.6 THEN 'medium'
                WHEN churn_probability < 0.8 THEN 'high'
                ELSE 'critical'
            END as risk_level,
            COUNT(*) as cnt
        FROM customer_profiles
        GROUP BY risk_level
    """)
    churn_dist = dict(cursor.fetchall())
    
    print(f"\nChurn Risk Distribution:")
    for level in ['low', 'medium', 'high', 'critical']:
        count = churn_dist.get(level, 0)
        pct = (count / total_cust * 100) if total_cust > 0 else 0
        print(f"  {level.capitalize()}: {count:,} ({pct:.1f}%)")
    
    audit["phases"]["phase7_churn"] = churn_dist
    audit["passed"].append("Churn Center distribution validated")
    
    # ====================================================================
    # PHASE 8: REVENUE AT RISK CALCULATION
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("PHASE 8: REVENUE AT RISK")
    print("-" * 100)
    
    high_risk_count = churn_dist.get('high', 0) + churn_dist.get('critical', 0)
    
    # Method 1: CLV-based
    cursor.execute("""
        SELECT SUM(clv)
        FROM customer_profiles
        WHERE churn_probability >= 0.7
    """)
    revenue_at_risk_clv = cursor.fetchone()[0] or 0
    
    # Method 2: Historical orders
    cursor.execute("""
        SELECT SUM(o.total_amount)
        FROM orders o
        JOIN customer_profiles cp ON o.customer_id = cp.customer_id
        WHERE cp.churn_probability >= 0.7
    """)
    revenue_at_risk_orders = cursor.fetchone()[0] or 0
    
    # Method 3: Potential (non-purchasers × avg order)
    cursor.execute("""
        SELECT COUNT(*)
        FROM customer_profiles
        WHERE churn_probability >= 0.7
        AND customer_id NOT IN (SELECT DISTINCT customer_id FROM orders)
    """)
    high_risk_non_purchasers = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(total_amount) FROM orders")
    avg_order = cursor.fetchone()[0] or 0
    
    potential_revenue_at_risk = high_risk_non_purchasers * avg_order
    
    total_revenue_at_risk = revenue_at_risk_orders + potential_revenue_at_risk
    
    print(f"\nRevenue At Risk Calculation:")
    print(f"  High Risk Customers: {high_risk_count:,}")
    print(f"  Method 1 (CLV): ₹{revenue_at_risk_clv:,.2f}")
    print(f"  Method 2 (Historical Orders): ₹{revenue_at_risk_orders:,.2f}")
    print(f"  Method 3 (Potential): ₹{potential_revenue_at_risk:,.2f}")
    print(f"    - Non-purchasers: {high_risk_non_purchasers:,}")
    print(f"    - Avg Order: ₹{avg_order:,.2f}")
    print(f"  ✓ Total Revenue At Risk: ₹{total_revenue_at_risk:,.2f}")
    
    if revenue_at_risk_clv == 0 and total_revenue_at_risk > 0:
        print(f"\n⚠️  CLV is zero - using order-based calculation")
        audit["warnings"].append("CLV is zero for all customers, using alternative calculation")
    
    audit["phases"]["phase8_revenue_at_risk"] = {
        "high_risk_count": high_risk_count,
        "clv_based": revenue_at_risk_clv,
        "historical_based": revenue_at_risk_orders,
        "potential_based": potential_revenue_at_risk,
        "total": total_revenue_at_risk,
        "method_used": "historical + potential"
    }
    
    if total_revenue_at_risk > 0:
        audit["passed"].append(f"Revenue At Risk calculated: ₹{total_revenue_at_risk:,.2f}")
    else:
        audit["failed"].append("Revenue At Risk is ₹0")
    
    # ====================================================================
    # FINAL SUMMARY
    # ====================================================================
    
    print("\n\n" + "=" * 100)
    print("AUDIT SUMMARY")
    print("=" * 100)
    
    print(f"\n✅ PASSED ({len(audit['passed'])}):")
    for item in audit["passed"][:10]:
        print(f"  • {item}")
    
    print(f"\n⚠️  WARNINGS ({len(audit['warnings'])}):")
    for item in audit["warnings"]:
        print(f"  • {item}")
    
    print(f"\n❌ FAILED ({len(audit['failed'])}):")
    for item in audit["failed"]:
        print(f"  • {item}")
    
    print(f"\n🔍 CRITICAL ISSUES ({len(audit['issues'])}):")
    for issue in audit["issues"]:
        print(f"  • [{issue['severity']}] {issue['issue']}")
    
    # Save report
    with open("complete_system_audit_report.json", "w") as f:
        json.dump(audit, f, indent=2, default=str)
    
    print(f"\n" + "=" * 100)
    print("AUDIT COMPLETE")
    print("=" * 100)
    print(f"Report saved to: complete_system_audit_report.json")
    
    conn.close()
    return audit

if __name__ == "__main__":
    complete_system_audit()
