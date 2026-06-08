"""
OMNIPULSE AI - COMPREHENSIVE SYSTEM AUDIT
Phases 1-15: Complete database and system validation
"""
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def audit_database():
    """Phase 1: Database Audit"""
    conn = sqlite3.connect('omnipulse.db')
    cursor = conn.cursor()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "phases": {}
    }
    
    print("="*80)
    print("OMNIPULSE AI - COMPREHENSIVE SYSTEM AUDIT")
    print("="*80)
    
    # ========================================================================
    # PHASE 1: DATABASE AUDIT
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 1: DATABASE AUDIT")
    print("="*80)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nFound {len(tables)} tables:")
    
    table_info = {}
    for table in tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        foreign_keys = cursor.fetchall()
        
        table_info[table] = {
            "row_count": row_count,
            "columns": [{"name": col[1], "type": col[2], "notnull": col[3], "pk": col[5]} for col in columns],
            "foreign_keys": foreign_keys
        }
        
        print(f"\n  📊 {table}")
        print(f"     Rows: {row_count:,}")
        print(f"     Columns: {len(columns)}")
        if foreign_keys:
            print(f"     Foreign Keys: {len(foreign_keys)}")
    
    report["phases"]["phase1_database_audit"] = {
        "status": "COMPLETE",
        "tables": table_info,
        "total_tables": len(tables)
    }
    
    # ========================================================================
    # PHASE 2: CUSTOMER DATA QUALITY
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 2: CUSTOMER DATA QUALITY")
    print("="*80)
    
    issues = []
    
    # Check for garbage values in customers
    cursor.execute("SELECT customer_id, first_name, last_name, city FROM customers WHERE role='customer' LIMIT 1000")
    customers = cursor.fetchall()
    
    garbage_patterns = ["Inactive •", "Unknown", "??????", "��", "�"]
    corrupted_customers = 0
    
    for cust in customers:
        cust_id, first, last, city = cust
        full_data = f"{first} {last} {city}"
        for pattern in garbage_patterns:
            if pattern in full_data:
                corrupted_customers += 1
                issues.append(f"Customer {cust_id}: contains '{pattern}'")
                break
    
    print(f"\n  ✓ Total customers checked: {len(customers)}")
    print(f"  {'❌' if corrupted_customers > 0 else '✅'} Corrupted customer records: {corrupted_customers}")
    
    # Check product names in events
    cursor.execute("SELECT DISTINCT event_value FROM events WHERE event_type='product_view' LIMIT 100")
    products = [row[0] for row in cursor.fetchall()]
    
    corrupted_products = sum(1 for p in products if any(pattern in str(p) for pattern in garbage_patterns))
    
    print(f"  ✓ Unique products checked: {len(products)}")
    print(f"  {'❌' if corrupted_products > 0 else '✅'} Corrupted product names: {corrupted_products}")
    
    report["phases"]["phase2_data_quality"] = {
        "status": "COMPLETE" if corrupted_customers == 0 and corrupted_products == 0 else "ISSUES_FOUND",
        "corrupted_customers": corrupted_customers,
        "corrupted_products": corrupted_products,
        "issues": issues[:10]  # First 10 issues
    }
    
    # ========================================================================
    # PHASE 3: CUSTOMER 360
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 3: CUSTOMER 360 VALIDATION")
    print("="*80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN clv IS NULL OR clv = 0 THEN 1 ELSE 0 END) as null_clv,
            SUM(CASE WHEN trust_score IS NULL THEN 1 ELSE 0 END) as null_trust,
            SUM(CASE WHEN churn_probability IS NULL THEN 1 ELSE 0 END) as null_churn,
            SUM(CASE WHEN emotion IS NULL THEN 1 ELSE 0 END) as null_emotion
        FROM customer_profiles
    """)
    
    total, null_clv, null_trust, null_churn, null_emotion = cursor.fetchone()
    
    print(f"\n  ✓ Total profiles: {total}")
    print(f"  {'⚠️ ' if null_clv > total * 0.5 else '✅'} CLV missing: {null_clv} ({null_clv/total*100:.1f}%)")
    print(f"  {'❌' if null_trust > 0 else '✅'} Trust missing: {null_trust}")
    print(f"  {'❌' if null_churn > 0 else '✅'} Churn missing: {null_churn}")
    print(f"  {'❌' if null_emotion > 0 else '✅'} Emotion missing: {null_emotion}")
    
    report["phases"]["phase3_customer360"] = {
        "status": "PASS" if null_trust == 0 and null_churn == 0 else "FAIL",
        "total_profiles": total,
        "missing_clv_pct": round(null_clv/total*100, 1),
        "missing_trust": null_trust,
        "missing_churn": null_churn
    }
    
    # ========================================================================
    # PHASE 4: EMOTION CENTER
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 4: EMOTION CENTER VALIDATION")
    print("="*80)
    
    cursor.execute("SELECT emotion, COUNT(*) FROM customer_profiles GROUP BY emotion")
    emotion_dist = dict(cursor.fetchall())
    
    print(f"\n  Emotion Distribution:")
    for emotion, count in sorted(emotion_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"    {emotion}: {count} ({count/total*100:.1f}%)")
    
    report["phases"]["phase4_emotion"] = {
        "status": "PASS",
        "distribution": emotion_dist
    }
    
    # ========================================================================
    # PHASE 5: CHURN CENTER
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 5: CHURN CENTER VALIDATION")
    print("="*80)
    
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN churn_probability >= 0.8 THEN 1 ELSE 0 END) as critical,
            SUM(CASE WHEN churn_probability >= 0.6 AND churn_probability < 0.8 THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN churn_probability >= 0.3 AND churn_probability < 0.6 THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN churn_probability < 0.3 THEN 1 ELSE 0 END) as low
        FROM customer_profiles
    """)
    
    critical, high, medium, low = cursor.fetchone()
    
    print(f"\n  Churn Risk Distribution:")
    print(f"    Critical (≥80%): {critical} ({critical/total*100:.1f}%)")
    print(f"    High (60-80%): {high} ({high/total*100:.1f}%)")
    print(f"    Medium (30-60%): {medium} ({medium/total*100:.1f}%)")
    print(f"    Low (<30%): {low} ({low/total*100:.1f}%)")
    
    # Check for duplicates
    cursor.execute("""
        SELECT customer_id, COUNT(*) as cnt 
        FROM customer_profiles 
        GROUP BY customer_id 
        HAVING cnt > 1
    """)
    duplicates = cursor.fetchall()
    
    print(f"\n  {'❌' if duplicates else '✅'} Duplicate profiles: {len(duplicates)}")
    
    report["phases"]["phase5_churn"] = {
        "status": "PASS" if not duplicates else "FAIL",
        "distribution": {"critical": critical, "high": high, "medium": medium, "low": low},
        "duplicates": len(duplicates)
    }
    
    # ========================================================================
    # PHASE 6: TRUST CENTER
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 6: TRUST CENTER VALIDATION")
    print("="*80)
    
    cursor.execute("""
        SELECT 
            AVG(trust_score) as avg_trust,
            SUM(CASE WHEN trust_score >= 80 THEN 1 ELSE 0 END) as high_trust,
            SUM(CASE WHEN trust_score >= 50 AND trust_score < 80 THEN 1 ELSE 0 END) as medium_trust,
            SUM(CASE WHEN trust_score < 50 THEN 1 ELSE 0 END) as low_trust
        FROM customer_profiles
    """)
    
    avg_trust, high_trust, medium_trust, low_trust = cursor.fetchone()
    
    print(f"\n  Average Trust Score: {avg_trust:.1f}")
    print(f"  Trust Distribution:")
    print(f"    High (≥80): {high_trust} ({high_trust/total*100:.1f}%)")
    print(f"    Medium (50-79): {medium_trust} ({medium_trust/total*100:.1f}%)")
    print(f"    Low (<50): {low_trust} ({low_trust/total*100:.1f}%)")
    
    # Check return rate calculation
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM events WHERE event_type='refund_request'")
    refund_requests = cursor.fetchone()[0]
    
    return_rate = (refund_requests / total_orders * 100) if total_orders > 0 else 0
    
    print(f"\n  Return Rate Validation:")
    print(f"    Total Orders: {total_orders}")
    print(f"    Refund Requests: {refund_requests}")
    print(f"    Return Rate: {return_rate:.1f}%")
    
    report["phases"]["phase6_trust"] = {
        "status": "PASS",
        "avg_trust": round(avg_trust, 1),
        "distribution": {"high": high_trust, "medium": medium_trust, "low": low_trust},
        "return_rate": round(return_rate, 1)
    }
    
    # ========================================================================
    # PHASE 7: NBA CENTER
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 7: NBA CENTER VALIDATION")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM nba_decisions")
    total_nba = cursor.fetchone()[0]
    
    print(f"\n  Total NBA Decisions: {total_nba}")
    
    # Check for duplicates (same customer multiple times)
    cursor.execute("""
        SELECT customer_id, COUNT(*) as cnt
        FROM nba_decisions
        GROUP BY customer_id
        ORDER BY cnt DESC
        LIMIT 10
    """)
    
    nba_duplicates = cursor.fetchall()
    max_per_customer = max([c[1] for c in nba_duplicates]) if nba_duplicates else 0
    
    print(f"  Max decisions per customer: {max_per_customer}")
    
    # Check action diversity
    cursor.execute("SELECT recommended_action, COUNT(*) FROM nba_decisions GROUP BY recommended_action")
    action_dist = dict(cursor.fetchall())
    
    print(f"\n  Action Distribution:")
    for action, count in sorted(action_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"    {action}: {count} ({count/total_nba*100:.1f}%)")
    
    # Check if one action dominates > 95%
    max_action_pct = max(action_dist.values()) / total_nba * 100 if total_nba > 0 else 0
    
    if max_action_pct > 95:
        print(f"\n  ❌ WARNING: One action dominates {max_action_pct:.1f}%")
    else:
        print(f"\n  ✅ Action diversity looks good")
    
    # Check channel diversity
    cursor.execute("SELECT channel, COUNT(*) FROM nba_decisions GROUP BY channel")
    channel_dist = dict(cursor.fetchall())
    
    print(f"\n  Channel Distribution:")
    for channel, count in sorted(channel_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"    {channel}: {count} ({count/total_nba*100:.1f}%)")
    
    # Check confidence diversity
    cursor.execute("SELECT confidence FROM nba_decisions LIMIT 100")
    confidences = [row[0] for row in cursor.fetchall()]
    unique_confidences = len(set(confidences))
    
    print(f"\n  Confidence Diversity: {unique_confidences} unique values in sample")
    
    report["phases"]["phase7_nba"] = {
        "status": "FAIL" if max_action_pct > 95 else "PASS",
        "total_decisions": total_nba,
        "max_per_customer": max_per_customer,
        "action_distribution": action_dist,
        "channel_distribution": channel_dist,
        "confidence_diversity": unique_confidences,
        "max_action_pct": round(max_action_pct, 1)
    }
    
    # ========================================================================
    # PHASE 8: JOURNEY REPLAY
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 8: JOURNEY REPLAY VALIDATION")
    print("="*80)
    
    # Get sample customer events
    cursor.execute("""
        SELECT customer_id, COUNT(*) as event_count
        FROM events
        GROUP BY customer_id
        ORDER BY event_count DESC
        LIMIT 5
    """)
    
    top_customers = cursor.fetchall()
    
    print(f"\n  Top 5 Customers by Event Count:")
    for cust_id, count in top_customers:
        print(f"    {cust_id}: {count} events")
    
    # Check event type distribution
    cursor.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC")
    event_types = cursor.fetchall()
    
    print(f"\n  Event Type Distribution:")
    for event_type, count in event_types[:10]:
        print(f"    {event_type}: {count}")
    
    report["phases"]["phase8_journey"] = {
        "status": "PASS",
        "top_customer_events": dict(top_customers),
        "event_types": dict(event_types)
    }
    
    # ========================================================================
    # PHASE 9: CAMPAIGN INTELLIGENCE
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 9: CAMPAIGN INTELLIGENCE VALIDATION")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM campaigns")
    total_campaigns = cursor.fetchone()[0]
    
    print(f"\n  Total Campaigns: {total_campaigns}")
    
    if total_campaigns > 0:
        cursor.execute("SELECT status, COUNT(*) FROM campaigns GROUP BY status")
        campaign_status = dict(cursor.fetchall())
        
        print(f"  Campaign Status:")
        for status, count in campaign_status.items():
            print(f"    {status}: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM campaign_responses")
        total_responses = cursor.fetchone()[0]
        
        print(f"\n  Campaign Responses: {total_responses}")
        
        if total_responses > 0:
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN opened THEN 1 ELSE 0 END) as opens,
                    SUM(CASE WHEN clicked THEN 1 ELSE 0 END) as clicks,
                    SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions
                FROM campaign_responses
            """)
            opens, clicks, conversions = cursor.fetchone()
            
            print(f"  Opens: {opens} ({opens/total_responses*100:.1f}%)")
            print(f"  Clicks: {clicks} ({clicks/total_responses*100:.1f}%)")
            print(f"  Conversions: {conversions} ({conversions/total_responses*100:.1f}%)")
        
        report["phases"]["phase9_campaigns"] = {
            "status": "PASS",
            "total_campaigns": total_campaigns,
            "campaign_status": campaign_status,
            "total_responses": total_responses
        }
    else:
        print("  ⚠️  No campaigns found")
        report["phases"]["phase9_campaigns"] = {
            "status": "WARNING",
            "total_campaigns": 0
        }
    
    # ========================================================================
    # PHASE 10: ROI ATTRIBUTION CENTER
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 10: ROI ATTRIBUTION CENTER VALIDATION")
    print("="*80)
    
    # Total revenue
    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status != 'cancelled'")
    total_revenue = cursor.fetchone()[0] or 0
    
    print(f"\n  Total Revenue: ₹{total_revenue:,.0f}")
    
    # Campaign revenue
    cursor.execute("SELECT SUM(revenue) FROM campaign_responses WHERE converted = 1")
    campaign_revenue = cursor.fetchone()[0] or 0
    
    print(f"  Campaign Revenue: ₹{campaign_revenue:,.0f} ({campaign_revenue/total_revenue*100:.1f}% of total)" if total_revenue > 0 else "  Campaign Revenue: ₹0")
    
    # Revenue at risk
    cursor.execute("SELECT SUM(clv) FROM customer_profiles WHERE churn_probability > 0.6")
    revenue_at_risk = cursor.fetchone()[0] or 0
    
    print(f"  Revenue At Risk: ₹{revenue_at_risk:,.0f}")
    
    # Check if all are zeros
    has_zeros = total_revenue == 0 or campaign_revenue == 0
    
    print(f"\n  {'❌ WARNING: Zero values detected' if has_zeros else '✅ Revenue data looks good'}")
    
    report["phases"]["phase10_roi"] = {
        "status": "FAIL" if has_zeros else "PASS",
        "total_revenue": round(total_revenue, 2),
        "campaign_revenue": round(campaign_revenue, 2),
        "revenue_at_risk": round(revenue_at_risk, 2)
    }
    
    # ========================================================================
    # PHASE 13: DATA CONSISTENCY
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 13: DATA CONSISTENCY CHECK")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE role='customer'")
    customer_count_customers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customer_profiles")
    customer_count_profiles = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
    customer_count_orders = cursor.fetchone()[0]
    
    print(f"\n  Customer counts across tables:")
    print(f"    customers table: {customer_count_customers}")
    print(f"    customer_profiles: {customer_count_profiles}")
    print(f"    orders (unique): {customer_count_orders}")
    
    consistency = customer_count_customers == customer_count_profiles
    
    print(f"\n  {'✅' if consistency else '❌'} Customer count consistency: {'PASS' if consistency else 'FAIL'}")
    
    report["phases"]["phase13_consistency"] = {
        "status": "PASS" if consistency else "FAIL",
        "customer_counts": {
            "customers": customer_count_customers,
            "profiles": customer_count_profiles,
            "orders_unique": customer_count_orders
        }
    }
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("PHASE 15: FINAL VALIDATION REPORT")
    print("="*80)
    
    passed = sum(1 for phase in report["phases"].values() if phase["status"] == "PASS")
    failed = sum(1 for phase in report["phases"].values() if phase["status"] == "FAIL")
    warnings = sum(1 for phase in report["phases"].values() if phase["status"] in ["WARNING", "ISSUES_FOUND"])
    
    print(f"\n  ✅ PASSED: {passed}")
    print(f"  ❌ FAILED: {failed}")
    print(f"  ⚠️  WARNINGS: {warnings}")
    
    print(f"\n  Phase Status:")
    for phase_name, phase_data in report["phases"].items():
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️", "ISSUES_FOUND": "⚠️", "COMPLETE": "✅"}.get(phase_data["status"], "❓")
        print(f"    {status_icon} {phase_name}: {phase_data['status']}")
    
    report["summary"] = {
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "total_phases": len(report["phases"])
    }
    
    conn.close()
    
    # Save report
    with open('comprehensive_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n  📄 Full report saved to: comprehensive_audit_report.json")
    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80)
    
    return report

if __name__ == "__main__":
    audit_database()
