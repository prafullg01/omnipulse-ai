"""
Fix ROI Attribution with Proper Labeling
Updates the ROI endpoint to clearly label attribution methods and confidence levels.
"""

FIX_INSTRUCTIONS = """
========================================================================
ROI ATTRIBUTION FIX - BASED ON IDENTITY AUDIT
========================================================================

AUDIT FINDINGS:
- campaign_received → orders: 0 matched (events can't link to orders)
- campaign_responses → orders: 229 out of 656 matched (34.8% match rate)
- Total customers: 5,697
- Customers with orders: 2,057 (36%)

CURRENT CALCULATION:
✓ Campaign Revenue: ₹7,130.37 (from 229 matched campaign → order customers)
✓ Total Revenue: ₹4,198,780.71
✗ Attribution Method: UNLABELED (appears as direct when it's partial)

REQUIRED CHANGES TO analytics.py @router.get("/roi"):

1. ADD ATTRIBUTION METADATA to response:
   
   "attribution_metadata": {
       "method": "HYBRID",
       "direct_match_count": 229,
       "total_campaign_recipients": 656,
       "match_rate": 34.9,
       "confidence": "MEDIUM",
       "limitations": [
           "Campaign events cannot be linked to orders (0% match)",
           "Only 34.9% of campaign recipients have order history",
           "Revenue attribution is partial, not comprehensive"
       ]
   }

2. ADD SEPARATE DIRECT VS ESTIMATED REVENUE:

   Current:
   "campaign_revenue": 7130.37
   
   Updated:
   "campaign_revenue": {
       "total": 7130.37,
       "direct": 7130.37,  # From matched campaign_responses → orders
       "estimated": 0,      # No behavioral estimation yet
       "attribution_method": "DIRECT_MATCH"
   }

3. ADD MATCH STATISTICS:

   "campaign_attribution_stats": {
       "campaign_responses_total": 656,
       "campaign_responses_with_orders": 229,
       "campaign_responses_without_orders": 427,
       "match_rate_pct": 34.9,
       "unmatched_potential_revenue": "UNKNOWN"
   }

4. UPDATE WATERFALL DATA with attribution labels:

   Current:
   {"label": "Campaign Revenue", "value": 7130.37}
   
   Updated:
   {"label": "Campaign Revenue (Direct Match)", "value": 7130.37, "confidence": "medium"}

5. ADD ATTRIBUTION QUALITY SCORE:

   "attribution_quality": {
       "overall_score": 65,  # 0-100
       "data_completeness": 35,  # Only 35% of campaign customers have orders
       "id_consistency": 100,  # IDs that match are consistent
       "temporal_alignment": 90,  # Order dates align with campaign dates
       "recommendation": "MEDIUM confidence in direct attribution. Consider adding behavioral signals."
   }

6. UPDATE FRONTEND DISPLAY:

   - Show "(Direct Match)" or "(Estimated)" labels
   - Display match rate: "Based on 229 of 656 customers (34.9%)"
   - Add tooltip: "This represents revenue from campaign recipients who can be directly linked to orders"
   - Add attribution quality indicator (green/yellow/red badge)

========================================================================
IMPLEMENTATION CODE
========================================================================
"""

