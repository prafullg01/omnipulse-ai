import sqlite3
c = sqlite3.connect('omnipulse.db')
r = c.execute("SELECT typeof(city), COUNT(*) FROM customers GROUP BY typeof(city)").fetchall()
print("City types:", r)
s = c.execute("SELECT city, COUNT(*) as cnt FROM customers WHERE role='customer' GROUP BY city ORDER BY cnt DESC LIMIT 10").fetchall()
print("Top cities:", s)
p = c.execute("SELECT city, COUNT(*) as cnt FROM customer_profiles GROUP BY city ORDER BY cnt DESC LIMIT 10").fetchall()
print("Profile top cities:", p)
c.close()
