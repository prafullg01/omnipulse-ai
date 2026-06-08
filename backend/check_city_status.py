import sqlite3

conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()

# Check customers table
r = c.execute("SELECT typeof(city), COUNT(*) FROM customers GROUP BY typeof(city)").fetchall()
print("Customer city types:", r)

r2 = c.execute("SELECT city FROM customers WHERE role='customer' LIMIT 5").fetchall()
print("Sample customer cities:", r2)

# Check customer_profiles table  
try:
    r3 = c.execute("SELECT typeof(city), COUNT(*) FROM customer_profiles GROUP BY typeof(city)").fetchall()
    print("Profile city types:", r3)
    r4 = c.execute("SELECT city FROM customer_profiles LIMIT 5").fetchall()
    print("Sample profile cities:", r4)
except Exception as e:
    print(f"customer_profiles has no city column: {e}")

# Check column names
cols_customers = c.execute("PRAGMA table_info(customers)").fetchall()
print("\ncustomers columns:", [col[1] for col in cols_customers])

cols_profiles = c.execute("PRAGMA table_info(customer_profiles)").fetchall()
print("customer_profiles columns:", [col[1] for col in cols_profiles])

conn.close()
