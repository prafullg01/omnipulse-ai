import sqlite3
conn = sqlite3.connect('omnipulse.db')
c = conn.cursor()
print('customer_profiles columns:')
for row in c.execute('PRAGMA table_info(customer_profiles)').fetchall():
    print(f'  {row[1]} ({row[2]})')
