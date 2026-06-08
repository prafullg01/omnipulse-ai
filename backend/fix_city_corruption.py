"""
Fix city data corruption in customers table.
Replaces binary blob values with realistic Indian city names.
"""
import sqlite3
import random

INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Surat", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad",
    "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
    "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
    "Amritsar", "Allahabad", "Ranchi", "Howrah", "Coimbatore",
    "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai",
    "Raipur", "Kota", "Chandigarh", "Guwahati", "Noida",
    "Mysore", "Dehradun", "Mangalore", "Thiruvananthapuram", "Kochi",
]

# Weighted distribution (metro cities more likely)
CITY_WEIGHTS = [
    12, 12, 10, 8, 8,   # Top 5 metros
    7, 7, 6, 5, 4,      # Tier 1
    3, 3, 3, 3, 3,      # Tier 2
    2, 2, 2, 2, 2,
    2, 2, 2, 2, 2,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
]

def fix_cities():
    conn = sqlite3.connect('omnipulse.db')
    c = conn.cursor()
    
    # Count corrupted
    corrupted = c.execute("SELECT COUNT(*) FROM customers WHERE typeof(city) = 'blob'").fetchone()[0]
    total = c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    
    print(f"Total customers: {total}")
    print(f"Corrupted city values: {corrupted}")
    
    if corrupted == 0:
        print("✅ No corruption found")
        conn.close()
        return
    
    # Get all corrupted customer IDs
    corrupted_rows = c.execute(
        "SELECT customer_id FROM customers WHERE typeof(city) = 'blob'"
    ).fetchall()
    
    print(f"\nFixing {len(corrupted_rows)} records with Indian city names...")
    
    for row in corrupted_rows:
        city = random.choices(INDIAN_CITIES, weights=CITY_WEIGHTS, k=1)[0]
        c.execute("UPDATE customers SET city = ? WHERE customer_id = ?", (city, row[0]))
    
    conn.commit()
    
    # Also fix customer_profiles if city is 'Unknown'
    unknown_profiles = c.execute(
        "SELECT customer_id FROM customer_profiles WHERE city = 'Unknown' OR city IS NULL"
    ).fetchall()
    
    if unknown_profiles:
        print(f"Fixing {len(unknown_profiles)} customer_profiles city values...")
        for row in unknown_profiles:
            # Try to match the city from the customers table
            cust_city = c.execute(
                "SELECT city FROM customers WHERE customer_id = ?", (row[0],)
            ).fetchone()
            if cust_city and cust_city[0]:
                c.execute(
                    "UPDATE customer_profiles SET city = ? WHERE customer_id = ?",
                    (cust_city[0], row[0])
                )
            else:
                city = random.choices(INDIAN_CITIES, weights=CITY_WEIGHTS, k=1)[0]
                c.execute(
                    "UPDATE customer_profiles SET city = ? WHERE customer_id = ?",
                    (city, row[0])
                )
        conn.commit()
    
    # Verify
    remaining = c.execute("SELECT COUNT(*) FROM customers WHERE typeof(city) = 'blob'").fetchone()[0]
    unknown_remaining = c.execute("SELECT COUNT(*) FROM customer_profiles WHERE city = 'Unknown' OR city IS NULL").fetchone()[0]
    
    print(f"\n✅ Fix complete!")
    print(f"  Remaining corrupted customers: {remaining}")
    print(f"  Remaining unknown profiles: {unknown_remaining}")
    
    # Show sample
    sample = c.execute("SELECT customer_id, city FROM customers LIMIT 10").fetchall()
    print(f"\nSample cities after fix:")
    for cid, city in sample:
        print(f"  {cid}: {city}")
    
    # City distribution
    dist = c.execute("""
        SELECT city, COUNT(*) as cnt 
        FROM customers 
        WHERE role='customer' 
        GROUP BY city 
        ORDER BY cnt DESC 
        LIMIT 15
    """).fetchall()
    print(f"\nCity distribution (top 15):")
    for city, cnt in dist:
        print(f"  {city}: {cnt}")
    
    conn.close()

if __name__ == "__main__":
    fix_cities()
