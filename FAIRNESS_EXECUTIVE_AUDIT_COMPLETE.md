# Fairness Observatory & Executive Intelligence Audit Report

**Date**: June 4, 2026  
**Audit Tool**: `backend/audit_fairness_executive.py`  
**Status**: ✅ AUDIT COMPLETE - Issues Identified & Solutions Provided

---

## Executive Summary

Comprehensive audit of Fairness Observatory and Executive Intelligence Center reveals:
- ✅ **Fairness Observatory**: Using REAL data, properly calculated
- ⚠️ **Executive Intelligence**: Using REAL data BUT Revenue At Risk is ₹0 despite 1,121 high-risk customers
- ❌ **Critical Issue**: CLV is zero for all customers, breaking revenue-at-risk calculations

---

## 🎯 Audit Results

### FAIRNESS OBSERVATORY

| Metric | Value | Source | Status |
|--------|-------|--------|--------|
| **Overall Fairness Score** | 87.8/100 | Calculated from NBA | ✅ REAL |
| **Equity Index** | 0.878 | NBA confidence variance | ✅ REAL |
| **Gender Fairness** | 99.5/100 | 3 genders distributed evenly | ✅ EXCELLENT |
| **Age Fairness** | 94.9/100 | 5 age groups distributed evenly | ✅ EXCELLENT |
| **Action Fairness** | 66.8/100 | 5 action types (imbalanced) | ⚠️ NEEDS ATTENTION |
| **Channel Fairness** | 90.2/100 | 7 channels distributed well | ✅ GOOD |

**Data Sources**:
- NBA Decisions: 5,757 records
- Gender Distribution: Male (34.4%), Female (36.6%), Other (29.0%)
- Age Distribution: Balanced across 18-24, 25-34, 35-44, 45-54, 55+
- Action Distribution: **Imbalanced** - cross_sell (64.1%) dominates

**Bias Detection**:
- ✅ No gender bias detected
- ✅ No age bias detected  
- ⚠️ Action distribution shows imbalance (cross_sell 64%, others <20%)

**Validation**: All metrics calculated from real NBA decisions joined with customer demographics.

---

### EXECUTIVE INTELLIGENCE CENTER

| KPI | Value | SQL Query | Status |
|-----|-------|-----------|--------|
| **Total Customers** | 5,697 | `SELECT COUNT(*) FROM customers WHERE role='customer'` | ✅ REAL |
| **Total Revenue** | ₹4,198,780.71 | `SELECT SUM(total_amount) FROM orders WHERE status!='cancelled'` | ✅ REAL |
| **Active Campaigns** | 5 | `SELECT COUNT(*) FROM campaigns WHERE status='active'` | ✅ REAL |
| **High Risk Customers** | 1,121 | `SELECT COUNT(*) FROM customer_profiles WHERE churn_probability>=0.7` | ✅ REAL |
| **Avg Churn Risk** | 44.4% | `SELECT AVG(churn_probability) FROM customer_profiles` | ✅ REAL |
| **Avg Trust Score** | 86.8 | `SELECT AVG(trust_score) FROM customer_profiles` | ✅ REAL |
| **Revenue At Risk** | ₹0.00 | `SELECT SUM(clv) FROM customer_profiles WHERE churn_probability>=0.7` | ❌ **BROKEN** |
| **Revenue Exposure** | ₹0.00 | Same as Revenue At Risk | ❌ **BROKEN** |

---

## 🚨 Critical Issues Found

### Issue #1: Revenue At Risk = ₹0 (CRITICAL)

**Problem**:
```sql
-- Current calculation (BROKEN)
SELECT SUM(clv) 
FROM customer_profiles 
WHERE churn_probability >= 0.7;
-- Result: 0.00
```

**Root Cause**: CLV (Customer Lifetime Value) is 0 for ALL customers

**Evidence**:
```sql
SELECT COUNT(*) FROM customer_profiles WHERE clv > 0;
-- Result: 0

SELECT MIN(clv), MAX(clv), AVG(clv) FROM customer_profiles;
-- Result: 0.0, 0.0, 0.0
```

**Impact**:
- Revenue At Risk shows ₹0 despite 1,121 high-risk customers
- Executive recommendations say "protect ₹0 in revenue" (nonsensical)
- ROI calculations underestimate protected revenue
- Business decisions based on incomplete risk assessment

**Fix Required**: Calculate Revenue At Risk using ACTUAL order history instead of CLV

---

### Issue #2: Fairness Action Imbalance

**Problem**: cross_sell action dominates NBA recommendations (64.1%)

**Distribution**:
- cross_sell: 3,689 (64.1%) ⚠️
- re_engagement: 1,143 (19.9%)
- churn_rescue: 693 (12.0%)
- premium_upgrade: 127 (2.2%)
- loyalty_reward: 105 (1.8%)

**Impact**: Action Fairness Score only 66.8/100 (below 80 threshold)

**Root Cause**: NBA logic heavily favors cross_sell recommendations

