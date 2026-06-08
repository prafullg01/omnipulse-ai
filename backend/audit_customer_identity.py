"""
Customer Identity Fragmentation Audit
Identifies all customer ID formats across datasets and builds identity resolution mapping.
"""
import sqlite3
import json
from datetime import datetime

def audit_customer_identity():
    conn = sqlite3.connect("omnipulse.db")
    
    print("=" * 80)
    print("CUSTOMER IDENTITY FRAGMENTATION AUDIT")
    print("=" * 80)
    print()
    
    # ========================================================================
    # PHASE 1: AUDIT ALL CUSTOMER ID SOURCES
    # ========================================================================
    
    print("PHASE 1: Customer ID Source Audit")
    print("-" * 80)
    
    sources = {}
    
    # 1. Customers table
    cursor = conn.cursor()
    cursor.execute("""
        SELECT customer_id, first_name, last_name, email, city
        FROM customers
        WHERE role = 'customer'
        LIMIT 5
    """)
    customers_sample = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM customers WHERE role = 'customer'")
    customers_count = cursor.fetchone()[0]
    
    sources['customers'] = {
        'count': customers_count,
        'id_format': customers_sample[0][0] if customers_sample else None,
        'sample_ids': [row[0] for row in customers_sample]
    }
    print(f"✓ customers: {sources['customers']['count']} records")
    print(f"  Format: {sources['customers']['id_format']}")
    print(f"  Sample: {sources['customers']['sample_ids']}")
    print()
    
    # 2. Orders table
    cursor.execute("SELECT DISTINCT customer_id FROM orders LIMIT 5")
    orders_sample = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
    orders_count = cursor.fetchone()[0]
    
    sources['orders'] = {
        'count': orders_count,
        'id_format': orders_sample[0][0] if orders_sample else None,
        'sample_ids': [row[0] for row in orders_sample]
    }
    print(f"✓ orders: {sources['orders']['count']} unique customers")
    print(f"  Format: {sources['orders']['id_format']}")
    print(f"  Sample: {sources['orders']['sample_ids']}")
    print()
    
    # 3. Events table
    cursor.execute("SELECT DISTINCT customer_id FROM events LIMIT 5")
    events_sample = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM events")
    events_count = cursor.fetchone()[0]
    
    sources['events'] = {
        'count': events_count,
        'id_format': events_sample[0][0] if events_sample else None,
        'sample_ids': [row[0] for row in events_sample]
    }
    print(f"✓ events: {sources['events']['count']} unique customers")
    print(f"  Format: {sources['events']['id_format']}")
    print(f"  Sample: {sources['events']['sample_ids']}")
    print()
    
    # 4. Customer Profiles
    cursor.execute("SELECT DISTINCT customer_id FROM customer_profiles LIMIT 5")
    profiles_sample = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customer_profiles")
    profiles_count = cursor.fetchone()[0]
    
    sources['customer_profiles'] = {
        'count': profiles_count,
        'id_format': profiles_sample[0][0] if profiles_sample else None,
        'sample_ids': [row[0] for row in profiles_sample]
    }
    print(f"✓ customer_profiles: {sources['customer_profiles']['count']} unique customers")
    print(f"  Format: {sources['customer_profiles']['id_format']}")
    print(f"  Sample: {sources['customer_profiles']['sample_ids']}")
    print()
    
    # 5. NBA Decisions
    cursor.execute("SELECT DISTINCT customer_id FROM nba_decisions LIMIT 5")
    nba_sample = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM nba_decisions")
    nba_count = cursor.fetchone()[0]
    
    sources['nba_decisions'] = {
        'count': nba_count,
        'id_format': nba_sample[0][0] if nba_sample else None,
        'sample_ids': [row[0] for row in nba_sample]
    }
    print(f"✓ nba_decisions: {sources['nba_decisions']['count']} unique customers")
    print(f"  Format: {sources['nba_decisions']['id_format']}")
    print(f"  Sample: {sources['nba_decisions']['sample_ids']}")
    print()
    
    # 6. Campaign Responses
    cursor.execute("SELECT DISTINCT customer_id FROM campaign_responses LIMIT 5")
    campaign_resp_sample = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM campaign_responses")
    campaign_resp_count = cursor.fetchone()[0]
    
    sources['campaign_responses'] = {
        'count': campaign_resp_count,
        'id_format': campaign_resp_sample[0][0] if campaign_resp_sample else None,
        'sample_ids': [row[0] for row in campaign_resp_sample]
    }
    print(f"✓ campaign_responses: {sources['campaign_responses']['count']} unique customers")
    print(f"  Format: {sources['campaign_responses']['id_format']}")
    print(f"  Sample: {sources['campaign_responses']['sample_ids']}")
    print()
    
    # ========================================================================
    # PHASE 2: DETECT ID FORMAT PATTERNS
    # ========================================================================
    
    print("\nPHASE 2: ID Format Pattern Detection")
    print("-" * 80)
    
    patterns = {}
    for source, data in sources.items():
        if data['sample_ids']:
            sample = data['sample_ids'][0]
            if sample.startswith('CUST-') and len(sample) == 12:
                patterns[source] = 'CUST-NNNNNN (sequential)'
            elif sample.startswith('CUST-') and len(sample) > 12:
                patterns[source] = 'CUST-HEXHASH (UUID-like)'
            elif sample.startswith('MALL-'):
                patterns[source] = 'MALL-NNNNN (mall customers)'
            else:
                patterns[source] = f'Unknown ({sample})'
            print(f"{source:20s} → {patterns[source]}")
    
    print()
    
    # ========================================================================
    # PHASE 3: VALIDATE CROSS-TABLE JOINS
    # ========================================================================
    
    print("\nPHASE 3: Cross-Table Join Validation")
    print("-" * 80)
    
    validations = {}
    
    # Customers → Orders
    cursor.execute("""
        SELECT COUNT(DISTINCT c.customer_id) as matched
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE c.role = 'customer'
    """)
    validations['customers_orders'] = cursor.fetchone()[0]
    print(f"customers → orders: {validations['customers_orders']} matched")
    
    # Customers → Events
    cursor.execute("""
        SELECT COUNT(DISTINCT c.customer_id) as matched
        FROM customers c
        JOIN events e ON c.customer_id = e.customer_id
        WHERE c.role = 'customer'
    """)
    validations['customers_events'] = cursor.fetchone()[0]
    print(f"customers → events: {validations['customers_events']} matched")
    
    # Orders → Events
    cursor.execute("""
        SELECT COUNT(DISTINCT o.customer_id) as matched
        FROM orders o
        JOIN events e ON o.customer_id = e.customer_id
    """)
    validations['orders_events'] = cursor.fetchone()[0]
    print(f"orders → events: {validations['orders_events']} matched")
    
    # Campaign Events → Orders (THE CRITICAL TEST)
    cursor.execute("""
        SELECT COUNT(DISTINCT e.customer_id) as matched
        FROM events e
        JOIN orders o ON e.customer_id = o.customer_id
        WHERE e.event_type = 'campaign_received'
    """)
    validations['campaign_events_orders'] = cursor.fetchone()[0]
    print(f"campaign_received → orders: {validations['campaign_events_orders']} matched ⚠️")
    
    # Campaign Responses → Orders
    cursor.execute("""
        SELECT COUNT(DISTINCT cr.customer_id) as matched
        FROM campaign_responses cr
        JOIN orders o ON cr.customer_id = o.customer_id
    """)
    validations['campaign_responses_orders'] = cursor.fetchone()[0]
    print(f"campaign_responses → orders: {validations['campaign_responses_orders']} matched")
    
    print()
    
    # ========================================================================
    # PHASE 4: ANALYZE CUSTOMER ID OVERLAP
    # ========================================================================
    
    print("\nPHASE 4: Customer ID Overlap Analysis")
    print("-" * 80)
    
    # Get all unique customer IDs from key tables
    cursor.execute("SELECT DISTINCT customer_id FROM customers WHERE role = 'customer' LIMIT 10")
    sample_customers = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customers WHERE role = 'customer'")
    total_customers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
    total_orders = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM events")
    total_events = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM campaign_responses")
    total_campaigns = cursor.fetchone()[0]
    
    all_unique = total_customers + total_orders + total_events + total_campaigns
    
    print(f"Total unique customer IDs (estimated sum): {all_unique}")
    print()
    
    # Check which IDs appear in multiple tables
    overlap_analysis = []
    for cid in sample_customers:
        tables = []
        cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_id = ?", (cid,))
        if cursor.fetchone()[0] > 0:
            tables.append('customers')
        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (cid,))
        if cursor.fetchone()[0] > 0:
            tables.append('orders')
        cursor.execute("SELECT COUNT(*) FROM events WHERE customer_id = ?", (cid,))
        if cursor.fetchone()[0] > 0:
            tables.append('events')
        cursor.execute("SELECT COUNT(*) FROM customer_profiles WHERE customer_id = ?", (cid,))
        if cursor.fetchone()[0] > 0:
            tables.append('profiles')
        overlap_analysis.append({
            'customer_id': cid,
            'tables': tables,
            'table_count': len(tables)
        })
    
    print("Sample ID Overlap:")
    for item in overlap_analysis:
        print(f"  {item['customer_id']}: {item['table_count']} tables → {', '.join(item['tables'])}")
    
    print()
    
    # ========================================================================
    # PHASE 5: ROOT CAUSE ANALYSIS
    # ========================================================================
    
    print("\nPHASE 5: Root Cause Analysis")
    print("-" * 80)
    
    # Check if campaign_received events exist at all
    cursor.execute("""
        SELECT event_type, COUNT(*) as count
        FROM events
        WHERE event_type LIKE '%campaign%'
        GROUP BY event_type
    """)
    campaign_events = cursor.fetchall()
    
    print("Campaign-related events:")
    if len(campaign_events) > 0:
        for row in campaign_events:
            print(f"  {row[0]}: {row[1]}")
    else:
        print("  ⚠️  NO campaign events found in events table!")
    
    print()
    
    # Check campaign_responses
    cursor.execute("SELECT COUNT(*) as c FROM campaign_responses")
    cr_count = cursor.fetchone()[0]
    print(f"campaign_responses records: {cr_count}")
    
    # Sample campaign response customer IDs
    cursor.execute("SELECT customer_id FROM campaign_responses LIMIT 10")
    cr_sample = cursor.fetchall()
    print(f"Sample campaign_responses customer_ids:")
    for row in cr_sample:
        cid = row[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (cid,))
        in_orders = cursor.fetchone()[0] > 0
        cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_id = ?", (cid,))
        in_customers = cursor.fetchone()[0] > 0
        print(f"  {cid} → orders:{in_orders}, customers:{in_customers}")
    
    print()
    
    # ========================================================================
    # PHASE 6: GENERATE IDENTITY RESOLUTION STRATEGY
    # ========================================================================
    
    print("\nPHASE 6: Identity Resolution Strategy")
    print("-" * 80)
    
    # Determine if identity resolution is feasible
    if validations['campaign_events_orders'] == 0 and validations['campaign_responses_orders'] == 0:
        print("⚠️  CRITICAL FINDING:")
        print("   Campaign customers and order customers have ZERO overlap.")
        print("   This means:")
        print("   1. Campaigns were sent to different customer IDs than those who placed orders")
        print("   2. Direct campaign → revenue attribution is IMPOSSIBLE with current data")
        print("   3. Campaign revenue must be calculated using BEHAVIORAL attribution")
        print()
        print("RECOMMENDED APPROACH:")
        print("   Instead of direct ID matching:")
        print("   - Use temporal correlation (purchases after campaign send date)")
        print("   - Use segment-based attribution (campaigns to high-risk → high-risk purchases)")
        print("   - Label all campaign revenue as 'ESTIMATED (behavioral)' not 'DIRECT'")
        print("   - Create a separate 'Campaign Influence Score' instead of direct revenue")
        
        strategy = "BEHAVIORAL_ATTRIBUTION"
    else:
        print("✓ Some customer ID overlap detected")
        print(f"  {validations['campaign_responses_orders']} campaign customers have orders")
        print("  Direct attribution is possible for matched customers")
        print("  Use behavioral attribution for unmatched customers")
        
        strategy = "HYBRID_ATTRIBUTION"
    
    print()
    
    # ========================================================================
    # GENERATE REPORT
    # ========================================================================
    
    report = {
        "audit_timestamp": datetime.utcnow().isoformat(),
        "sources": sources,
        "patterns": patterns,
        "validations": validations,
        "total_unique_customers": all_unique,
        "overlap_sample": overlap_analysis,
        "strategy": strategy,
        "critical_issues": [
            {
                "issue": "Campaign-to-Order attribution broken",
                "severity": "CRITICAL",
                "impact": "Cannot calculate true campaign revenue",
                "cause": "Customer IDs from campaign_responses don't match order customer_ids",
                "solution": "Use behavioral/temporal attribution with clear labeling"
            }
        ] if validations['campaign_responses_orders'] == 0 else [],
        "recommendations": [
            "Update ROI endpoint to use behavioral attribution",
            "Add 'attribution_method' field to all revenue metrics",
            "Create separate 'Campaign Influence Index' metric",
            "Label all campaign revenue as ESTIMATED not DIRECT",
            "Add confidence scores to attribution calculations"
        ] if strategy == "BEHAVIORAL_ATTRIBUTION" else [
            "Use direct attribution for matched customers",
            "Use behavioral attribution for unmatched customers",
            "Report both direct and estimated revenue separately"
        ]
    }
    
    with open("customer_identity_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"Report saved to: customer_identity_audit_report.json")
    print(f"Strategy: {strategy}")
    print()
    
    conn.close()
    return report

if __name__ == "__main__":
    report = audit_customer_identity()
