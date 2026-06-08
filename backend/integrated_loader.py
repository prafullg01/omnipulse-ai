"""
Integrated Data Loader for OmniPulse AI
=========================================
Loads data from:
1. Synthetic datasets (omnipulse_master_events.csv, ai_predictions.csv)
2. Real Indian e-commerce datasets (Flipkart, Ecommerce, etc.)

Integrates everything into the OmniPulse database.
"""
import sys
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.insert(0, '.')

from app.database.connection import SessionLocal, init_db
from app.models.models import (Customer, Product, Order, OrderItem, Event,
                                CustomerProfile, SupportTicket, Campaign, CampaignResponse)
from app.utils.auth import hash_password

print("=" * 70)
print("OMNIPULSE AI - INTEGRATED DATA LOADER")
print("=" * 70)

# Initialize database
init_db()
db = SessionLocal()

try:
    # ── STEP 1: Load synthetic master events ───────────────────────────
    print("\n[1/5] Loading synthetic master events...")
    
    events_df = pd.read_csv('datasets/omnipulse_master_events.csv')
    print(f"  Loaded {len(events_df)} events from omnipulse_master_events.csv")
    
    # Extract unique customers from events
    customers_from_events = events_df[[
        'customer_id', 'customer_name', 'age', 'gender', 'city', 'state',
        'risk_score', 'trust_score', 'happiness_score'
    ]].drop_duplicates('customer_id')
    
    print(f"  Found {len(customers_from_events)} unique customers")
    
    # Create customers
    customer_count = 0
    for _, row in customers_from_events.iterrows():
        existing = db.query(Customer).filter(Customer.customer_id == row['customer_id']).first()
        if not existing:
            names = str(row['customer_name']).split()
            customer = Customer(
                customer_id=row['customer_id'],
                first_name=names[0] if len(names) > 0 else 'Customer',
                last_name=names[1] if len(names) > 1 else 'User',
                email=f"{row['customer_id'].lower()}@omnipulse.ai",
                password_hash=hash_password("password123"),
                age=int(row['age']) if pd.notna(row['age']) else 25,
                gender=str(row['gender']).lower() if pd.notna(row['gender']) else 'other',
                city=row['city'] if pd.notna(row['city']) else 'Mumbai',
                role='customer',
                status='active'
            )
            db.add(customer)
            db.flush()
            
            # Create profile
            profile = CustomerProfile(
                customer_id=customer.customer_id,
                risk_score=float(row['risk_score']) if pd.notna(row['risk_score']) else 50.0,
                trust_score=float(row['trust_score']) if pd.notna(row['trust_score']) else 50.0,
                happiness_score=float(row['happiness_score']) if pd.notna(row['happiness_score']) else 50.0,
                segment='new'
            )
            db.add(profile)
            customer_count += 1
    
    db.commit()
    print(f"  ✓ Created {customer_count} customers with profiles")
    
    # ── STEP 2: Load products from synthetic data ──────────────────────
    print("\n[2/5] Loading products from synthetic events...")
    
    products_from_events = events_df[[
        'product_id', 'product_name', 'category'
    ]].drop_duplicates('product_id')
    
    product_count = 0
    for _, row in products_from_events.iterrows():
        existing = db.query(Product).filter(Product.product_id == row['product_id']).first()
        if not existing:
            product = Product(
                product_id=row['product_id'],
                name=row['product_name'],
                category=row['category'],
                price=1999.0,  # Default price
                brand='Generic',
                rating=4.2,
                review_count=100
            )
            db.add(product)
            product_count += 1
    
    db.commit()
    print(f"  ✓ Created {product_count} products")
    
    # ── STEP 3: Load real Flipkart products ────────────────────────────
    print("\n[3/5] Loading real Flipkart products...")
    
    try:
        flipkart_df = pd.read_csv('datasets/extracted_archive (1)/flipkart_com-ecommerce_sample.csv', nrows=5000)
        print(f"  Loaded {len(flipkart_df)} products from Flipkart dataset")
        
        flipkart_products = 0
        for idx, row in flipkart_df.iterrows():
            if idx > 500:  # Limit to 500 products
                break
            
            try:
                product_id = f"FLIP-{idx:05d}"
                existing = db.query(Product).filter(Product.product_id == product_id).first()
                if not existing:
                    # Parse price
                    price_str = str(row.get('retail_price', '1000'))
                    try:
                        price = float(price_str.replace(',', '').replace('₹', '').strip())
                    except:
                        price = 1000.0
                    
                    product = Product(
                        product_id=product_id,
                        name=str(row.get('product_name', 'Product'))[:255],
                        category=str(row.get('product_category_tree', 'General')).split('>>')[0][:100] if pd.notna(row.get('product_category_tree')) else 'General',
                        description=str(row.get('description', ''))[:500],
                        price=price,
                        brand=str(row.get('brand', 'Generic'))[:100],
                        rating=4.0,
                        review_count=50
                    )
                    db.add(product)
                    flipkart_products += 1
            except Exception as e:
                continue
        
        db.commit()
        print(f"  ✓ Added {flipkart_products} Flipkart products")
    except Exception as e:
        print(f"  ⚠️  Could not load Flipkart products: {e}")
    
    # ── STEP 4: Create events from synthetic data ──────────────────────
    print("\n[4/5] Creating customer events...")
    
    event_count = 0
    for _, row in events_df.head(10000).iterrows():  # Limit to 10k events
        customer = db.query(Customer).filter(Customer.customer_id == row['customer_id']).first()
        if customer:
            event = Event(
                customer_id=customer.customer_id,
                event_type=row['event_type'],
                event_value=row['product_name'] if pd.notna(row['product_name']) else None,
                timestamp=pd.to_datetime(row['timestamp']) if pd.notna(row['timestamp']) else datetime.now(),
                metadata_json={
                    'product_id': row['product_id'] if pd.notna(row['product_id']) else None,
                    'category': row['category'] if pd.notna(row['category']) else None,
                    'emotion': row['emotion'] if pd.notna(row['emotion']) else None,
                    'sentiment': row['sentiment'] if pd.notna(row['sentiment']) else None,
                }
            )
            db.add(event)
            event_count += 1
            
            if event_count % 1000 == 0:
                db.commit()
                print(f"  ... {event_count} events processed")
    
    db.commit()
    print(f"  ✓ Created {event_count} customer events")
    
    # ── STEP 5: Load AI predictions ─────────────────────────────────────
    print("\n[5/5] Loading AI predictions...")
    
    try:
        predictions_df = pd.read_csv('datasets/ai_predictions.csv')
        print(f"  Loaded {len(predictions_df)} AI predictions")
        
        # Update customer profiles with AI predictions
        updated = 0
        for _, row in predictions_df.iterrows():
            profile = db.query(CustomerProfile).filter(
                CustomerProfile.customer_id == row['customer_id']
            ).first()
            
            if profile:
                profile.churn_probability = float(row['churn_score']) / 100.0 if pd.notna(row['churn_score']) else 0.5
                profile.clv = float(row['clv']) if pd.notna(row['clv']) else 0.0
                profile.predicted_clv = float(row['clv']) * 1.2 if pd.notna(row['clv']) else 0.0
                profile.persona = str(row['persona']) if pd.notna(row['persona']) else 'General'
                profile.emotion = str(row['emotion']) if pd.notna(row['emotion']) else 'Neutral'
                updated += 1
        
        db.commit()
        print(f"  ✓ Updated {updated} customer profiles with AI predictions")
    except Exception as e:
        print(f"  ⚠️  Could not load AI predictions: {e}")
    
    # ── FINAL STATS ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("DATA LOADING COMPLETE!")
    print("=" * 70)
    print(f"Total Customers:  {db.query(Customer).count()}")
    print(f"Total Products:   {db.query(Product).count()}")
    print(f"Total Events:     {db.query(Event).count()}")
    print(f"Total Profiles:   {db.query(CustomerProfile).count()}")
    print("=" * 70)
    print("\n✅ All data successfully loaded into OmniPulse AI!")
    print("\n🔐 Login Credentials:")
    print("  Admin:    admin@omnipulse.ai / admin123")
    print("  Customer: Use any customer ID + password123")
    print("\n🌐 Access:")
    print("  Frontend: http://localhost:5173")
    print("  Backend:  http://localhost:8000")
    print("=" * 70)

except Exception as e:
    db.rollback()
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    raise
finally:
    db.close()
