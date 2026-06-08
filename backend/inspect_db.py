"""Quick DB inspection script."""
import sqlite3

conn = sqlite3.connect("omnipulse.db")
cur = conn.cursor()

# Check event type distribution
print("EVENT TYPES:")
cur.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC")
for row in cur.fetchall():
    print(f"  {row[0]:25s}: {row[1]:,}")

print()
print("CUSTOMER ID SAMPLES (from customers):")
cur.execute("SELECT customer_id FROM customers WHERE role='customer' LIMIT 10")
for row in cur.fetchall():
    print(f"  {row[0]}")

print()
print("CAMPAIGN NAMES:")
cur.execute("SELECT campaign_name, status FROM campaigns")
for row in cur.fetchall():
    print(f"  {row[0]:40s} [{row[1]}]")

print()
print("SUPPORT TICKETS:")
cur.execute("SELECT ticket_id, customer_id, sentiment, status FROM support_tickets LIMIT 10")
for row in cur.fetchall():
    print(f"  {row}")

print()
print(f"MESSAGES COUNT: {cur.execute('SELECT COUNT(*) FROM messages').fetchone()[0]}")
print(f"JOURNEYS COUNT: {cur.execute('SELECT COUNT(*) FROM journeys').fetchone()[0]}")

print()
print("JOURNEY BREAKDOWN:")
cur.execute("SELECT journey_type, journey_status, COUNT(*) FROM journeys GROUP BY journey_type, journey_status")
for row in cur.fetchall():
    print(f"  {row[0]:20s} [{row[1]:10s}]: {row[2]}")

print()
print("NBA DECISIONS BREAKDOWN:")
cur.execute("SELECT recommended_action, COUNT(*) FROM nba_decisions GROUP BY recommended_action ORDER BY COUNT(*) DESC LIMIT 10")
for row in cur.fetchall():
    print(f"  {row[0]:30s}: {row[1]}")

print()
print("ORDER STATUS DISTRIBUTION:")
cur.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
for row in cur.fetchall():
    print(f"  {row[0]:15s}: {row[1]}")

print()
print("CUSTOMER PROFILE SEGMENTS:")
cur.execute("SELECT segment, COUNT(*) FROM customer_profiles GROUP BY segment")
for row in cur.fetchall():
    print(f"  {str(row[0]):15s}: {row[1]}")

print()
print("DIGITAL TWIN RESULTS:")
cur.execute("SELECT scenario, COUNT(*) FROM digital_twin_results GROUP BY scenario")
for row in cur.fetchall():
    print(f"  {str(row[0]):15s}: {row[1]}")

conn.close()
