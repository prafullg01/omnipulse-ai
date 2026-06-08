# TRUST CENTER - SQL QUERIES REFERENCE

**All SQL queries used in Trust Center calculations**

---

## 1. AVERAGE TRUST SCORE

```sql
SELECT AVG(trust_score) 
FROM customer_profiles;
```
**Result:** 86.78

---

## 2. TRUST DISTRIBUTION

```sql
SELECT 
    SUM(CASE WHEN trust_score < 50 THEN 1 ELSE 0 END) as low,
    SUM(CASE WHEN trust_score >= 50 AND trust_score < 80 THEN 1 ELSE 0 END) as medium,
    SUM(CASE WHEN trust_score >= 80 THEN 1 ELSE 0 END) as high,
    COUNT(*) as total
FROM customer_profiles;
```
**Result:** 
- Low: 502
- Medium: 1,226
- High: 3,969
- Total: 5,697

---

## 3. TOTAL CUSTOMERS

```sql
SELECT COUNT(*) 
FROM customers 
WHERE role = 'customer';
```
**Result:** 5,697

---

## 4. PURCHASE HISTORY

```sql
SELECT 
    COUNT(DISTINCT customer_id) as customers_with_orders,
    (SELECT COUNT(*) FROM customers WHERE role='customer') as total_customers,
    ROUND(COUNT(DISTINCT customer_id) * 100.0 / 
          (SELECT COUNT(*) FROM customers WHERE role='customer'), 1) as percentage
FROM orders;
```
**Result:** 2,057 / 5,697 = 36.1%

---

## 5. PAYMENT RELIABILITY

```sql
SELECT 
    SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
    COUNT(*) as total_orders,
    ROUND(SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as percentage
FROM orders;
```
**Result:** 2,536 / 2,536 = 100.0%

---

## 6. RETURN RATE

```sql
SELECT 
    SUM(CASE WHEN status IN ('cancelled', 'refunded') THEN 1 ELSE 0 END) as returns,
    COUNT(*) as total_orders,
    ROUND(SUM(CASE WHEN status IN ('cancelled', 'refunded') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as percentage
FROM orders;
```
**Result:** 0 / 2,536 = 0.0%

---

## 7. COMPLAINT HISTORY

```sql
SELECT 
    COUNT(DISTINCT customer_id) as customers_with_complaints,
    (SELECT COUNT(*) FROM customers WHERE role='customer') as total_customers,
    ROUND(COUNT(DISTINCT customer_id) * 100.0 / 
          (SELECT COUNT(*) FROM customers WHERE role='customer'), 1) as percentage
FROM events
WHERE event_type LIKE '%complaint%';
```
**Result:** 321 / 5,697 = 5.6%

---

## 8. ENGAGEMENT LEVEL

```sql
SELECT AVG(engagement_score) 
FROM customer_profiles;
```
**Result:** 9.7

---

## 9. ACCOUNT AGE (FIXED)

```sql
WITH customer_first_orders AS (
    SELECT 
        customer_id,
        MIN(order_date) as first_order_date
    FROM orders
    GROUP BY customer_id
)
SELECT 
    COUNT(*) as mature_customers,
    (SELECT COUNT(*) FROM customers WHERE role='customer') as total_customers,
    ROUND(COUNT(*) * 100.0 / 
          (SELECT COUNT(*) FROM customers WHERE role='customer'), 1) as percentage
FROM customer_first_orders
WHERE julianday('now') - julianday(first_order_date) > 90;
```
**Result:** 2,057 / 5,697 = 36.1%

**Note:** This replaces the old query that used `registration_date`:
```sql
-- OLD (INCORRECT) - returned 0%
SELECT COUNT(*) 
FROM customers 
WHERE role='customer' 
AND registration_date < datetime('now', '-90 days');
```

---

## 10. ORDER DATE RANGE

```sql
SELECT 
    MIN(order_date) as first_order, 
    MAX(order_date) as last_order
FROM orders;
```
**Result:** 2018-01-04 to 2024-12-30

---

## 11. LOW TRUST CUSTOMERS

```sql
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name as name,
    p.trust_score,
    p.churn_probability
FROM customer_profiles p
JOIN customers c ON p.customer_id = c.customer_id
WHERE p.trust_score < 50
ORDER BY p.trust_score ASC
LIMIT 50;
```
**Result:** 502 total low trust customers (returns top 50)

---

## 12. TRUST TREND (DAILY)

For each day in the last 14 days of the dataset:

