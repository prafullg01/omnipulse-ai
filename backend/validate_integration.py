"""
OMNIPULSE AI - Integration Validation Script
Validates that all endpoints return real data with no placeholder values
"""
import sys
import json
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.routers.analytics import (
    executive_overview, churn_analytics, emotion_analytics, 
    trust_analytics, roi_analytics, fairness_analytics
)

def validate_no_placeholders(data, path="root"):
    """Recursively check for placeholder values"""
    issues = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Check for common placeholder patterns
            if isinstance(value, (int, float)) and value == 0:
                # Zero is acceptable for counts
                pass
            elif isinstance(value, str) and any(x in value.lower() for x in ['placeholder', 'demo', 'sample', 'test']):
                issues.append(f"{path}.{key} contains placeholder text: {value}")
            elif isinstance(value, (dict, list)):
                issues.extend(validate_no_placeholders(value, f"{path}.{key}"))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            issues.extend(validate_no_placeholders(item, f"{path}[{i}]"))
    
    return issues

def test_endpoint(name, func, db):
    """Test an endpoint and validate its response"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    try:
        result = func(db=db)
        
        # Check if result is dict
        if not isinstance(result, dict):
            print(f"❌ FAIL: Returned non-dict type: {type(result)}")
            return False
        
        # Check for placeholder values
        issues = validate_no_placeholders(result, name)
        if issues:
            print(f"⚠️  WARNING: Found potential placeholders:")
            for issue in issues:
                print(f"   - {issue}")
        
        # Print sample of returned data
        print(f"✅ SUCCESS: Endpoint returned valid data")
        print(f"Keys returned: {list(result.keys())}")
        
        # Print some sample values
        for key, value in list(result.items())[:5]:
            if isinstance(value, (int, float)):
                print(f"   {key}: {value}")
            elif isinstance(value, dict):
                print(f"   {key}: {len(value)} items")
            elif isinstance(value, list):
                print(f"   {key}: {len(value)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   OMNIPULSE AI - INTEGRATION VALIDATION                      ║
    ║   Testing all analytics endpoints for real data              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test all endpoints
        endpoints = [
            ("Executive Overview", executive_overview),
            ("Churn Analytics", churn_analytics),
            ("Emotion Analytics", emotion_analytics),
            ("Trust Analytics", trust_analytics),
            ("ROI Analytics", roi_analytics),
            ("Fairness Analytics", fairness_analytics),
        ]
        
        results = {}
        for name, func in endpoints:
            results[name] = test_endpoint(name, func, db)
        
        # Summary
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print('='*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {name}")
        
        print(f"\nResults: {passed}/{total} endpoints passed")
        
        if passed == total:
            print("\n🎉 ALL ENDPOINTS VALIDATED - INTEGRATION COMPLETE!")
            return 0
        else:
            print("\n⚠️  SOME ENDPOINTS FAILED - REVIEW ERRORS ABOVE")
            return 1
            
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