**Recommendation**: Review NBA decision rules to balance action types

---

### Issue #3: Missing Fairness Metrics Table

**Problem**: `fairness_metrics` table does not exist

**Impact**: 
- Fairness calculations happen on-the-fly (slow)
- No historical fairness tracking
- Cannot show fairness trends over time

**Recommendation**: Create fairness_metrics table to store historical calculations

---

## 📋 Validation Queries

All SQL queries used for each KPI with results:

### 1. Total Customers
```sql
SELECT COUNT(*) 
FROM customers 
WHERE role = 'customer';
```
**Result**: 5,697  
**Confidence**: HIGH ✅

### 2. Total Revenue
```sql
SELECT SUM(total_amount) 
FROM orders 
WHERE status != 'cancelled';
```
**Result**: ₹4,198,780.71  
**Confidence**: HIGH ✅

### 3. Active Campaigns
```sql
SELECT COUNT(*) 
FROM campaigns 
WHERE status = 'active';
```
**Result**: 5  
**Confidence**: HIGH ✅

### 4. High Risk Customers
```sql
SELECT COUNT(*) 
FROM customer_profiles 
WHERE churn_probability >= 0.7;
```
**Result**: 1,121  
**Confidence**: HIGH ✅

### 5. Revenue At Risk (BROKEN)
```sql
-- Current (returns 0)
SELECT SUM(clv) 
FROM customer_profiles 
WHERE churn_probability >= 0.7;
```
**Result**: ₹0.00  
**Confidence**: LOW ❌  
**Issue**: CLV is zero for all customers

### 6. Revenue At Risk (FIXED)
```sql
-- Corrected calculation
SELECT SUM(o.total_amount)
FROM orders o
JOIN customer_profiles cp ON o.customer_id = cp.customer_id
WHERE cp.churn_probability >= 0.7
AND o.status != 'cancelled';
```
**Result**: ₹0.00  
**Confidence**: MEDIUM ⚠️  
**Finding**: High-risk customers have NO order history (they never purchased!)

### 7. Average Churn Risk
```sql
SELECT AVG(churn_probability) 
FROM customer_profiles;
```
**Result**: 44.4%  
**Confidence**: HIGH ✅

### 8. Average Trust Score
```sql
SELECT AVG(trust_score) 
FROM customer_profiles;
```
**Result**: 86.8  
**Confidence**: HIGH ✅

---

## 🔍 Deep Dive: Why Revenue At Risk = ₹0

Let me investigate further:

```sql
-- How many high-risk customers exist?
SELECT COUNT(*) FROM customer_profiles WHERE churn_probability >= 0.7;
-- Result: 1,121

-- Do any of them have orders?
SELECT COUNT(DISTINCT o.customer_id)
FROM orders o
JOIN customer_profiles cp ON o.customer_id = cp.customer_id
WHERE cp.churn_probability >= 0.7;
-- Result: 0

-- Are these customers even in the customers table?
SELECT COUNT(*)
FROM customer_profiles cp
JOIN customers c ON cp.customer_id = c.customer_id
WHERE cp.churn_probability >= 0.7;
-- Result: 1,121 (Yes, they exist)

-- Do they have purchase history?
SELECT COUNT(DISTINCT cp.customer_id)
FROM customer_profiles cp
WHERE cp.churn_probability >= 0.7
AND NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = cp.customer_id
);
-- Result: 1,121 (ALL high-risk customers have ZERO orders)
```

**FINDING**: The 1,121 high-risk customers are **non-purchasers**. They've never placed an order!

**This means**:
1. ✅ The system correctly identifies them as high-risk (likely to churn)
2. ✅ Revenue At Risk = ₹0 is ACCURATE (they have no revenue to lose)
3. ⚠️ The BUSINESS INTERPRETATION needs adjustment:
   - These are "prospects at risk" not "customers at risk"
   - Risk is "potential future revenue" not "historical revenue"
   - Different intervention strategy needed (acquisition vs retention)

---

## 💡 Recommendations

### Immediate Actions

#### 1. Fix Revenue At Risk Calculation Logic

**Current Code** (in `ai_router.py` and `analytics.py`):
```python
revenue_at_risk = db.query(func.sum(CustomerProfile.clv)).filter(
    CustomerProfile.churn_probability > 0.6
).scalar() or 0
```

**Recommended Fix**:
```python
# For customers WITH order history
revenue_at_risk_historical = db.query(func.sum(Order.total_amount)).join(
    CustomerProfile, Order.customer_id == CustomerProfile.customer_id
).filter(
    CustomerProfile.churn_probability >= 0.7,
    Order.status != "cancelled"
).scalar() or 0

# For customers WITHOUT order history (potential value)
high_risk_non_purchasers = db.query(func.count(CustomerProfile.customer_id)).filter(
    CustomerProfile.churn_probability >= 0.7,
    ~CustomerProfile.customer_id.in_(
        db.query(Order.customer_id).distinct()
    )
).scalar() or 0

# Estimated value per prospect (average order value)
avg_order_value = db.query(func.avg(Order.total_amount)).filter(
    Order.status != "cancelled"
).scalar() or 0

potential_revenue_at_risk = high_risk_non_purchasers * avg_order_value

# Total Revenue At Risk
revenue_at_risk = revenue_at_risk_historical + potential_revenue_at_risk
```

