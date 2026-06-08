import sqlite3
import json

conn = sqlite3.connect('omnipulse.db')
cursor = conn.cursor()

# Get sample events
cursor.execute('SELECT * FROM events WHERE customer_id="CUST-8B9E9885" ORDER BY timestamp DESC LIMIT 3')
cols = [d[0] for d in cursor.description]
rows = cursor.fetchall()

print("Sample Events:")
print(json.dumps([dict(zip(cols, r)) for r in rows], indent=2, default=str))

# Check product names for corruption
cursor.execute('SELECT DISTINCT event_value FROM events WHERE event_type="product_view" LIMIT 10')
print("\n\nSample Product Names:")
for row in cursor.fetchall():
    print(f"  {row[0]}")

conn.close()
