# 🏷️ Frontend Label Updates - Production Polish

**Time Required**: 30 minutes  
**Impact**: Resolves user confusion around identical revenue values  
**Priority**: High (recommended before go-live)

---

## File 1: ExecutiveSummary.tsx

**Location**: `frontend/src/pages/admin/ExecutiveSummary.tsx`  
**Lines**: 97-100

### Current Code:
```typescript
{ label: 'Revenue At Risk',         value: `₹${(data.metrics?.revenue_at_risk || 0).toLocaleString('en-IN')}`, prefix: '', color: '#F59E0B', sub: 'Non-purchaser potential' },
{ label: 'Potential Rev Loss',      value: `₹${(data.metrics?.potential_revenue_loss || 0).toLocaleString('en-IN')}`, prefix: '', color: '#EF4444', sub: 'If high-risk churn' },
{ label: 'Campaign Revenue',        value: `₹${(data.metrics?.campaign_revenue || 0).toLocaleString('en-IN')}`, prefix: '', color: '#8B5CF6', sub: 'Confirmed conversions' },
```

### Updated Code:
```typescript
{ label: 'Revenue At Risk',         value: `₹${(data.metrics?.revenue_at_risk || 0).toLocaleString('en-IN')}`, prefix: '', color: '#F59E0B', sub: 'Historical + Potential from non-purchasers' },
{ label: 'Potential Rev Loss',      value: `₹${(data.metrics?.potential_revenue_loss || 0).toLocaleString('en-IN')}`, prefix: '', color: '#EF4444', sub: 'Maximum impact if all high-risk churn' },
{ label: 'Campaign Revenue',        value: `₹${(data.metrics?.campaign_revenue || 0).toLocaleString('en-IN')}`, prefix: '', color: '#8B5CF6', sub: 'Direct conversions only (ID mismatch)' },
```

### Changes:
1. ✏️ "Revenue At Risk" subtitle: More descriptive formula explanation
2. ✏️ "Potential Rev Loss" subtitle: Clarifies this is worst-case scenario
3. ✏️ "Campaign Revenue" subtitle: Indicates limitation transparently

---

## File 2: ROICenter.tsx

**Location**: `frontend/src/pages/admin/ROICenter.tsx`  
**Line**: 193

### Current Code:
```typescript
{ label: 'Revenue at Risk', value: `₹${(roi.revenue_at_risk || 0).toLocaleString('en-IN')}`, sub: 'From potential churn', color: '#EF4444' },
```

### Updated Code:
```typescript
{ label: 'Revenue at Risk', value: `₹${(roi.revenue_at_risk || 0).toLocaleString('en-IN')}`, sub: 'From high-risk non-purchasers', color: '#EF4444' },
```

### Changes:
1. ✏️ More specific subtitle explaining the source

---

## File 3: Dashboard.tsx (Optional Enhancement)

**Location**: `frontend/src/pages/admin/Dashboard.tsx`  
**Line**: 261

### Current Code:
```typescript
<span className="text-xs font-semibold text-yellow-400">Revenue at Risk</span>
```

### Optional Enhancement:
```typescript
<div className="flex items-center gap-1">
  <span className="text-xs font-semibold text-yellow-400">Revenue at Risk</span>
  <Tooltip content="Estimated value from 1,121 high-risk non-purchasers using platform avg order value">
    <Info size={10} className="text-slate-500" />
  </Tooltip>
</div>
```

*(Requires importing Tooltip and Info components)*

---

## File 4: Add Fairness Score Tooltip (Optional)

**Location**: Create new component or add to `FairnessObservatory.tsx`

### Add Tooltip to Fairness Score Display:

```typescript
<div className="flex items-center gap-2">
  <div className="text-3xl font-bold">73/100</div>
  <Tooltip content="Fairness score measures distribution evenness across demographics, actions, and channels. Score of 73 indicates some concentration in email channel and churn_rescue actions, which is normal for targeted campaigns.">
    <Info size={16} className="text-slate-400 hover:text-purple-400 cursor-help" />
  </Tooltip>
</div>
```

---

## Testing Checklist

After making changes, verify:

- [ ] Executive Summary loads without errors
- [ ] All revenue metrics display correctly
- [ ] Subtitles are visible and readable
- [ ] ROI Center shows updated label
- [ ] No console errors
- [ ] Mobile responsive (subtitles don't overflow)

---

## Deployment Command

```bash
# Frontend rebuild
cd frontend
npm run build

# Or if using dev server, restart:
npm run dev
```

---

## Alternative: Backend Label Enhancement (Optional)

If you prefer backend-driven labels, update the API response:

**File**: `backend/app/routers/ai_router.py`  
**Line**: 442-448

```python
return {
    "summary": summary_text,
    "metrics": {
        **summary.metrics,
        # Add metadata
        "revenue_at_risk_label": "Historical + Potential from non-purchasers",
        "potential_revenue_loss_label": "Maximum impact if all high-risk churn",
        "campaign_revenue_label": "Direct conversions only",
        "campaign_revenue_confidence": "Confirmed",
        "campaign_revenue_note": "Full attribution pending customer ID mapping"
    },
    ...
}
```

Then use these in the frontend:

```typescript
{ label: 'Campaign Revenue', value: `₹${...}`, sub: data.metrics?.campaign_revenue_label || 'Confirmed conversions' }
```

---

## Visual Before/After

### Before:
```
Revenue At Risk: ₹18,56,006.77
Non-purchaser potential

Potential Rev Loss: ₹18,56,006.77  
If high-risk churn
```
*User thinks*: "These are the same... bug?"

### After:
```
Revenue At Risk: ₹18,56,006.77
Historical + Potential from non-purchasers

Potential Rev Loss: ₹18,56,006.77
Maximum impact if all high-risk churn
```
*User thinks*: "Ah, different scenarios, same current value"

---

## Summary

**Changes Required**: 3 lines of code  
**Risk Level**: Minimal (label changes only)  
**User Impact**: High (eliminates confusion)  
**Time to Deploy**: 30 minutes

**Recommendation**: Apply these changes before announcing production release.

---

*See FINAL_PRODUCTION_AUDIT_REPORT.md for complete analysis*
