# Apply Revenue At Risk Fix - Step by Step

**Estimated Time**: 10 minutes  
**Impact**: Revenue At Risk will change from ₹0 to ₹1,856,007  
**Risk Level**: LOW (additive change, no data modification)

---

## Current Problem

```
Revenue At Risk: ₹0.00
Recommendation: "protect ₹0 in potential revenue loss" ❌
```

## After Fix

```
Revenue At Risk: ₹1,856,007
Recommendation: "Focus conversion on 1,121 at-risk prospects representing ₹1,856,007 in potential revenue" ✅
```

---

## Step-by-Step Instructions

### Step 1: Open ai_router.py

Location: `backend/app/routers/ai_router.py`

**Find this code** (around line 365):
```python
revenue_at_risk = db.query(func.sum(CustomerProfile.clv)).filter(CustomerProfile.churn_probability > 0.6).scalar() or 0
```

**Replace with**:
```python
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
```

**Also find this** (around line 369):
```python
summary_text = (
    f"Executive Briefing — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
    f"Total customers: {total_customers}. Revenue: ₹{total_revenue:,.0f}. "
    f"High-risk customers: {high_risk}. Revenue at risk: ₹{revenue_at_risk:,.0f}. "
    f"Avg happiness: {avg_happiness:.0f}/100. Active campaigns: {active_campaigns}. "
    f"Recommendation: Focus retention efforts on {high_risk} high-risk customers to protect ₹{revenue_at_risk:,.0f} in revenue."
)
```

**Replace with**:
```python
summary_text = (
    f"Executive Briefing — {datetime.utcnow().strftime('%B %d, %Y')}\n\n"
    f"Total customers: {total_customers}. Revenue: ₹{total_revenue:,.0f}. "
    f"High-risk customers: {high_risk} ({high_risk_non_purchasers} non-purchasers). "
    f"Revenue at risk: ₹{revenue_at_risk:,.0f} (₹{revenue_at_risk_historical:,.0f} historical + ₹{potential_revenue_at_risk:,.0f} potential). "
    f"Avg happiness: {avg_happiness:.0f}/100. Active campaigns: {active_campaigns}. "
    f"Recommendation: Focus retention on existing customers (₹{revenue_at_risk_historical:,.0f}) and conversion on high-risk prospects (₹{potential_revenue_at_risk:,.0f})."
)
```

### Step 2: Open analytics.py

Location: `backend/app/routers/analytics.py`

**Find this code** (around line 55 in `executive_overview` function):
```python
revenue_at_risk = db.query(func.sum(CustomerProfile.clv)).filter(
    CustomerProfile.churn_probability > 0.6
).scalar() or 0
```

**Replace with**:
```python
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
```

### Step 3: Update ROI Analytics (Optional but Recommended)

In the same `analytics.py` file, **find** (around line 510-520 in `roi_analytics` function):
```python
# Revenue at risk = actual historical revenue from high-risk customers
# (since CLV is often 0, use actual order history)
revenue_at_risk = db.query(func.sum(Order.total_amount)).filter(
    Order.customer_id.in_(high_risk_ids),
    Order.status != "cancelled"
).scalar() or 0
```

**Replace with**:
```python
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
```

### Step 4: Save Files

Save both files:
- `backend/app/routers/ai_router.py`
- `backend/app/routers/analytics.py`

### Step 5: Restart Backend

**Kill existing backend processes**:
```powershell
# PowerShell
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.Path -like "*backend*"} | Stop-Process -Force
```

**Start fresh backend**:
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### Step 6: Verify the Fix

**Test Executive Summary**:
```powershell
curl http://localhost:8000/api/ai/executive-summary
```

**Expected Output** (should now show):
```json
{
  "summary": "Executive Briefing — June 04, 2026\n\nTotal customers: 5697. Revenue: ₹4,198,781. High-risk customers: 1121 (1121 non-purchasers). Revenue at risk: ₹1,856,007 (₹0 historical + ₹1,856,007 potential). ...",
  "metrics": {
    "customers": 5697,
    "revenue": 4198780.71,
    "high_risk": 1121
  }
}
```

**Test Analytics Overview**:
```powershell
curl http://localhost:8000/api/analytics/overview
```

**Expected** (should show `revenue_at_risk: 1856007`):
```json
{
  "total_customers": 5697,
  "total_revenue": 4198780.71,
  "revenue_at_risk": 1856006.77,
  ...
}
```

---

## Verification Checklist

- [ ] ai_router.py updated
- [ ] analytics.py updated  
- [ ] Both files saved
- [ ] Backend restarted
- [ ] Executive Summary shows ~₹1.86M Revenue At Risk
- [ ] Analytics Overview shows ~₹1.86M Revenue At Risk
- [ ] Recommendation text mentions "prospects" and "potential revenue"

---

## Expected Results

### Before Fix:
```
Revenue At Risk: ₹0
High Risk: 1,121 customers
Recommendation: "protect ₹0 in revenue"
```

### After Fix:
```
Revenue At Risk: ₹1,856,007
High Risk: 1,121 customers (all non-purchasers)
Breakdown:
  - Historical: ₹0 (no high-risk customers have orders)
  - Potential: ₹1,856,007 (1,121 × ₹1,655.67 avg order)
Recommendation: "Focus conversion on 1,121 at-risk prospects"
```

---

## Rollback (If Needed)

If anything goes wrong, revert by:

1. Run `git diff backend/app/routers/` to see changes
2. Run `git checkout backend/app/routers/ai_router.py backend/app/routers/analytics.py`
3. Restart backend

---

## Impact Assessment

**Business Impact**: HIGH ✅
- Executive dashboard will show meaningful Revenue At Risk
- Recommendations will distinguish prospects vs customers
- ROI calculations will include potential revenue

**Technical Risk**: LOW ✅
- Additive change (no data modification)
- Backward compatible (same endpoint structure)
- Reversible (can rollback via git)

**User Experience**: IMPROVED ✅
- Revenue At Risk makes sense (₹1.86M vs ₹0)
- Actionable recommendations
- Clear distinction between retention and conversion

---

**Ready to apply? Start with Step 1!** ✅
