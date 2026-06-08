"""
Dataset Loader for OmniPulse AI
================================
This script loads your 3 CSV/Excel datasets into the OmniPulse database.

IMPORTANT: Place your 3 datasets in the 'datasets/' folder with these names:
1. customers.csv - Customer information (name, email, demographics)
2. orders.csv - Order/transaction data (customer_id, product, amount, date)
3. events.csv - Customer behavior events (customer_id, event_type, timestamp)

Supported formats: CSV, Excel (.xlsx, .xls)
"""
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal, init_db
from app.models.models import Customer, Product, Order, OrderItem, Event, CustomerProfile
from app.utils.auth import hash_password

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")


def load_file(filename):
    """Load CSV or Excel file."""
    filepath = os.path.join(DATASETS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            print(f"❌ Unsupported file format: {filename}")
            return None
        
        print(f"✓ Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
        print(f"  Columns: {', '.join(df.columns.tolist())}")
        return df
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None


def load_customers(db, df):
    """Load customer data from DataFrame."""
    if df is None:
        return
    
    print("\n📊 Loading customers...")
    count = 0
    
    # Expected columns: first_name, last_name, email, phone, city, age, gender
    for idx, row in df.iterrows():
        try:
            # Check if customer already exists
            email = row.get('email', f"customer{idx}@example.com")
            existing = db.query(Customer).filter(Customer.email == email).first()
            if existing:
                continue
            
            customer = Customer(
                first_name=row.get('first_name', row.get('name', 'Customer')).split()[0] if pd.notna(row.get('first_name', row.get('name', 'Customer'))) else 'Customer',
                last_name=row.get('last_name', row.get('name', 'Name')).split()[-1] if pd.notna(row.get('last_name', row.get('name', 'Name'))) else 'Name',
                email=email,
                password_hash=hash_password("password123"),
                phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                city=row.get('city', 'Unknown') if pd.notna(row.get('city')) else 'Unknown',
                age=int(row.get('age', 25)) if pd.notna(row.get('age')) else 25,
                gender=row.get('gender', 'other') if pd.notna(row.get('gender')) else 'other',
                role='customer',
                status='active',
            )
            db.add(customer)
            db.flush()
            
            # Create profile
            profile = CustomerProfile(
                customer_id=customer.customer_id,
                trust_score=50.0,
                happiness_score=50.0,
                engagement_score=50.0,
                segment="new",
            )
            db.add(profile)
            count += 1
            
        except Exception as e:
            print(f"  ⚠️  Row {idx} error: {e}")
            continue
    
    db.commit()
    print(f"✓ Loaded {count} customers")


def load_orders(db, df):
    """Load order data from DataFrame."""
    if df is None:
        return
    
    print("\n📊 Loading orders...")
    count = 0
    
    # Expected columns: customer_email, product_name, amount, quantity, order_date, status
    for idx, row in df.iterrows():
        try:
            # Find customer by email
            customer_email = row.get('customer_email', row.get('email'))
            customer = db.query(Customer).filter(Customer.email == customer_email).first()
            if not customer:
                continue
            
            # Create or find product
            product_name = row.get('product_name', row.get('product', 'Product'))
            product = db.query(Product).filter(Product.name == product_name).first()
            if not product:
                product = Product(
                    name=product_name,
                    category=row.get('category', 'General'),
                    description=row.get('description', ''),
                    price=float(row.get('price', row.get('amount', 1000))),
                    brand=row.get('brand', 'Generic'),
                )
                db.add(product)
                db.flush()
            
            # Create order
            order = Order(
                customer_id=customer.customer_id,
                total_amount=float(row.get('amount', row.get('total_amount', 1000))),
                status=row.get('status', 'delivered'),
                payment_method=row.get('payment_method', 'card'),
                order_date=pd.to_datetime(row.get('order_date', datetime.now())) if pd.notna(row.get('order_date')) else datetime.now(),
            )
            db.add(order)
            db.flush()
            
            # Create order item
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=int(row.get('quantity', 1)),
                price=product.price,
            )
            db.add(order_item)
            count += 1
            
        except Exception as e:
            print(f"  ⚠️  Row {idx} error: {e}")
            continue
    
    db.commit()
    print(f"✓ Loaded {count} orders")


def load_events(db, df):
    """Load event data from DataFrame."""
    if df is None:
        return
    
    print("\n📊 Loading events...")
    count = 0
    
    # Expected columns: customer_email, event_type, event_value, timestamp
    for idx, row in df.iterrows():
        try:
            # Find customer
            customer_email = row.get('customer_email', row.get('email'))
            customer = db.query(Customer).filter(Customer.email == customer_email).first()
            if not customer:
                continue
            
            event = Event(
                customer_id=customer.customer_id,
                event_type=row.get('event_type', 'page_view'),
                event_value=str(row.get('event_value', '')) if pd.notna(row.get('event_value')) else None,
                timestamp=pd.to_datetime(row.get('timestamp', datetime.now())) if pd.notna(row.get('timestamp')) else datetime.now(),
                metadata_json={}
            )
            db.add(event)
            count += 1
            
        except Exception as e:
            print(f"  ⚠️  Row {idx} error: {e}")
            continue
    
    db.commit()
    print(f"✓ Loaded {count} events")


def main():
    """Main dataset loading function."""
    print("=" * 60)
    print("OmniPulse AI - Dataset Loader")
    print("=" * 60)
    
    # Check if datasets folder exists
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)
        print(f"\n📁 Created datasets folder: {DATASETS_DIR}")
        print("\n⚠️  Please place your 3 dataset files in the 'datasets/' folder:")
        print("   1. customers.csv (or .xlsx)")
        print("   2. orders.csv (or .xlsx)")
        print("   3. events.csv (or .xlsx)")
        print("\nThen run this script again.")
        return
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Load datasets
        print("\n🔍 Looking for dataset files in:", DATASETS_DIR)
        print()
        
        # Try to load customers
        customers_df = None
        for fname in ['customers.csv', 'customers.xlsx', 'customers.xls']:
            customers_df = load_file(fname)
            if customers_df is not None:
                break
        
        # Try to load orders
        orders_df = None
        for fname in ['orders.csv', 'orders.xlsx', 'orders.xls']:
            orders_df = load_file(fname)
            if orders_df is not None:
                break
        
        # Try to load events
        events_df = None
        for fname in ['events.csv', 'events.xlsx', 'events.xls']:
            events_df = load_file(fname)
            if events_df is not None:
                break
        
        # Load data into database
        if customers_df is not None:
            load_customers(db, customers_df)
        else:
            print("\n⚠️  No customers dataset found")
        
        if orders_df is not None:
            load_orders(db, orders_df)
        else:
            print("\n⚠️  No orders dataset found")
        
        if events_df is not None:
            load_events(db, events_df)
        else:
            print("\n⚠️  No events dataset found")
        
        print("\n" + "=" * 60)
        print("✅ Dataset loading complete!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
