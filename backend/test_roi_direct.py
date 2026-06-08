"""Test ROI function directly to see the error"""
import sys
sys.path.insert(0, '.')

from app.database.connection import get_db
from app.routers.analytics import roi_analytics

try:
    db = next(get_db())
    result = roi_analytics(db)
    print("SUCCESS!")
    print(f"Total Revenue: ₹{result['total_revenue']:,.2f}")
    print(f"Campaign Revenue: ₹{result['campaign_revenue']:,.2f}")
    print(f"Revenue Protected: ₹{result['revenue_protected']:,.2f}")
    print(f"Revenue At Risk: ₹{result['revenue_at_risk']:,.2f}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
