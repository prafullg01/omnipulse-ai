"""
Fix Revenue At Risk Calculation
Updates Executive Intelligence to properly calculate revenue at risk using:
1. Historical revenue from high-risk customers with orders
2. Potential revenue from high-risk prospects without orders
"""

FIX_CODE = '''
# ============================================================================
# FIX FOR: app/routers/ai_router.py - executive_summary function
# ============================================================================

# REPLACE THIS (line ~365):
    revenue_at_risk = db.query(func.sum(CustomerProfile.clv)).filter(CustomerProfile.churn_probability > 0.6).scalar() or 0

# WITH THIS:
    # Calculate Revenue At Risk using BOTH historical and potential revenue
    
    # 1. Historical revenue from high-risk customers WHO HAVE ORDERS
    revenue_at_risk_historical = db.query(func.sum(Order.total_amount)).join(
        CustomerProfile, Order.customer_id == CustomerProfile.customer_id
    ).filter(
        CustomerProfile.churn_probability >= 0.7,
        Order.status != "cancelled"
    ).scalar() or 0
    
    # 2. Count high-risk customers WITHOUT any orders (prospects)
    high_risk_non_purchasers = db.query(func.count(CustomerProfile.customer_id)).filter(
        CustomerProfile.churn_probability >= 0.7,
        ~CustomerProfile.customer_id.in_(
            db.query(Order.customer_id).distinct()
        )
    ).scalar() or 0
    
    # 3. Estimate potential value using average order value
    avg_order_value = db.query(func.avg(Order.total_amount)).filter(
        Order.status != "cancelled"
    ).scalar() or 0
    
    potential_revenue_at_risk = high_risk_non_purchasers * avg_order_value
    
    # 4. Total Revenue At Risk = Historical + Potential
    revenue_at_risk = revenue_at_risk_historical + potential_revenue_at_risk

# ALSO UPDATE THE SUMMARY TEXT (line ~369):
    summary_text = (
        f"Executive Briefing — {datetime.utcnow().strftime(\'%B %d, %Y\')}\\n\\n"
        f"Total customers: {total_customers}. Revenue: ₹{total_revenue:,.0f}. "
        f"High-risk customers: {high_risk} ({high_risk_non_purchasers} non-purchasers). "
        f"Revenue at risk: ₹{revenue_at_risk:,.0f} (₹{revenue_at_risk_historical:,.0f} historical + ₹{potential_revenue_at_risk:,.0f} potential). "
        f"Avg happiness: {avg_happiness:.0f}/100. Active campaigns: {active_campaigns}. "
        f"Recommendation: Focus retention on existing customers (₹{revenue_at_risk_historical:,.0f}) and conversion on high-risk prospects (₹{potential_revenue_at_risk:,.0f})."
    )

# ============================================================================
# FIX FOR: app/routers/analytics.py - executive_overview function
# ============================================================================

# FIND (around line ~55):
    revenue_at_risk = db.query(func.sum(CustomerProfile.clv)).filter(
        CustomerProfile.churn_probability > 0.6
    ).scalar() or 0

# REPLACE WITH:
    # Calculate Revenue At Risk with historical + potential
    revenue_at_risk_historical = db.query(func.sum(Order.total_amount)).join(
        CustomerProfile, Order.customer_id == CustomerProfile.customer_id
    ).filter(
        CustomerProfile.churn_probability >= 0.7,
        Order.status != "cancelled"
    ).scalar() or 0
    
    high_risk_non_purchasers = db.query(func.count(CustomerProfile.customer_id)).filter(
        CustomerProfile.churn_probability >= 0.7,
        ~CustomerProfile.customer_id.in_(
            db.query(Order.customer_id).distinct()
        )
    ).scalar() or 0
    
    avg_order_value = db.query(func.avg(Order.total_amount)).filter(
        Order.status != "cancelled"
    ).scalar() or 0
    
    potential_revenue_at_risk = high_risk_non_purchasers * avg_order_value
    revenue_at_risk = revenue_at_risk_historical + potential_revenue_at_risk

# ============================================================================
# FIX FOR: app/routers/analytics.py - roi_analytics function
# ============================================================================

# FIND (around line ~510-520):
    # Revenue at risk = actual historical revenue from high-risk customers
    # (since CLV is often 0, use actual order history)
    revenue_at_risk = db.query(func.sum(Order.total_amount)).filter(
        Order.customer_id.in_(high_risk_ids),
        Order.status != "cancelled"
    ).scalar() or 0

# REPLACE WITH (keep this one as-is, but add potential revenue):
    # Revenue at risk = historical + potential
    revenue_at_risk_historical = db.query(func.sum(Order.total_amount)).filter(
        Order.customer_id.in_(high_risk_ids),
        Order.status != "cancelled"
    ).scalar() or 0
    
    # Add potential revenue from high-risk non-purchasers
    high_risk_non_purchasers = len([hid for hid in high_risk_ids if hid not in 
        [o.customer_id for o in db.query(Order.customer_id).distinct().all()]])
    
    avg_order_value = db.query(func.avg(Order.total_amount)).filter(
        Order.status != "cancelled"
    ).scalar() or 0
    
    potential_revenue_at_risk = high_risk_non_purchasers * avg_order_value
    revenue_at_risk = revenue_at_risk_historical + potential_revenue_at_risk

# ============================================================================
# FIX FOR: app/routers/ai_router.py - copilot_query function (revenue question)
# ============================================================================

# FIND (around line ~420):
    elif "revenue" in question:
        total = db.query(func.sum(Order.total_amount)).scalar() or 0
        at_risk = db.query(func.sum(CustomerProfile.clv)).filter(CustomerProfile.churn_probability > 0.6).scalar() or 0
        return {
            "answer": f"Total revenue: ₹{total:,.0f}. Revenue at risk from potential churn: ₹{at_risk:,.0f}. Recommend launching retention campaigns to protect this revenue.",
            "references": [{"type": "roi_center", "label": "View ROI Center"}],
        }

# REPLACE WITH:
    elif "revenue" in question:
        total = db.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Calculate revenue at risk properly
        at_risk_historical = db.query(func.sum(Order.total_amount)).join(
            CustomerProfile, Order.customer_id == CustomerProfile.customer_id
        ).filter(
            CustomerProfile.churn_probability >= 0.7,
            Order.status != "cancelled"
        ).scalar() or 0
        
        high_risk_non_purchasers = db.query(func.count(CustomerProfile.customer_id)).filter(
            CustomerProfile.churn_probability >= 0.7,
            ~CustomerProfile.customer_id.in_(db.query(Order.customer_id).distinct())
        ).scalar() or 0
        
        avg_order = db.query(func.avg(Order.total_amount)).filter(
            Order.status != "cancelled"
        ).scalar() or 0
        
        potential_at_risk = high_risk_non_purchasers * avg_order
        at_risk = at_risk_historical + potential_at_risk
        
        return {
            "answer": f"Total revenue: ₹{total:,.0f}. Revenue at risk: ₹{at_risk:,.0f} (₹{at_risk_historical:,.0f} from existing customers + ₹{potential_at_risk:,.0f} potential from {high_risk_non_purchasers} at-risk prospects). Recommend dual strategy: retention campaigns for existing customers and conversion campaigns for prospects.",
            "references": [{"type": "roi_center", "label": "View ROI Center"}],
        }
'''

