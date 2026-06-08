"""Add missing columns to customer_profiles table"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///omnipulse.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

print("Adding missing columns to customer_profiles...")

session = Session()

# List of columns to add
columns_to_add = [
    ("journey_stage", "TEXT"),
    ("favorite_category", "TEXT"),
    ("favorite_product", "TEXT"),
    ("competitive_risk", "REAL"),
    ("last_interaction", "TEXT"),
]

for column_name, column_type in columns_to_add:
    try:
        alter_query = text(f"ALTER TABLE customer_profiles ADD COLUMN {column_name} {column_type}")
        session.execute(alter_query)
        session.commit()
        print(f"  [SUCCESS] Added column: {column_name}")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print(f"  [SKIP] Column {column_name} already exists")
        else:
            print(f"  [ERROR] Failed to add {column_name}: {e}")

session.close()
print("\n[COMPLETE] Database migration finished")
