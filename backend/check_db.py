import sqlite3
import os

db_path = "omnipulse.db"

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

# Get file size
size_mb = os.path.getsize(db_path) / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB\n")

# Connect and count records
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = [
    'customers', 'products', 'orders', 'order_items', 
    'events', 'support_tickets', 'campaigns', 
    'customer_profiles', 'nba_decisions', 'messages'
]

print("Record Counts:")
print("-" * 40)
for table in tables:
    try:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:20} : {count:>6,} records")
    except Exception as e:
        print(f"{table:20} : ERROR - {e}")

conn.close()
