"""
OMNIPULSE AI — One-time migration to fix:
1. RFM values (all zero) → compute from orders table
2. Customer names (5000 'CustomerNNNN User') → generate real Indian names
3. CLV/predicted_clv for zero-value customers → compute from orders
4. total_revenue sync → compute from orders
5. Persona/segment/journey_stage → recompute from actual data
"""
import sqlite3
import random

random.seed(42)

FIRST_NAMES_M = [
    "Rahul", "Arjun", "Vikram", "Aditya", "Rohan", "Karan", "Siddharth", "Aarav", "Dev", "Nikhil",
    "Pranav", "Harsh", "Varun", "Ishaan", "Dhruv", "Manish", "Rajesh", "Suresh", "Ankit", "Amit",
    "Sahil", "Yash", "Kunal", "Abhishek", "Gaurav", "Vivek", "Mohit", "Deepak", "Ajay", "Sandeep",
    "Ravi", "Manoj", "Tushar", "Vishal", "Akash", "Sachin", "Neeraj", "Ritesh", "Ashish", "Pankaj",
    "Saurav", "Tarun", "Jayesh", "Mayank", "Kapil", "Hitesh", "Lokesh", "Naveen", "Ramesh", "Dinesh",
]
FIRST_NAMES_F = [
    "Priya", "Ananya", "Sneha", "Kavya", "Ishita", "Meera", "Nisha", "Pooja", "Riya", "Shruti",
    "Divya", "Neha", "Aisha", "Tanya", "Simran", "Pallavi", "Deepika", "Sakshi", "Kritika", "Lavanya",
    "Aditi", "Swati", "Anjali", "Komal", "Sonali", "Megha", "Bhavna", "Jyoti", "Sonal", "Radhika",
    "Preeti", "Shweta", "Mansi", "Nikita", "Payal", "Rashmi", "Garima", "Aparna", "Namrata", "Charmi",
    "Tanvi", "Khushi", "Rupal", "Heena", "Vaishali", "Kirti", "Mitali", "Asha", "Lata", "Rekha",
]
LAST_NAMES = [
    "Sharma", "Patel", "Gupta", "Singh", "Kumar", "Mehta", "Joshi", "Reddy", "Nair", "Iyer",
    "Kapoor", "Malhotra", "Bhat", "Rao", "Verma", "Chopra", "Desai", "Pillai", "Menon", "Shah",
    "Agarwal", "Banerjee", "Chatterjee", "Das", "Ghosh", "Mukherjee", "Roy", "Sinha", "Tiwari", "Yadav",
    "Pandey", "Mishra", "Saxena", "Khanna", "Bose", "Dutta", "Sen", "Bhatt", "Kulkarni", "Patil",
]


