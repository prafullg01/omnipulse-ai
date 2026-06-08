import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/analytics/roi') as response:
        data = json.loads(response.read().decode())
        print("=" * 80)
        print("ROI ENDPOINT RESPONSE")
        print("=" * 80)
        print(json.dumps(data, indent=2))
        print("\n" + "=" * 80)
        print("KEY METRICS")
        print("=" * 80)
        print(f"Total Revenue: ₹{data.get('total_revenue', 0):,.2f}")
        print(f"Campaign Revenue: ₹{data.get('campaign_revenue', 0):,.2f}")
        print(f"Revenue Protected: ₹{data.get('revenue_protected', 0):,.2f}")
        print(f"Revenue At Risk: ₹{data.get('revenue_at_risk', 0):,.2f}")
        print(f"Revenue Saved: ₹{data.get('revenue_saved', 0):,.2f}")
        print(f"Campaign ROI: {data.get('campaign_roi', 0):.1f}%")
        print(f"Retention Lift: {data.get('retention_lift', 0):.1f}%")
        print(f"Conversion Lift: {data.get('conversion_lift', 0):.1f}%")
except Exception as e:
    print(f"Error: {e}")
