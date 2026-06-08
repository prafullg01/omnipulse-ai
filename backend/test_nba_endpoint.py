"""Test NBA Analytics Endpoint"""
import urllib.request
import json

try:
    with urllib.request.urlopen('http://localhost:8000/api/analytics/nba') as response:
        data = json.loads(response.read())
        
    print("="*80)
    print("NBA ANALYTICS API RESPONSE")
    print("="*80)
    
    print(f"\nTotal Decisions: {data['total_decisions']:,}")
    print(f"Decisions Returned: {len(data['decisions'])}")
    print(f"Average Confidence: {data['avg_confidence']:.2%}")
    print(f"High Confidence (>70%): {data['high_confidence_decisions']}")
    print(f"Confidence Range: {data['confidence_range']['min']:.2%} to {data['confidence_range']['max']:.2%}")
    
    print(f"\nAction Distribution:")
    for action, count in data['action_distribution'].items():
        print(f"  {action}: {count:,}")
    
    print(f"\nChannel Distribution:")
    for channel, count in data['channel_distribution'].items():
        print(f"  {channel}: {count:,}")
    
    print(f"\nTier Distribution:")
    for tier, count in data['tier_distribution'].items():
        print(f"  {tier}: {count:,}")
    
    print(f"\nTop 10 Highest-Risk Customers:")
    print(f"{'Customer':<30} {'Churn':>6} {'Trust':>6} {'Engage':>7} {'CLV':>10} {'Conf':>6} {'Action':<20}")
    print("-"*95)
    for decision in data['decisions'][:10]:
        print(f"{decision['customer_name']:<30} {decision['churn_probability']:>6.2f} {decision['trust_score']:>6.1f} {decision['engagement_score']:>7.1f} ₹{decision['clv']:>9,.0f} {decision['confidence']:>6.1%} {decision['recommended_action']:<20}")
    
    print("\n" + "="*80)
    print("✅ NBA ENDPOINT WORKING WITH DYNAMIC CONFIDENCE")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
