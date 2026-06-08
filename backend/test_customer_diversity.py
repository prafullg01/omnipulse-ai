"""Test Customer List Diversity"""
import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/customers') as response:
        data = json.loads(response.read())
        
    print("="*80)
    print("CUSTOMER LIST DIVERSITY TEST")
    print("="*80)
    
    print(f"\nTotal Customers Returned: {len(data)}")
    
    # Categorize by risk
    critical = [c for c in data if c['churn_probability'] > 0.80]
    high = [c for c in data if 0.60 <= c['churn_probability'] <= 0.80]
    medium = [c for c in data if 0.30 <= c['churn_probability'] < 0.60]
    low = [c for c in data if c['churn_probability'] < 0.30]
    
    print(f"\nRisk Distribution:")
    print(f"  Critical (>80%): {len(critical)}")
    print(f"  High (60-80%): {len(high)}")
    print(f"  Medium (30-60%): {len(medium)}")
    print(f"  Low (<30%): {len(low)}")
    
    # Show sample from each category
    print(f"\nSample Customers by Risk Category:")
    print(f"{'Category':<12} {'Name':<30} {'Risk %':>8} {'Trust':>6} {'Persona':<20}")
    print("-"*85)
    
    if critical:
        for c in critical[:3]:
            print(f"{'Critical':<12} {c['name']:<30} {c['churn_probability']*100:>7.1f}% {c['trust_score']:>6.0f} {c['persona']:<20}")
    
    if high:
        for c in high[:3]:
            print(f"{'High':<12} {c['name']:<30} {c['churn_probability']*100:>7.1f}% {c['trust_score']:>6.0f} {c['persona']:<20}")
    
    if medium:
        for c in medium[:3]:
            print(f"{'Medium':<12} {c['name']:<30} {c['churn_probability']*100:>7.1f}% {c['trust_score']:>6.0f} {c['persona']:<20}")
    
    if low:
        for c in low[:3]:
            print(f"{'Low':<12} {c['name']:<30} {c['churn_probability']*100:>7.1f}% {c['trust_score']:>6.0f} {c['persona']:<20}")
    
    print("\n" + "="*80)
    if len(critical) >= 8 and len(high) >= 8 and len(medium) >= 8 and len(low) >= 8:
        print("✅ CUSTOMER LIST SHOWS DIVERSE RISK LEVELS")
    else:
        print("⚠ Customer list needs more diversity")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
