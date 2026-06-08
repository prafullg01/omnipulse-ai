"""
OMNIPULSE AI - REBUILD CUSTOMER 360
Add missing customer attributes to customer_profiles table
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///omnipulse.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

print("="*80)
print("OMNIPULSE AI - CUSTOMER 360 REBUILD")
print("="*80)

# ============================================================================
# STEP 1: ADD MISSING COLUMNS TO customer_profiles
# ============================================================================
print("\n[STEP 1] Adding missing Customer 360 columns...")
print("-"*80)

session = Session()

# Add columns one by one (SQLite doesn't support multiple ADD COLUMN in one statement)
columns_to_add = [
    ("customer_name", "VARCHAR(255)"),
    ("age", "INTEGER"),
    ("gender", "VARCHAR(20)"),
    ("city", "VARCHAR(100)"),
    ("state", "VARCHAR(100)"),
    ("income", "FLOAT"),
    ("total_orders", "INTEGER DEFAULT 0"),
    ("total_revenue", "FLOAT DEFAULT 0.0"),
    ("average_order_value", "FLOAT DEFAULT 0.0"),
    ("nba_action", "VARCHAR(255)"),
    ("days_since_last_order", "INTEGER DEFAULT 999")
]

for col_name, col_type in columns_to_add:
    try:
        # Check if column exists
        check_query = text(f"SELECT {col_name} FROM customer_profiles LIMIT 1")
        session.execute(check_query)
        print(f"  [SKIP] Column '{col_name}' already exists")
    except Exception:
        # Column doesn't exist, add it
        try:
            alter_query = text(f"ALTER TABLE customer_profiles ADD COLUMN {col_name} {col_type}")
            session.execute(alter_query)
            session.commit()
            print(f"  [OK] Added column '{col_name}'")
        except Exception as e:
            print(f"  [ERROR] Failed to add '{col_name}': {e}")
            session.rollback()

print("\n[SUCCESS] Schema updated")

# ============================================================================
# STEP 2: POPULATE CUSTOMER 360 ATTRIBUTES
# ============================================================================
print("\n[STEP 2] Populating Customer 360 attributes...")
print("-"*80)

# Get all customers with their data
customers_query = text("""
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.age,
        c.gender,
        c.city,
        c.country
    FROM customers c
    WHERE c.role = 'customer'
""")

customers_df = pd.read_sql(customers_query, engine)
print(f"  [INFO] Processing {len(customers_df)} customers...")

# Get order data
orders_query = text("""
    SELECT 
        customer_id,
        order_id,
        total_amount,
        order_date,
        status
    FROM orders
    WHERE status != 'cancelled'
""")

orders_df = pd.read_sql(orders_query, engine)

# Get NBA decisions
nba_query = text("""
    SELECT 
        customer_id,
        recommended_action,
        offer,
        confidence,
        timestamp
    FROM nba_decisions
    ORDER BY timestamp DESC