**Update Recommendation Text**:
```python
recommendation_text = (
    f"Immediate intervention required: "
    f"{high_risk_with_orders} existing customers with ₹{revenue_at_risk_historical:,.2f} in historical revenue, "
    f"plus {high_risk_non_purchasers} high-risk prospects representing ₹{potential_revenue_at_risk:,.2f} in potential revenue."
)
```

#### 2. Update Fairness Observatory Display

**Add Bias Alert Thresholds**:
```python
# In fairness_analytics endpoint
if overall_fairness < 80:
    bias_alerts.append({
        "severity": "warning",
        "message": f"Overall fairness score ({overall_fairness:.1f}) below 80 threshold",
        "recommendation": "Review action distribution - cross_sell dominates recommendations"
    })
elif overall_fairness >= 90:
    bias_alerts.append({
        "severity": "info",
        "message": "No significant bias detected",
        "recommendation": "Continue monitoring fairness metrics"
    })
```

**Improve Action Balance**:
- Review NBA logic to reduce cross_sell dominance from 64% to ~30%
- Increase diversity: churn_rescue, loyalty_reward, premium_upgrade should each be 15-20%

#### 3. Create Fairness Metrics Table

```sql
CREATE TABLE fairness_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_fairness REAL,
    gender_fairness REAL,
    age_fairness REAL,
    action_fairness REAL,
    channel_fairness REAL,
    equity_index REAL,
    total_decisions INTEGER,
    bias_alerts TEXT -- JSON array
);
```

---

## ✅ What's Working Well

### Fairness Observatory
1. ✅ Gender distribution extremely fair (99.5/100)
2. ✅ Age distribution very fair (94.9/100)
3. ✅ Channel distribution fair (90.2/100)
4. ✅ Equity Index properly calculated from NBA confidence variance
5. ✅ Coverage score shows 100% of customers have NBA recommendations
6. ✅ Real-time bias detection for gender and age in predictions
7. ✅ All calculations use REAL database data, not hardcoded values

### Executive Intelligence
1. ✅ Total Customers accurate (5,697)
2. ✅ Total Revenue accurate (₹4,198,780.71)
3. ✅ Active Campaigns accurate (5)
4. ✅ High Risk Customers accurate (1,121)
5. ✅ Average metrics (churn, trust) accurate
6. ✅ All SQL queries traceable and validated
7. ✅ No hardcoded placeholder values

---

## 📊 Fairness Score Interpretation

| Score Range | Interpretation | Status |
|-------------|----------------|--------|
| **90-100** | Excellent - No bias detected | Gender (99.5), Age (94.9), Channel (90.2) |
| **80-89** | Good - Minor imbalances | Overall (87.8) |
| **70-79** | Fair - Needs monitoring | |
| **60-69** | Poor - Bias detected | Action (66.8) ⚠️ |
| **<60** | Critical - Significant bias | None |

**Overall Assessment**: Fairness Observatory receives a **B+ grade**. Demographic fairness is excellent, but action type distribution needs rebalancing.

---

## 📁 Generated Files

1. **audit_fairness_executive.py** - Comprehensive audit tool
2. **fairness_executive_audit_report.json** - Machine-readable results
3. **This document** - Human-readable analysis

---

## 🎯 Action Items

### Priority 1 (Critical)
- [ ] Fix Revenue At Risk calculation to use order history + potential value
- [ ] Update Executive Summary recommendation text
- [ ] Test updated revenue calculations

### Priority 2 (High)
- [ ] Rebalance NBA action distribution (reduce cross_sell from 64% to ~30%)
- [ ] Add dynamic bias alerts to Fairness Observatory UI
- [ ] Create fairness_metrics table for historical tracking

### Priority 3 (Medium)
- [ ] Add Revenue At Risk breakdown (historical vs potential)
- [ ] Show prospect vs customer segments in Executive Intelligence
- [ ] Add fairness trend charts (requires historical data)

---

## 🏆 Final Verdict

**Fairness Observatory**: ✅ VALIDATED - Using real data, properly calculated  
**Executive Intelligence**: ⚠️ PARTIALLY VALIDATED - Real data but Revenue At Risk needs context  

**Overall Grade**: B+ (87/100)

**Key Insight**: The system is honest - Revenue At Risk truly is ₹0 because high-risk customers are non-purchasers. The fix isn't to fabricate numbers but to reframe the metric as "potential revenue at risk from prospect churn" and calculate it using average order value estimation.

---

**Next Steps**: Apply the recommended fixes to properly contextualize Revenue At Risk as a combination of historical customer revenue + potential prospect value.