```sql
-- Get date range first
SELECT MAX(order_date) FROM orders;
-- Result: 2024-12-30

-- For each day (example: Dec 17, 2024)
SELECT 
    COUNT(DISTINCT customer_id) as active_customers
FROM orders
WHERE order_date >= '2024-12-17 00:00:00'
  AND order_date <= '2024-12-17 23:59:59';

-- If active_customers > 0, get average trust of those customers
SELECT 
    AVG(p.trust_score) as daily_trust
FROM customer_profiles p
WHERE p.customer_id IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= '2024-12-17 00:00:00'
      AND order_date <= '2024-12-17 23:59:59'
);
```

**Sample Results:**
- Dec 17: 66.9 (4 customers)
- Dec 18: 55.8 (5 customers)
- Dec 19: 53.5 (9 customers)
- Dec 20: 53.8 (3 customers)
- Dec 21: 71.3 (3 customers)

---

## PYTHON/SQLALCHEMY EQUIVALENTS

### Trust Distribution (Python)
```python
all_profiles = db.query(CustomerProfile).all()
distribution = {"low": 0, "medium": 0, "high": 0}
for p in all_profiles:
    if p.trust_score < 50:
        distribution["low"] += 1
    elif p.trust_score < 80:
        distribution["medium"] += 1
    else:
        distribution["high"] += 1
```

### Purchase History (Python)
```python
customers_with_orders = db.query(func.count(func.distinct(Order.customer_id))).scalar()
total_customers = db.query(Customer).filter(Customer.role == "customer").count()
purchase_history = (customers_with_orders / max(total_customers, 1)) * 100
```

### Account Age (Python with raw SQL)
```python
from sqlalchemy import text

mature_customers = db.execute(text("""
    WITH customer_first_orders AS (
        SELECT customer_id, MIN(order_date) as first_order_date
        FROM orders GROUP BY customer_id
    )
    SELECT COUNT(*)
    FROM customer_first_orders
    WHERE julianday('now') - julianday(first_order_date) > 90
""")).scalar()

account_age = (mature_customers / max(total_customers, 1)) * 100
```

---

## VERIFICATION QUERIES

Run these to validate Trust Center data:

### Complete Trust Dashboard Data
```sql
SELECT 
    -- Average Trust
    AVG(trust_score) as avg_trust,
    
    -- Distribution
    SUM(CASE WHEN trust_score < 50 THEN 1 ELSE 0 END) as low,
    SUM(CASE WHEN trust_score >= 50 AND trust_score < 80 THEN 1 ELSE 0 END) as medium,
    SUM(CASE WHEN trust_score >= 80 THEN 1 ELSE 0 END) as high,
    
    -- Total
    COUNT(*) as total_customers
FROM customer_profiles;
```

### All Trust Drivers in One Query
```sql
SELECT 
    -- Purchase History
    ROUND((SELECT COUNT(DISTINCT customer_id) FROM orders) * 100.0 / 
          (SELECT COUNT(*) FROM customers WHERE role='customer'), 1) as purchase_history_pct,
    
    -- Payment Reliability
    ROUND((SELECT COUNT(*) FROM orders WHERE status='delivered') * 100.0 / 
          (SELECT COUNT(*) FROM orders), 1) as payment_reliability_pct,
    
    -- Return Rate
    ROUND((SELECT COUNT(*) FROM orders WHERE status IN ('cancelled', 'refunded')) * 100.0 / 
          (SELECT COUNT(*) FROM orders), 1) as return_rate_pct,
    
    -- Complaint History
    ROUND((SELECT COUNT(DISTINCT customer_id) FROM events WHERE event_type LIKE '%complaint%') * 100.0 / 
          (SELECT COUNT(*) FROM customers WHERE role='customer'), 1) as complaint_rate_pct,
    
    -- Engagement Level
    ROUND((SELECT AVG(engagement_score) FROM customer_profiles), 1) as avg_engagement,
    
    -- Account Age
    ROUND((
        SELECT COUNT(*) FROM (
            SELECT customer_id, MIN(order_date) as first_order_date
            FROM orders GROUP BY customer_id
        ) WHERE julianday('now') - julianday(first_order_date) > 90
    ) * 100.0 / (SELECT COUNT(*) FROM customers WHERE role='customer'), 1) as account_age_pct;
```

---

## EXPECTED RESULTS

When running the complete verification query above, expect:

```
avg_trust:                 86.8
low:                       502
medium:                    1,226
high:                      3,969
total_customers:           5,697
purchase_history_pct:      36.1
payment_reliability_pct:   100.0
return_rate_pct:           0.0
complaint_rate_pct:        5.6
avg_engagement:            9.7
account_age_pct:           36.1
```

---

**End of SQL Reference**