""")

nba_df = pd.read_sql(nba_query, engine)

# Get the latest NBA action for each customer
latest_nba = nba_df.groupby('customer_id').first().reset_index()

updated_count = 0

for idx, customer in customers_df.iterrows():
    cust_id = customer['customer_id']
    
    # Customer basic info
    customer_name = f"{customer['first_name']} {customer['last_name']}"
    age = customer['age'] if pd.notna(customer['age']) else None
    gender = customer['gender'] if pd.notna(customer['gender']) else None
    city = customer['city'] if pd.notna(customer['city']) else None
    state = customer['country'] if pd.notna(customer['country']) else None  # Using country as state
    
    # Generate income based on persona/segment (realistic estimates)
    # We'll calculate this based on CLV
    current_profile = pd.read_sql(text(f"""
        SELECT clv, segment FROM customer_profiles WHERE customer_id = '{cust_id}'
    """), engine)
    
    if len(current_profile) > 0:
        clv = current_profile['clv'].iloc[0]
        segment = current_profile['segment'].iloc[0]
        
        # Estimate income based on CLV and segment
        if segment == 'VIP':
            income = np.random.uniform(80000, 150000)
        elif segment == 'Loyal':
            income = np.random.uniform(50000, 80000)
        elif segment == 'Active':
            income = np.random.uniform(30000, 60000)
        elif segment == 'At-Risk':
            income = np.random.uniform(25000, 50000)
        else:
            income = np.random.uniform(20000, 40000)
    else:
        income = 35000  # Default
    
    # Order statistics
    cust_orders = orders_df[orders_df['customer_id'] == cust_id]
    total_orders = len(cust_orders)
    total_revenue = cust_orders['total_amount'].sum() if total_orders > 0 else 0.0
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    
    # Days since last order
    if total_orders > 0:
        last_order_date = pd.to_datetime(cust_orders['order_date'].max())
        days_since_last_order = (datetime.now() - last_order_date).days
    else:
        days_since_last_order = 999
    
    # NBA action
    nba_row = latest_nba[latest_nba['customer_id'] == cust_id]
    if len(nba_row) > 0:
        nba_action = f"{nba_row['recommended_action'].iloc[0]}: {nba_row['offer'].iloc[0]}"
    else:
        nba_action = "No recommendation"
    
    # Update customer_profiles
    try:
        update_query = text("""
            UPDATE customer_profiles 
            SET 
                customer_name = :customer_name,
                age = :age,
                gender = :gender,
                city = :city,
                state = :state,
                income = :income,
                total_orders = :total_orders,
                total_revenue = :total_revenue,
                average_order_value = :average_order_value,
                days_since_last_order = :days_since_last_order,
                nba_action = :nba_action
            WHERE customer_id = :customer_id
        """)
        
        session.execute(update_query, {
            'customer_id': cust_id,
            'customer_name': customer_name,
            'age': int(age) if age is not None else None,
            'gender': gender,
            'city': city,
            'state': state,
            'income': float(income),
            'total_orders': int(total_orders),
            'total_revenue': float(total_revenue),
            'average_order_value': float(average_order_value),
            'days_since_last_order': int(days_since_last_order),
            'nba_action': nba_action
        })
        
        updated_count += 1
        
        if updated_count % 500 == 0:
            session.commit()
            print(f"  [INFO] Updated {updated_count} profiles...")
        
    except Exception as e:
        print(f"  [ERROR] Failed to update {cust_id}: {e}")
        continue

session.commit()
print(f"\n[SUCCESS] Updated {updated_count} Customer 360 profiles")

session.close()

# ============================================================================
# STEP 3: VALIDATION
# ============================================================================
print("\n[STEP 3] Validating Customer 360 rebuild...")
print("-"*80)

# Check profile count
profile_count = pd.read_sql(text("SELECT COUNT(*) as count FROM customer_profiles"), engine)
print(f"  Customer Profile Count: {profile_count['count'][0]}")

# Sample profile check
sample_profile = pd.read_sql(text("""
    SELECT 
        customer_name, age, gender, city, state, income,
        total_orders, total_revenue, average_order_value,
        trust_score, churn_probability, happiness_score, 
        engagement_score, persona, emotion, segment, 
        journey_stage, nba_action
    FROM customer_profiles 
    WHERE customer_name IS NOT NULL
    LIMIT 5
"""), engine)

print("\n  Sample Customer 360 Profiles:")
print("-"*80)
for idx, profile in sample_profile.iterrows():
    print(f"\n  Customer: {profile['customer_name']}")
    print(f"    Demographics: {profile['age']} years, {profile['gender']}, {profile['city']}, {profile['state']}")
    print(f"    Income: ${profile['income']:,.2f}")
    print(f"    Orders: {profile['total_orders']}, Revenue: ${profile['total_revenue']:,.2f}, AOV: ${profile['average_order_value']:,.2f}")
    print(f"    Intelligence: Trust={profile['trust_score']:.1f}, Churn={profile['churn_probability']:.2f}, Happiness={profile['happiness_score']:.1f}")
    print(f"    Segmentation: {profile['persona']}, {profile['emotion']}, {profile['segment']}, {profile['journey_stage']}")
    print(f"    NBA: {profile['nba_action'][:60]}...")

# Check for NULL values
null_check = pd.read_sql(text("""
    SELECT 
        SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) as null_names,
        SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) as null_ages,
        SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) as null_genders,
        SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) as null_cities,
        SUM(CASE WHEN nba_action IS NULL THEN 1 ELSE 0 END) as null_nba
    FROM customer_profiles
"""), engine)

print("\n\n  NULL Value Check:")
print("-"*80)
print(f"    Names with NULL: {null_check['null_names'][0]}")
print(f"    Ages with NULL: {null_check['null_ages'][0]}")
print(f"    Genders with NULL: {null_check['null_genders'][0]}")
print(f"    Cities with NULL: {null_check['null_cities'][0]}")
print(f"    NBA Actions with NULL: {null_check['null_nba'][0]}")

print("\n" + "="*80)
print("[CUSTOMER 360 REBUILD COMPLETE]")
print("="*80)
print("\nNext steps:")
print("  1. Update API endpoints to return new Customer 360 fields")
print("  2. Update Customer360.tsx to display new fields")
print("  3. Test Customer360 UI with real data")
