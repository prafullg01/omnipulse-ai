import sqlite3
conn = sqlite3.connect("omnipulse.db")
c = conn.cursor()

c.execute("SELECT gender, COUNT(*) FROM customers WHERE role='customer' AND gender IS NOT NULL GROUP BY gender")
rows = c.fetchall()
print("Gender distribution:", rows)

total = sum(r[1] for r in rows)
female = next((r[1] for r in rows if r[0] == 'female'), 0)
pct = female / total * 100

# THIS IS THE ACTUAL FORMULA IN analytics.py line 1244
score = min(100, 100 - abs(50 - pct) * 2)

print(f"\nFormula: 100 - abs(50 - female%) * 2")
print(f"Female count:  {female}")
print(f"Total:         {total}")
print(f"Female %:      {pct:.4f}%")
print(f"abs(50 - {pct:.2f}) = {abs(50-pct):.4f}")
print(f"* 2 = {abs(50-pct)*2:.4f}")
print(f"100 - {abs(50-pct)*2:.4f} = {score:.4f}")
print(f"\nFINAL FAIRNESS SCORE = {round(score, 1)}")

print("\n--- PROBLEM ---")
print("This formula ONLY measures gender balance (female vs 50%).")
print("It ignores: age, city, action distribution, channel distribution.")
print("It is NOT a real fairness score.")
print(f"Expected from real distribution analysis: 87.8/100")
print(f"What the UI shows: 73.0 (wrong formula)")
conn.close()