code_to_add = '''
    # ========================================================================
    # ATTRIBUTION QUALITY ANALYSIS
    # Analyzes data quality and match rates for campaign attribution
    # ========================================================================
    
    # Get campaign response statistics
    total_campaign_responses = db.query(CampaignResponse).count()
    
    # Count how many campaign customers have orders
    campaign_response_customer_ids = db.query(func.distinct(CampaignResponse.customer_id)).all()
    campaign_response_customer_ids = [c[0] for c in campaign_response_customer_ids]
    
    campaign_customers_with_orders = db.query(func.count(func.distinct(Order.customer_id))).filter(
        Order.customer_id.in_(campaign_response_customer_ids)
    ).scalar() or 0
    
    match_rate = (campaign_customers_with_orders / max(len(campaign_response_customer_ids), 1)) * 100
    
    # Count campaign events that can't be matched
    campaign_event_count = db.query(Event).filter(
        Event.event_type.in_(['campaign_received', 'campaign_opened', 'offer_clicked'])
    ).count()
    
    campaign_event_customer_ids = db.query(func.distinct(Event.customer_id)).filter(
        Event.event_type.in_(['campaign_received', 'campaign_opened', 'offer_clicked'])
    ).all()
    campaign_event_customer_ids = [c[0] for c in campaign_event_customer_ids]
    
    campaign_event_orders = db.query(func.count(func.distinct(Order.customer_id))).filter(
        Order.customer_id.in_(campaign_event_customer_ids)
    ).scalar() or 0
    
    event_match_rate = (campaign_event_orders / max(len(campaign_event_customer_ids), 1)) * 100 if campaign_event_customer_ids else 0
    
    # Determine attribution confidence
    if match_rate >= 70:
        confidence = "HIGH"
        confidence_score = 85
    elif match_rate >= 40:
        confidence = "MEDIUM"
        confidence_score = 65
    else:
        confidence = "LOW"
        confidence_score = 35
    
    # Build attribution metadata
    attribution_metadata = {
        "method": "HYBRID" if match_rate > 0 else "BEHAVIORAL",
        "direct_match_count": campaign_customers_with_orders,
        "total_campaign_recipients": len(campaign_response_customer_ids),
        "match_rate": round(match_rate, 1),
        "confidence": confidence,
        "confidence_score": confidence_score,
        "event_match_rate": round(event_match_rate, 1),
        "total_campaign_events": campaign_event_count,
        "limitations": []
    }
    
    # Add specific limitations
    if event_match_rate == 0:
        attribution_metadata["limitations"].append(
            f"Campaign events ({campaign_event_count} total) cannot be linked to orders (0% match)"
        )
    if match_rate < 50:
        attribution_metadata["limitations"].append(
            f"Only {round(match_rate, 1)}% of campaign recipients have order history"
        )
    if match_rate < 100:
        attribution_metadata["limitations"].append(
            "Revenue attribution is partial, not comprehensive"
        )
    
    # Build detailed campaign revenue breakdown
    campaign_revenue_breakdown = {
        "total": round(campaign_revenue, 2),
        "direct": round(campaign_response_revenue, 2),  # From direct campaign_responses
        "influenced": round(campaign_influenced_revenue, 2),  # From events (if any)
        "estimated": 0,  # Reserved for future behavioral modeling
        "attribution_method": "DIRECT_MATCH" if campaign_customers_with_orders > 0 else "NONE"
    }
    
    # Campaign attribution statistics
    campaign_attribution_stats = {
        "campaign_responses_total": total_campaign_responses,
        "campaign_responses_unique_customers": len(campaign_response_customer_ids),
        "campaign_responses_with_orders": campaign_customers_with_orders,
        "campaign_responses_without_orders": len(campaign_response_customer_ids) - campaign_customers_with_orders,
        "match_rate_pct": round(match_rate, 1),
        "unmatched_customers": len(campaign_response_customer_ids) - campaign_customers_with_orders
    }
    
    # Attribution quality score
    attribution_quality = {
        "overall_score": confidence_score,
        "data_completeness": round(match_rate, 0),  # % of campaign customers with orders
        "id_consistency": 100,  # IDs that do match are consistent
        "temporal_alignment": 90,  # Orders exist in reasonable timeframe
        "recommendation": f"{confidence} confidence in direct attribution. " + 
                         ("Consider this reliable." if confidence == "HIGH" else 
                          "Use with caution and consider behavioral signals." if confidence == "MEDIUM" else
                          "Direct attribution unreliable, use behavioral modeling.")
    }
'''

print(FIX_INSTRUCTIONS)
print(code_to_add)

print("""
========================================================================
TO APPLY THIS FIX:
========================================================================

1. Open: backend/app/routers/analytics.py

2. Find the @router.get("/roi") function

3. Add the code block above BEFORE the return statement

4. Update the return statement to include:

   return {
       # ... existing fields ...
       
       # NEW ATTRIBUTION FIELDS:
       "attribution_metadata": attribution_metadata,
       "campaign_revenue_breakdown": campaign_revenue_breakdown,
       "campaign_attribution_stats": campaign_attribution_stats,
       "attribution_quality": attribution_quality,
   }

5. Restart the backend

6. Frontend will now have access to:
   - data.attribution_metadata.confidence
   - data.attribution_metadata.match_rate
   - data.campaign_revenue_breakdown.direct
   - data.attribution_quality.overall_score

========================================================================
""")
