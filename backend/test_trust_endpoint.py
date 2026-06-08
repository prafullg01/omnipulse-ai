"""Test Trust Analytics Endpoint"""
import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/analytics/trust') as response:
        data = json.loads(response.read())
        
    print("="*80)
    print("TRUST ANALYTICS API RESPONSE")
    print("="*80)
    
    print(f"\nAverage Trust: {data['avg_trust']}")
    
    print(f"\nTrust Distribution:")
    print(f"  Low:    {data['distribution']['low']:,}")
    print(f"  Medium: {data['distribution']['medium']:,}")
    print(f"  High:   {data['distribution']['high']:,}")
    print(f"  TOTAL:  {sum(data['distribution'].values()):,}")
    
    print(f"\nTrust Drivers:")
    for driver in data['trust_drivers']:
        print(f"  {driver['label']:<25} {driver['value']:>6.1f}%")
    
    print(f"\nTrust Trend (sample):")
    for i, day in enumerate(data['trust_trend'][:5]):
        print(f"  {day['date']}: {day['trust']:.1f} (Active: {day['active_customers']})")
    print(f"  ... ({len(data['trust_trend'])} days total)")
    
    print(f"\nLow Trust Customers: {len(data['low_trust_customers'])} shown")
    
    print("\n" + "="*80)
    print("✅ API ENDPOINT WORKING CORRECTLY")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error: {e}")