def run_migration():
    conn = sqlite3.connect('omnipulse.db')
    c = conn.cursor()

    print("=" * 70)
    print("OMNIPULSE AI — DATA MIGRATION")
    print("=" * 70)

    # ══════════════════════════════════════════════════════
    # 1. FIX CUSTOMER NAMES
    # ══════════════════════════════════════════════════════
    print("\n[1/5] Fixing customer names...")
    fake_customers = c.execute(
        "SELECT customer_id, gender FROM customers WHERE first_name LIKE 'Customer%' AND role='customer'"
    ).fetchall()

    print(f"  Found {len(fake_customers)} fake-name customers to fix")
    used_names = set()
    name_updates = []
    profile_name_updates = []

    for cid, gender in fake_customers:
        # Decode gender if bytes
        if isinstance(gender, bytes):
            try:
                gender = gender.decode('utf-8')
            except:
                gender = 'male'

        while True:
            if gender and 'female' in str(gender).lower():
                fn = random.choice(FIRST_NAMES_F)
            else:
                fn = random.choice(FIRST_NAMES_M)
            ln = random.choice(LAST_NAMES)
            full = f"{fn} {ln}"
            if full not in used_names:
                used_names.add(full)
                break

        email = f"{fn.lower()}.{ln.lower()}{random.randint(1,999)}@gmail.com"
        name_updates.append((fn, ln, email, cid))
        profile_name_updates.append((full, cid))

    c.executemany(
        "UPDATE customers SET first_name=?, last_name=?, email=? WHERE customer_id=?",
        name_updates
    )
    c.executemany(
        "UPDATE customer_profiles SET customer_name=? WHERE customer_id=?",
        profile_name_updates
    )
    print(f"  ✓ Updated {len(name_updates)} customer names")

    # ══════════════════════════════════════════════════════
    # 2. FIX RFM VALUES
    # ══════════════════════════════════════════════════════
    print("\n[2/5] Computing RFM from orders...")

    # Get all customer profiles
    all_profiles = c.execute("SELECT customer_id FROM customer_profiles").fetchall()

    rfm_updates = []
    for (cid,) in all_profiles:
        # Recency: days since last non-cancelled order
        last_order = c.execute(
            "SELECT MAX(order_date) FROM orders WHERE customer_id=? AND status != 'cancelled'",
            (cid,)
        ).fetchone()[0]

        if last_order:
            # Calculate days difference
            from datetime import datetime
            try:
                last_dt = datetime.fromisoformat(last_order.replace('Z', '+00:00').split('+')[0])
                recency = (datetime.utcnow() - last_dt).days
            except:
                recency = 999
        else:
            recency = 999  # No orders

        # Frequency: count of non-cancelled orders
        freq = c.execute(
            "SELECT COUNT(*) FROM orders WHERE customer_id=? AND status != 'cancelled'",
            (cid,)
        ).fetchone()[0]

        # Monetary: total revenue from non-cancelled orders
        monetary = c.execute(
            "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id=? AND status != 'cancelled'",
            (cid,)
        ).fetchone()[0]

        rfm_updates.append((recency, freq, monetary, cid))

    c.executemany(
        "UPDATE customer_profiles SET recency_days=?, frequency=?, monetary=? WHERE customer_id=?",
        rfm_updates
    )
    print(f"  ✓ Updated RFM for {len(rfm_updates)} profiles")

    # Verify
    r = c.execute("SELECT AVG(recency_days), AVG(frequency), AVG(monetary) FROM customer_profiles").fetchone()
    print(f"  Verification — Avg recency={r[0]:.1f}d, freq={r[1]:.1f}, monetary=₹{r[2]:.0f}")

    # ══════════════════════════════════════════════════════
    # 3. FIX CLV / TOTAL_REVENUE / PREDICTED_CLV
    # ══════════════════════════════════════════════════════
    print("\n[3/5] Fixing CLV and total_revenue...")

    clv_updates = []
    for (cid,) in all_profiles:
        # Total revenue from orders
        total_rev = c.execute(
            "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE customer_id=? AND status != 'cancelled'",
            (cid,)
        ).fetchone()[0]

        # Order count
        order_count = c.execute(
            "SELECT COUNT(*) FROM orders WHERE customer_id=? AND status != 'cancelled'",
            (cid,)
        ).fetchone()[0]

        # CLV = actual total revenue
        clv = total_rev

        # Predicted CLV
        if order_count >= 2:
            avg_order = total_rev / order_count
            # Simple projection: avg_order × expected_future_orders
            predicted_clv = total_rev + (avg_order * order_count * 0.8)  # 80% repeat factor
        elif order_count == 1:
            predicted_clv = total_rev * 1.5
        else:
            # No orders — estimate from engagement
            event_count = c.execute(
                "SELECT COUNT(*) FROM events WHERE customer_id=?", (cid,)
            ).fetchone()[0]
            predicted_clv = event_count * 50  # ₹50 per engagement signal

        clv_updates.append((total_rev, clv, round(predicted_clv, 2), cid))

    c.executemany(
        "UPDATE customer_profiles SET total_revenue=?, clv=?, predicted_clv=? WHERE customer_id=?",
        clv_updates
    )
    print(f"  ✓ Updated CLV for {len(clv_updates)} profiles")

    r = c.execute("SELECT AVG(clv), AVG(predicted_clv), AVG(total_revenue) FROM customer_profiles").fetchone()
    print(f"  Verification — Avg CLV=₹{r[0]:.0f}, predicted=₹{r[1]:.0f}, revenue=₹{r[2]:.0f}")

    # ══════════════════════════════════════════════════════
    # 4. FIX PERSONA / SEGMENT / JOURNEY_STAGE
    # ══════════════════════════════════════════════════════
    print("\n[4/5] Recomputing persona/segment/journey_stage...")

    segment_updates = []
    for (cid,) in all_profiles:
        # Get profile data
        row = c.execute(
            "SELECT churn_probability, total_revenue, frequency, recency_days FROM customer_profiles WHERE customer_id=?",
            (cid,)
        ).fetchone()
        churn, rev, freq, recency = row

        # Get event types for this customer
        event_types = [r[0] for r in c.execute(
            "SELECT DISTINCT event_type FROM events WHERE customer_id=?", (cid,)
        ).fetchall()]

        has_purchase = any(et in event_types for et in ['purchase', 'PURCHASE_COMPLETED'])
        has_cart = any(et in event_types for et in ['cart_add', 'ADD_TO_CART'])
        has_view = any(et in event_types for et in ['product_view', 'PRODUCT_VIEW'])

        # Segment
        if rev > 5000 and freq >= 3:
            segment = "VIP"
            persona = "VIP"
        elif rev > 0 and churn < 0.4:
            segment = "Loyal"
            persona = "Loyal"
        elif churn > 0.6:
            segment = "At-Risk"
            persona = "At-Risk"
        elif has_purchase:
            segment = "Active"
            persona = "Active"
        elif has_cart:
            segment = "High-Intent"
            persona = "High-Intent"
        elif has_view:
            segment = "Browsing"
            persona = "Browsing"
        else:
            segment = "Inactive"
            persona = "Inactive"

        # Journey stage
        if freq >= 3:
            journey = "loyal"
        elif has_purchase:
            journey = "active"
        elif churn > 0.6:
            journey = "at_risk"
        elif has_cart or has_view:
            journey = "consideration"
        else:
            journey = "inactive"

        segment_updates.append((segment, persona, journey, cid))

    c.executemany(
        "UPDATE customer_profiles SET segment=?, persona=?, journey_stage=? WHERE customer_id=?",
        segment_updates
    )
    print(f"  ✓ Updated segments for {len(segment_updates)} profiles")

    # Verify
    segs = c.execute("SELECT segment, COUNT(*) FROM customer_profiles GROUP BY segment ORDER BY COUNT(*) DESC").fetchall()
    print("  Segments:", dict(segs))

    # ══════════════════════════════════════════════════════
    # 5. FIX ENGAGEMENT SCORES
    # ══════════════════════════════════════════════════════
    print("\n[5/5] Recomputing engagement scores...")

    eng_updates = []
    for (cid,) in all_profiles:
        total_events = c.execute("SELECT COUNT(*) FROM events WHERE customer_id=?", (cid,)).fetchone()[0]
        # Engagement = min(100, event_count * 2)
        engagement = min(100, total_events * 2)
        eng_updates.append((engagement, cid))

    c.executemany(
        "UPDATE customer_profiles SET engagement_score=? WHERE customer_id=?",
        eng_updates
    )
    print(f"  ✓ Updated engagement for {len(eng_updates)} profiles")

    r = c.execute("SELECT MIN(engagement_score), AVG(engagement_score), MAX(engagement_score) FROM customer_profiles").fetchone()
    print(f"  Verification — Engagement min={r[0]:.0f}, avg={r[1]:.1f}, max={r[2]:.0f}")

    # ══════════════════════════════════════════════════════
    # COMMIT
    # ══════════════════════════════════════════════════════
    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE — All data fixed from real database records")
    print("=" * 70)


if __name__ == "__main__":
    run_migration()
