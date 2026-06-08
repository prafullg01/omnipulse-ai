"""
Create Real-Time Tracking Tables
==================================

This script creates the additional tables needed for real-time activity tracking:
- customer_sessions
- cart_items
- wishlist_items
- search_history
- product_views
"""

import sys
from sqlalchemy import inspect
from app.database.connection import engine
from app.models.realtime_models import (
    CustomerSession,
    CartItem,
    WishlistItem,
    SearchHistory,
    ProductView,
    Base
)

print("=" * 80)
print("CREATING REAL-TIME ACTIVITY TRACKING TABLES")
print("=" * 80)
print()

# Get inspector to check existing tables
inspector = inspect(engine)
existing_tables = inspector.get_table_names()

print("Current database tables:")
for table in existing_tables:
    print(f"  ✓ {table}")
print()

# Tables to create
new_tables = [
    ('customer_sessions', CustomerSession),
    ('cart_items', CartItem),
    ('wishlist_items', WishlistItem),
    ('search_history', SearchHistory),
    ('product_views', ProductView)
]

print("Creating real-time tracking tables...")
print()

created_count = 0
skipped_count = 0

for table_name, model_class in new_tables:
    if table_name in existing_tables:
        print(f"  ⊘ {table_name} - Already exists (skipping)")
        skipped_count += 1
    else:
        try:
            model_class.__table__.create(engine)
            print(f"  ✓ {table_name} - Created successfully")
            created_count += 1
        except Exception as e:
            print(f"  ✗ {table_name} - Error: {str(e)}")

print()
print("=" * 80)
print(f"SUMMARY: Created {created_count} tables, Skipped {skipped_count} existing tables")
print("=" * 80)
print()

# Verify tables were created
print("Verifying tables...")
inspector = inspect(engine)
existing_tables = inspector.get_table_names()

for table_name, _ in new_tables:
    if table_name in existing_tables:
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        print(f"  ✓ {table_name} ({len(columns)} columns)")
        for col in columns:
            print(f"      - {col}")
    else:
        print(f"  ✗ {table_name} - NOT FOUND")

print()
print("=" * 80)
print("REAL-TIME TABLES SETUP COMPLETE")
print("=" * 80)