print(FIX_CODE)

print("""
================================================================================
IMPLEMENTATION INSTRUCTIONS
================================================================================

1. Open the following files:
   - backend/app/routers/ai_router.py
   - backend/app/routers/analytics.py

2. Search for the sections marked "FIND" in the code above

3. Replace each section with the corresponding "REPLACE WITH" code

4. Save both files

5. Restart the backend server

6. Verify the changes by checking:
   - Executive Summary endpoint: GET /api/ai/executive-summary
   - Analytics Overview endpoint: GET /api/analytics/overview
   - ROI endpoint: GET /api/analytics/roi

EXPECTED RESULTS AFTER FIX:
- Revenue At Risk will show: ₹0 (historical) + ₹{avg_order * 1,121} (potential)
- For average order of ₹1,655: Revenue At Risk = ₹1,855,255
- Recommendation text will distinguish between existing customers and prospects

VERIFICATION QUERIES:
python -c "import sqlite3; conn = sqlite3.connect('backend/omnipulse.db'); 
c = conn.cursor(); 
c.execute('SELECT AVG(total_amount) FROM orders WHERE status != \\'cancelled\\''); 
print(f'Avg Order: ₹{c.fetchone()[0]:,.2f}'); 
c.execute('SELECT COUNT(*) FROM customer_profiles WHERE churn_probability >= 0.7'); 
high_risk = c.fetchone()[0]; 
print(f'High Risk: {high_risk}'); 
c.execute('SELECT AVG(total_amount) * (SELECT COUNT(*) FROM customer_profiles WHERE churn_probability >= 0.7 AND customer_id NOT IN (SELECT DISTINCT customer_id FROM orders)) FROM orders WHERE status != \\'cancelled\\''); 
print(f'Potential Revenue At Risk: ₹{c.fetchone()[0]:,.2f}')"

================================================================================
""")
