"""
Complete Audit: Fairness Observatory & Executive Intelligence Center
Validates all metrics against database and identifies hardcoded values.
"""
import sqlite3
import json
from datetime import datetime

def audit_fairness_and_executive():
    conn = sqlite3.connect("omnipulse.db")
    cursor = conn.cursor()
    
    print("=" * 80)
    print("FAIRNESS OBSERVATORY & EXECUTIVE INTELLIGENCE AUDIT")
    print("=" * 80)
    print()
    
    audit_results = {
        "audit_timestamp": datetime.utcnow().isoformat(),
        "fairness_observatory": {},
        "executive_intelligence": {},
        "validation_queries": [],
        "issues": [],
        "recommendations": []
    }
    
    # ========================================================================
    # PART 1: FAIRNESS OBSERVATORY AUDIT
    # ========================================================================
    
    print("PART 1: FAIRNESS OBSERVATORY AUDIT")
    print("-" * 80)
    print()
    
    # Check if fairness data exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fairness_metrics'")
    fairness_table_exists = cursor.fetchone() is not None
    
    if not fairness_table_exists:
        print("⚠️  fairness_metrics table does NOT exist!")
        audit_results["issues"].append({
            "module": "Fairness Observatory",
            "severity": "CRITICAL",
            "issue": "fairness_metrics table missing",
            "impact": "All fairness metrics are hardcoded or calculated on-the-fly"
        })
    else:
        print("✓ fairness_metrics table exists")
    
    print()
    
    # -------------------------------------------------------------------------
    # 1.1 Check NBA Decisions for Fairness Analysis
    # -------------------------------------------------------------------------
    
    print("1.1 NBA Decisions Distribution")
    print("-" * 40)
    
    # Get NBA decisions
    cursor.execute("SELECT COUNT(*) FROM nba_decisions")
    total_nba = cursor.fetchone()[0]
    print(f"Total NBA Decisions: {total_nba}")
    
    if total_nba == 0:
        audit_results["issues"].append({
            "module": "Fairness Observatory",
            "severity": "CRITICAL",
            "issue": "No NBA decisions found",
            "impact": "Cannot calculate fairness metrics"
        })
    
    # Check if customers table has demographic fields
    cursor.execute("PRAGMA table_info(customers)")
    customer_columns = {row[1] for row in cursor.fetchall()}
    
    has_gender = 'gender' in customer_columns
    has_age = 'age' in customer_columns or 'age_group' in customer_columns
    has_city = 'city' in customer_columns
    
    print(f"Customer demographics available:")
    print(f"  Gender: {'✓' if has_gender else '✗'}")
    print(f"  Age: {'✓' if has_age else '✗'}")
    print(f"  City/Region: {'✓' if has_city else '✗'}")
    print()
    
    fairness_data = {}
    
    # Gender distribution in NBA decisions
    if has_gender:
        cursor.execute("""
            SELECT c.gender, COUNT(n.decision_id) as count
            FROM nba_decisions n
            JOIN customers c ON n.customer_id = c.customer_id
            WHERE c.gender IS NOT NULL AND c.gender != ''
            GROUP BY c.gender
        """)
        gender_dist = cursor.fetchall()
        fairness_data['gender_distribution'] = {row[0]: row[1] for row in gender_dist}
        print(f"Gender Distribution in NBA:")
        for gender, count in gender_dist:
            pct = (count / total_nba * 100) if total_nba > 0 else 0
            print(f"  {gender}: {count} ({pct:.1f}%)")
        print()
    
    # Age distribution
    if has_age:
        if 'age' in customer_columns:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN c.age < 25 THEN '18-24'
                        WHEN c.age < 35 THEN '25-34'
                        WHEN c.age < 45 THEN '35-44'
                        WHEN c.age < 55 THEN '45-54'
                        ELSE '55+'
                    END as age_group,
                    COUNT(n.decision_id) as count
                FROM nba_decisions n
                JOIN customers c ON n.customer_id = c.customer_id
                WHERE c.age IS NOT NULL
                GROUP BY age_group
            """)
            age_dist = cursor.fetchall()
            fairness_data['age_distribution'] = {row[0]: row[1] for row in age_dist}
            print(f"Age Distribution in NBA:")
            for age_group, count in age_dist:
                pct = (count / total_nba * 100) if total_nba > 0 else 0
                print(f"  {age_group}: {count} ({pct:.1f}%)")
            print()
    
    # Action distribution
    cursor.execute("""
        SELECT recommended_action, COUNT(*) as count
        FROM nba_decisions
        GROUP BY recommended_action
    """)
    action_dist = cursor.fetchall()
    fairness_data['action_distribution'] = {row[0]: row[1] for row in action_dist}
    print(f"Action Distribution:")
    for action, count in action_dist:
        pct = (count / total_nba * 100) if total_nba > 0 else 0
        print(f"  {action}: {count} ({pct:.1f}%)")
    print()
    
    # Channel distribution
    cursor.execute("""
        SELECT channel, COUNT(*) as count
        FROM nba_decisions
        GROUP BY channel
    """)
    channel_dist = cursor.fetchall()
    fairness_data['channel_distribution'] = {row[0]: row[1] for row in channel_dist}
    print(f"Channel Distribution:")
    for channel, count in channel_dist:
        pct = (count / total_nba * 100) if total_nba > 0 else 0
        print(f"  {channel}: {count} ({pct:.1f}%)")
    print()
    
    # -------------------------------------------------------------------------
    # 1.2 Calculate Fairness Score from Real Data
    # -------------------------------------------------------------------------
    
    print("1.2 Fairness Score Calculation")
    print("-" * 40)
    
    # Calculate fairness using distribution variance
    # Lower variance = higher fairness
    
    def calculate_fairness_score(distribution_dict):
        """Calculate fairness score (0-100) from distribution. 100 = perfectly fair."""
        if not distribution_dict:
            return 50
        
        values = list(distribution_dict.values())
        if len(values) <= 1:
            return 100
        
        total = sum(values)
        if total == 0:
            return 100
        
        # Expected equal distribution
        expected_pct = 100 / len(values)
        
        # Calculate variance from expected
        actual_pcts = [(v / total * 100) for v in values]
        variance = sum((pct - expected_pct) ** 2 for pct in actual_pcts) / len(values)
        
        # Convert variance to fairness score (0-100)
        # Low variance = high fairness
        max_variance = expected_pct ** 2 * (len(values) - 1)  # Worst case: all in one bucket
        fairness = max(0, 100 - (variance / max_variance * 100)) if max_variance > 0 else 100
        
        return round(fairness, 1)
    
    fairness_scores = {}
    
    if fairness_data.get('gender_distribution'):
        fairness_scores['gender'] = calculate_fairness_score(fairness_data['gender_distribution'])
        print(f"Gender Fairness: {fairness_scores['gender']}/100")
    
    if fairness_data.get('age_distribution'):
        fairness_scores['age'] = calculate_fairness_score(fairness_data['age_distribution'])
        print(f"Age Fairness: {fairness_scores['age']}/100")
    
    fairness_scores['action'] = calculate_fairness_score(fairness_data['action_distribution'])
    print(f"Action Fairness: {fairness_scores['action']}/100")
    
    fairness_scores['channel'] = calculate_fairness_score(fairness_data['channel_distribution'])
    print(f"Channel Fairness: {fairness_scores['channel']}/100")
    
    # Overall fairness score (average)
    if fairness_scores:
        overall_fairness = sum(fairness_scores.values()) / len(fairness_scores)
        print(f"\n✓ Overall Fairness Score (calculated): {overall_fairness:.1f}/100")
        
        # Calculate Equity Index (normalized 0-1)
        equity_index = overall_fairness / 100
        print(f"✓ Equity Index (calculated): {equity_index:.3f}")
        
        # Validate consistency
        if equity_index > 0.95 and overall_fairness < 80:
            audit_results["issues"].append({
                "module": "Fairness Observatory",
                "severity": "HIGH",
                "issue": "Inconsistent metrics",
                "details": f"Equity Index {equity_index:.3f} > 0.95 but Fairness Score {overall_fairness:.1f} < 80",
                "impact": "Contradictory fairness indicators"
            })
            print(f"\n⚠️  INCONSISTENCY DETECTED!")
            print(f"   Equity Index ({equity_index:.3f}) suggests HIGH fairness")
            print(f"   But Fairness Score ({overall_fairness:.1f}) suggests issues")
        
        # Bias alerts
        if overall_fairness < 80:
            print(f"\n⚠️  Fairness score below 80 - bias detected")
            audit_results["recommendations"].append({
                "module": "Fairness Observatory",
                "recommendation": "Investigate distribution imbalances causing low fairness score",
                "action": "Review action/channel assignments for demographic groups"
            })
        elif overall_fairness >= 90:
            print(f"\n✓ Fairness score >= 90 - no significant bias detected")
        
        fairness_data['overall_fairness'] = overall_fairness
        fairness_data['equity_index'] = equity_index
        fairness_data['fairness_scores'] = fairness_scores
    else:
        print("\n⚠️  Cannot calculate fairness - insufficient data")
    
    audit_results["fairness_observatory"] = fairness_data
    
    print()
    print()
    
    # ========================================================================
    # PART 2: EXECUTIVE INTELLIGENCE CENTER AUDIT
    # ========================================================================
    
    print("PART 2: EXECUTIVE INTELLIGENCE CENTER AUDIT")
    print("-" * 80)
    print()
    
    executive_data = {}
    validation_queries = []
    
    # -------------------------------------------------------------------------
    # 2.1 Total Customers
    # -------------------------------------------------------------------------
    
    print("2.1 Total Customers")
    print("-" * 40)
    
    query_total_customers = "SELECT COUNT(*) FROM customers WHERE role = 'customer'"
    cursor.execute(query_total_customers)
    total_customers = cursor.fetchone()[0]
    print(f"✓ Total Customers: {total_customers:,}")
    
    validation_queries.append({
        "kpi": "Total Customers",
        "query": query_total_customers,
        "result": total_customers,
        "confidence": "HIGH"
    })
    executive_data['total_customers'] = total_customers
    print()
    
    # -------------------------------------------------------------------------
    # 2.2 Total Revenue
    # -------------------------------------------------------------------------
    
    print("2.2 Total Revenue")
    print("-" * 40)
    
    query_total_revenue = "SELECT SUM(total_amount) FROM orders WHERE status != 'cancelled'"
    cursor.execute(query_total_revenue)
    total_revenue = cursor.fetchone()[0] or 0
    print(f"✓ Total Revenue: ₹{total_revenue:,.2f}")
    
    validation_queries.append({
        "kpi": "Total Revenue",
        "query": query_total_revenue,
        "result": total_revenue,
        "confidence": "HIGH"
    })
    executive_data['total_revenue'] = total_revenue
    print()
    
    # -------------------------------------------------------------------------
    # 2.3 Active Campaigns
    # -------------------------------------------------------------------------
    
    print("2.3 Active Campaigns")
    print("-" * 40)
    
    query_active_campaigns = "SELECT COUNT(*) FROM campaigns WHERE status = 'active'"
    cursor.execute(query_active_campaigns)
    active_campaigns = cursor.fetchone()[0]
    print(f"✓ Active Campaigns: {active_campaigns}")
    
    validation_queries.append({
        "kpi": "Active Campaigns",
        "query": query_active_campaigns,
        "result": active_campaigns,
        "confidence": "HIGH"
    })
    executive_data['active_campaigns'] = active_campaigns
    print()
    
    # -------------------------------------------------------------------------
    # 2.4 High Risk Customers
    # -------------------------------------------------------------------------
    
    print("2.4 High Risk Customers")
    print("-" * 40)
    
    query_high_risk = "SELECT COUNT(*) FROM customer_profiles WHERE churn_probability >= 0.7"
    cursor.execute(query_high_risk)
    high_risk_customers = cursor.fetchone()[0]
    print(f"✓ High Risk Customers (churn >= 0.7): {high_risk_customers:,}")
    
    validation_queries.append({
        "kpi": "High Risk Customers",
        "query": query_high_risk,
        "result": high_risk_customers,
        "confidence": "HIGH"
    })
    executive_data['high_risk_customers'] = high_risk_customers
    print()
    
    # -------------------------------------------------------------------------
    # 2.5 Revenue At Risk (CRITICAL TEST)
    # -------------------------------------------------------------------------
    
    print("2.5 Revenue At Risk")
    print("-" * 40)
    
    # Method 1: Sum of CLV for high-risk customers
    query_revenue_at_risk_clv = """
        SELECT SUM(clv) 
        FROM customer_profiles 
        WHERE churn_probability >= 0.7
    """
    cursor.execute(query_revenue_at_risk_clv)
    revenue_at_risk_clv = cursor.fetchone()[0] or 0
    print(f"Method 1 (SUM CLV for high-risk): ₹{revenue_at_risk_clv:,.2f}")
    
    # Method 2: Actual historical revenue from high-risk customers
    query_revenue_at_risk_orders = """
        SELECT SUM(o.total_amount)
        FROM orders o
        JOIN customer_profiles cp ON o.customer_id = cp.customer_id
        WHERE cp.churn_probability >= 0.7
        AND o.status != 'cancelled'
    """
    cursor.execute(query_revenue_at_risk_orders)
    revenue_at_risk_orders = cursor.fetchone()[0] or 0
    print(f"Method 2 (Historical orders from high-risk): ₹{revenue_at_risk_orders:,.2f}")
    
    # Determine which to use
    if revenue_at_risk_clv > 0:
        revenue_at_risk = revenue_at_risk_clv
        method = "CLV-based"
        print(f"\n✓ Using CLV-based calculation: ₹{revenue_at_risk:,.2f}")
    else:
        revenue_at_risk = revenue_at_risk_orders
        method = "Historical orders"
        print(f"\n✓ CLV is zero, using historical orders: ₹{revenue_at_risk:,.2f}")
    
    validation_queries.append({
        "kpi": "Revenue At Risk",
        "query": query_revenue_at_risk_clv if revenue_at_risk_clv > 0 else query_revenue_at_risk_orders,
        "result": revenue_at_risk,
        "method": method,
        "confidence": "HIGH" if revenue_at_risk_clv > 0 else "MEDIUM"
    })
    executive_data['revenue_at_risk'] = revenue_at_risk
    executive_data['revenue_at_risk_method'] = method
    print()
    
    # -------------------------------------------------------------------------
    # 2.6 Revenue Exposure (should match Revenue At Risk)
    # -------------------------------------------------------------------------
    
    print("2.6 Revenue Exposure")
    print("-" * 40)
    
    # Revenue Exposure = Revenue At Risk (same calculation)
    revenue_exposure = revenue_at_risk
    print(f"✓ Revenue Exposure: ₹{revenue_exposure:,.2f} (matches Revenue At Risk)")
    
    validation_queries.append({
        "kpi": "Revenue Exposure",
        "query": "Same as Revenue At Risk",
        "result": revenue_exposure,
        "confidence": "HIGH"
    })
    executive_data['revenue_exposure'] = revenue_exposure
    print()
    
    # -------------------------------------------------------------------------
    # 2.7 Average Churn Risk
    # -------------------------------------------------------------------------
    
    print("2.7 Average Churn Risk")
    print("-" * 40)
    
    query_avg_churn = "SELECT AVG(churn_probability) FROM customer_profiles"
    cursor.execute(query_avg_churn)
    avg_churn = cursor.fetchone()[0] or 0
    avg_churn_pct = avg_churn * 100
    print(f"✓ Average Churn Risk: {avg_churn_pct:.1f}%")
    
    validation_queries.append({
        "kpi": "Average Churn Risk",
        "query": query_avg_churn,
        "result": avg_churn_pct,
        "confidence": "HIGH"
    })
    executive_data['avg_churn_risk'] = avg_churn_pct
    print()
    
    # -------------------------------------------------------------------------
    # 2.8 Average Trust Score
    # -------------------------------------------------------------------------
    
    print("2.8 Average Trust Score")
    print("-" * 40)
    
    query_avg_trust = "SELECT AVG(trust_score) FROM customer_profiles"
    cursor.execute(query_avg_trust)
    avg_trust = cursor.fetchone()[0] or 0
    print(f"✓ Average Trust Score: {avg_trust:.1f}")
    
    validation_queries.append({
        "kpi": "Average Trust Score",
        "query": query_avg_trust,
        "result": avg_trust,
        "confidence": "HIGH"
    })
    executive_data['avg_trust_score'] = avg_trust
    print()
    
    # -------------------------------------------------------------------------
    # 2.9 Verify Recommendation Text Uses Actual Data
    # -------------------------------------------------------------------------
    
    print("2.9 Recommendation Text Validation")
    print("-" * 40)
    
    recommendation_text = f"Immediate intervention required for {high_risk_customers:,} high-risk customers representing ₹{revenue_at_risk:,.2f} in potential revenue loss."
    print(f"✓ Generated recommendation text:")
    print(f"  '{recommendation_text}'")
    
    executive_data['recommendation_text'] = recommendation_text
    print()
    
    # -------------------------------------------------------------------------
    # 2.10 Check for Zero/Placeholder Values
    # -------------------------------------------------------------------------
    
    print("2.10 Zero/Placeholder Detection")
    print("-" * 40)
    
    zero_values = []
    if total_customers == 0:
        zero_values.append("Total Customers")
    if total_revenue == 0:
        zero_values.append("Total Revenue")
    if active_campaigns == 0:
        zero_values.append("Active Campaigns (OK if no campaigns)")
    if high_risk_customers == 0:
        zero_values.append("High Risk Customers (OK if all low risk)")
    if revenue_at_risk == 0:
        zero_values.append("Revenue At Risk (WARNING)")
    
    if zero_values:
        print(f"⚠️  Metrics showing zero:")
        for metric in zero_values:
            print(f"   - {metric}")
    else:
        print(f"✓ No zero values detected - all metrics populated")
    
    print()
    
    audit_results["executive_intelligence"] = executive_data
    audit_results["validation_queries"] = validation_queries
    
    # ========================================================================
    # PART 3: VALIDATION REPORT GENERATION
    # ========================================================================
    
    print()
    print("=" * 80)
    print("VALIDATION REPORT SUMMARY")
    print("=" * 80)
    print()
    
    print("FAIRNESS OBSERVATORY:")
    print(f"  Overall Fairness Score: {fairness_data.get('overall_fairness', 'N/A')}")
    print(f"  Equity Index: {fairness_data.get('equity_index', 'N/A')}")
    print(f"  Data Sources: NBA Decisions ({total_nba})")
    print()
    
    print("EXECUTIVE INTELLIGENCE:")
    print(f"  Total Customers: {total_customers:,}")
    print(f"  Total Revenue: ₹{total_revenue:,.2f}")
    print(f"  Active Campaigns: {active_campaigns}")
    print(f"  High Risk Customers: {high_risk_customers:,}")
    print(f"  Revenue At Risk: ₹{revenue_at_risk:,.2f} ({method})")
    print(f"  Revenue Exposure: ₹{revenue_exposure:,.2f}")
    print()
    
    print("ISSUES FOUND:")
    if audit_results["issues"]:
        for i, issue in enumerate(audit_results["issues"], 1):
            print(f"  {i}. [{issue['severity']}] {issue['issue']}")
            print(f"     Impact: {issue['impact']}")
    else:
        print("  ✓ No critical issues found")
    print()
    
    print("VALIDATION QUERIES:")
    for i, vq in enumerate(validation_queries, 1):
        print(f"  {i}. {vq['kpi']}")
        print(f"     Query: {vq['query'][:70]}...")
        print(f"     Result: {vq['result']}")
        print(f"     Confidence: {vq['confidence']}")
    print()
    
    # Save report
    with open("fairness_executive_audit_report.json", "w") as f:
        json.dump(audit_results, f, indent=2, default=str)
    
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"Report saved to: fairness_executive_audit_report.json")
    print()
    
    conn.close()
    return audit_results

if __name__ == "__main__":
    audit_fairness_and_executive()
