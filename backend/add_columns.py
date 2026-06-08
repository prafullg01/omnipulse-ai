"""Add missing columns to customer_profiles table."""
import sqlite3

conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()

# Check which columns exist
existing = [col[1] for col in c.execute("PRAGMA table_info(customer_profiles)").fetchall()]
print(f"Existing columns: {existing}")

new_columns = {
    "total_revenue": "FLOAT DEFAULT 0.0",
    "customer_name": "VARCHAR(200)",
    "journey_stage": "VARCHAR(50)",
}

for col_name, col_type in new_columns.items():
    if col_name not in existing:
        print(f"  Adding column: {col_name} ({col_type})")
        c.execute(f"ALTER TABLE customer_profiles ADD COLUMN {col_name} {col_type}")
    else:
        print(f"  Column already exists: {col_name}")

conn.commit()
conn.close()
print("Done — columns added.")
