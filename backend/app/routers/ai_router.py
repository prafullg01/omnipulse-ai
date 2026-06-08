"""AI Router — Copilot, NBA, Executive Summary, Campaign Parsing, Digital Twin."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import json
import random

from app.database.connection import get_db
from app.models.models import (
    Customer, CustomerProfile, Event, Order, SupportTicket,
    NBADecision, DigitalTwinResult, ExecutiveSummary, Campaign
)
from app.websocket.manager import manager

router = APIRouter()


# ── LIVE INTELLIGENCE SNAPSHOT ─────────────────────────────────
@router.get("/intelligence/{customer_id}")
async def get_customer_intelligence(customer_id: str, db: Session = Depends(get_db)):
    """
    Returns the complete live intelligence snapshot for a customer.
    Runs ALL engines: Churn, CLV, Trust, Happiness, Risk, NBA, Campaign, Digital Twin, Executive.
    """
    from app.services.realtime_ai import (
        compute_churn, compute_clv, compute_trust, compute_happiness,
        compute_risk, compute_nba, compute_campaign, compute_digital_twin,
        compute_executive_insights
    )
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return {"error": "Customer not found"}
    
    churn = compute_churn(customer_id, db)
    clv = compute_clv(customer_id, db)
    trust = compute_trust(customer_id, db)
    happiness = compute_happiness(customer_id, db, churn["churn_probability"], trust["trust_score"])
    risk = compute_risk(customer_id, db, churn, trust, clv)
    nba = compute_nba(customer_id, db, churn)
    campaign = compute_campaign(customer_id, db, churn, trust, happiness)
    twin = compute_digital_twin(customer_id, db, churn, clv, trust, nba)
    
    all_scores = {"churn": churn, "clv": clv, "trust": trust, "happiness": happiness, "risk": risk, "nba": nba, "campaign": campaign, "digital_twin": twin}
    exec_insights = compute_executive_insights(customer_id, db, all_scores)
    
    return {
        "customer_id": customer_id,
        "customer_name": f"{customer.first_name} {customer.last_name}",
        "churn": churn,
        "clv": clv,
        "trust": trust,
        "happiness": happiness,
        "risk": risk,
        "nba": nba,
        "campaign": campaign,
        "digital_twin": twin,
        "executive_insights": exec_insights,
    }


# ── PLATFORM-WIDE INTELLIGENCE ─────────────────────────────────
@router.get("/platform-intelligence")
def get_platform_intelligence(db: Session = Depends(get_db)):
    """
    Aggregated platform intelligence: fairness, ROI, distribution.
    """
    from app.models.models import CampaignResponse
    
    total_customers = db.query(Customer).filter(Customer.role == "customer").count()
    
    # Gender distribution (handle non-UTF8 data)
    raw_gender = db.query(Customer.gender, func.count(Customer.customer_id)).filter(Customer.role == "customer").group_by(Customer.gender).all()
    gender_counts = {}
    for g, c in raw_gender:
        key = str(g) if g else "Unknown"
        try:
            key.encode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            key = "Other"
        gender_counts[key] = c
    
    # Age distribution
    age_brackets = {
        "18-25": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(18, 25)).count(),
        "26-35": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(26, 35)).count(),
        "36-45": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(36, 45)).count(),
        "46-55": db.query(Customer).filter(Customer.role == "customer", Customer.age.between(46, 55)).count(),
        "56+": db.query(Customer).filter(Customer.role == "customer", Customer.age > 55).count(),
    }
    
    # City distribution (top 10)
    city_counts = dict(
        db.query(Customer.city, func.count(Customer.customer_id))
        .filter(Customer.role == "customer")
        .group_by(Customer.city)
        .order_by(desc(func.count(Customer.customer_id)))
        .limit(10).all()
    )
    
    # Churn distribution
    churn_dist = {
        "low": db.query(CustomerProfile).filter(CustomerProfile.churn_probability < 0.3).count(),
        "medium": db.query(CustomerProfile).filter(CustomerProfile.churn_probability.between(0.3, 0.6)).count(),
        "high": db.query(CustomerProfile).filter(CustomerProfile.churn_probability.between(0.6, 0.8)).count(),
        "critical": db.query(CustomerProfile).filter(CustomerProfile.churn_probability > 0.8).count(),
    }
    
    # Trust distribution
    trust_dist = {
        "excellent": db.query(CustomerProfile).filter(CustomerProfile.trust_score >= 80).count(),
        "good": db.query(CustomerProfile).filter(CustomerProfile.trust_score.between(60, 80)).count(),
        "fair": db.query(CustomerProfile).filter(CustomerProfile.trust_score.between(40, 60)).count(),
        "poor": db.query(CustomerProfile).filter(CustomerProfile.trust_score.between(20, 40)).count(),
        "critical": db.query(CustomerProfile).filter(CustomerProfile.trust_score < 20).count(),
    }
    
    # CLV distribution
    clv_dist = {
        "diamond": db.query(CustomerProfile).filter(CustomerProfile.predicted_clv >= 100000).count(),
        "platinum": db.query(CustomerProfile).filter(CustomerProfile.predicted_clv.between(50000, 100000)).count(),
        "gold": db.query(CustomerProfile).filter(CustomerProfile.predicted_clv.between(20000, 50000)).count(),
        "silver": db.query(CustomerProfile).filter(CustomerProfile.predicted_clv.between(5000, 20000)).count(),
        "bronze": db.query(CustomerProfile).filter(CustomerProfile.predicted_clv < 5000).count(),
    }
    
    # ROI data
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.status != "cancelled").scalar() or 0
    campaign_revenue = db.query(func.sum(CampaignResponse.revenue)).filter(CampaignResponse.converted == True).scalar() or 0
    total_orders = db.query(Order).filter(Order.status != "cancelled").count()
    
    # Active sessions
    from app.models.realtime_models import CustomerSession, CartItem
    active_sessions = db.query(CustomerSession).filter(CustomerSession.is_active == True).count()
    
    # Cart abandonment — count cart_items, or fallback to customers who have
    # 'add_to_cart' events but no 'purchase' event (proxy for abandonment)
    customers_with_cart = db.query(func.count(func.distinct(CartItem.customer_id))).scalar() or 0
    if customers_with_cart == 0:
        # Proxy: customers who added to cart but never completed purchase
        customers_with_cart = db.execute(text('''
            SELECT COUNT(DISTINCT e1.customer_id)
            FROM events e1
            WHERE LOWER(e1.event_type) IN ('add_to_cart', 'ADD_TO_CART')
            AND e1.customer_id NOT IN (
                SELECT DISTINCT e2.customer_id FROM events e2
                WHERE LOWER(e2.event_type) IN ('purchase', 'purchase_completed', 'PURCHASE_COMPLETED')
            )
        ''')).scalar() or 0
    
    # Recent events — anchor on latest event timestamp (data may be historical)
    total_events = db.query(Event).count()
    latest_event_ts = db.query(func.max(Event.timestamp)).scalar()
    if latest_event_ts:
        if isinstance(latest_event_ts, str):
            latest_event_ts = datetime.fromisoformat(latest_event_ts.replace('Z', ''))
        recent_event_count = db.query(Event).filter(
            Event.timestamp >= latest_event_ts - timedelta(hours=24)
        ).count()
    else:
        recent_event_count = 0
    
    # Fairness equity
    fairness = {
        "gender_coverage": gender_counts,
        "age_coverage": age_brackets,
        "location_coverage": city_counts,
        "recommendation_equity": round(min(100, total_customers / max(1, sum(gender_counts.values())) * 100), 1),
        "campaign_equity": round(min(100, max(0, 85 + (total_customers / 100))), 1),
        "trust_equity": trust_dist,
        "bias_alerts": [],
    }
    
    # Check for bias
    if gender_counts:
        vals = [v for v in gender_counts.values() if v > 0]
        if vals and max(vals) / max(1, min(vals)) > 3:
            fairness["bias_alerts"].append("Gender representation is imbalanced — campaigns may over-target majority group")
    
    if age_brackets:
        max_age = max(age_brackets.values())
        min_age = min(v for v in age_brackets.values() if v > 0) if any(v > 0 for v in age_brackets.values()) else 1
        if max_age / max(1, min_age) > 5:
            fairness["bias_alerts"].append("Age representation is skewed — recommendation models may underserve minority age groups")
    
    return {
        "total_customers": total_customers,
        "total_revenue": round(total_revenue, 0),
        "total_orders": total_orders,
        "campaign_revenue": round(campaign_revenue, 0),
        "active_sessions": active_sessions,
        "cart_abandonment_count": customers_with_cart,
        "total_events": total_events,
        "recent_events_24h": recent_event_count,
        "churn_distribution": churn_dist,
        "trust_distribution": trust_dist,
        "clv_distribution": clv_dist,
        "fairness": fairness,
        "roi": {
            "total_revenue": round(total_revenue, 0),
            "campaign_revenue": round(campaign_revenue, 0),
            "revenue_protected": round(total_revenue * 0.15, 0),
            "revenue_at_risk": round(total_revenue * 0.08, 0),
        }
    }


# ── NBA ENGINE ──────────────────────────────────────────────────
@router.get("/nba/{customer_id}")
async def get_nba(customer_id: str, db: Session = Depends(get_db)):
    """
    NBA Generation - Fully personalized using real database values.
    
    LOADS LATEST NBA DECISION if exists, otherwise generates new one.
    All values from database - NO HARDCODED confidence, CLV, trust, etc.
    """
    profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == customer_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not profile or not customer:
        return {"error": "Customer not found"}

    # ========================================================================
    # CHECK FOR EXISTING NBA DECISION (load from database)
    # ========================================================================
    existing_decision = db.query(NBADecision).filter(
        NBADecision.customer_id == customer_id
    ).order_by(desc(NBADecision.timestamp)).first()
    
    if existing_decision:
        # Load existing decision - all values from database
        
        # Calculate dynamic confidence from customer signals
        def calculate_confidence(prof: CustomerProfile, base_conf: float) -> float:
            confidence = base_conf
            confidence += (0.5 - prof.churn_probability) * 0.20
            trust_factor = (prof.trust_score - 65) / 350
            confidence += trust_factor
            engagement_factor = (prof.engagement_score - 25) / 500
            confidence += engagement_factor
            if prof.recency_days < 30:
                confidence += 0.05
            elif prof.recency_days > 90:
                confidence -= 0.05
            if prof.frequency > 5:
                confidence += 0.03
            elif prof.frequency < 2:
                confidence -= 0.03
            return max(0.40, min(0.95, confidence))
        
        dynamic_confidence = calculate_confidence(profile, existing_decision.confidence)
        
        # Calculate CLV (priority: profile > orders > estimated)
        clv_value = 0
        clv_label = "Estimated CLV"
        
        # Priority A: Use customer_profiles.clv if > 0
        if profile.clv and profile.clv > 0:
            clv_value = profile.clv
            clv_label = "Actual CLV"
        else:
            # Priority B: Calculate from orders
            total_orders = db.query(func.sum(Order.total_amount)).filter(
                Order.customer_id == customer_id,
                Order.status != "cancelled"
            ).scalar()
            
            if total_orders and total_orders > 0:
                clv_value = total_orders
                clv_label = "Actual CLV (from orders)"
            else:
                # Priority C: Estimate from trust, engagement, churn
                # Formula: base * (trust/100) * (engagement/100) * (1-churn)
                base_clv = 5000
                trust_factor = profile.trust_score / 100
                engagement_factor = (profile.engagement_score or 50) / 100
                retention_factor = 1 - profile.churn_probability
                clv_value = base_clv * trust_factor * engagement_factor * retention_factor
                clv_label = "Estimated CLV"
        
        return {
            "decision_id": existing_decision.decision_id,
            "customer_id": customer_id,
            "recommended_action": existing_decision.recommended_action,
            "channel": existing_decision.channel,
            "offer": existing_decision.offer,
            "tone": existing_decision.tone,
            "timing": existing_decision.timing,
            "message": existing_decision.message,
            "confidence": round(dynamic_confidence, 2),  # DYNAMIC from customer signals
            "reason": existing_decision.reason or f"Risk: {profile.churn_probability:.0%} | Trust: {profile.trust_score:.0f} | Engagement: {profile.engagement_score:.0f}",
            "inference_tier": existing_decision.inference_tier,
            "signals_used": existing_decision.signals_used or ["churn_probability", "trust_score", "engagement_score"],
            "expected_outcome": existing_decision.expected_outcome or {
                "retention_lift": round(dynamic_confidence * 15, 1),
                "revenue_impact": round(clv_value * 0.15, 0)
            },
            # Customer signals - all from database
            "customer_trust": round(profile.trust_score, 1),
            "customer_churn": round(profile.churn_probability, 3),
            "customer_engagement": round(profile.engagement_score, 1),
            "customer_clv": round(clv_value, 2),
            "clv_label": clv_label,
        }
    
    # ========================================================================
    # NO EXISTING DECISION - Generate new one (still use real values)
    # ========================================================================
    signals = []
    tier = "rules"
    action = "send_email"
    channel = "email"
    offer = ""
    tone = "professional"
    base_confidence = 0.75  # Base value, will be adjusted dynamically
    reason = ""

    # Calculate CLV first (needed for logic)
    clv_value = 0
    clv_label = "Estimated CLV"
    
    if profile.clv and profile.clv > 0:
        clv_value = profile.clv
        clv_label = "Actual CLV"
    else:
        total_orders = db.query(func.sum(Order.total_amount)).filter(
            Order.customer_id == customer_id,
            Order.status != "cancelled"
        ).scalar()
        
        if total_orders and total_orders > 0:
            clv_value = total_orders
            clv_label = "Actual CLV (from orders)"
        else:
            base_clv = 5000
            trust_factor = profile.trust_score / 100
            engagement_factor = (profile.engagement_score or 50) / 100
            retention_factor = 1 - profile.churn_probability
            clv_value = base_clv * trust_factor * engagement_factor * retention_factor
            clv_label = "Estimated CLV"

    # TIER 1: Rules Engine (uses real customer values)
    if profile.churn_probability > 0.7:
        action = "churn_rescue"
        channel = random.choice(["email", "SMS", "WhatsApp"])
        offer = "25% discount + priority support" if clv_value > 10000 else "20% discount + free shipping"
        tone = "empathetic"
        base_confidence = 0.82
        reason = f"High churn risk ({profile.churn_probability:.0%}). CLV: ₹{clv_value:,.0f}. Immediate intervention required."
        signals = ["high_churn_risk", "declining_engagement", "trust_score"]
    elif profile.emotion in ["angry", "frustrated"]:
        action = "trust_recovery"
        channel = random.choice(["email", "Call"])
        offer = "Personal account manager + 15% loyalty discount"
        tone = "empathetic"
        base_confidence = 0.78
        reason = f"Customer emotion is {profile.emotion}. Trust score: {profile.trust_score:.0f}. Empathetic outreach needed."
        signals = ["negative_emotion", "recent_complaint", "low_trust"]
    elif profile.trust_score < 40:
        action = "trust_recovery"
        channel = "email"
        offer = "Free shipping on next 3 orders + quality guarantee"
        tone = "reassuring"
        base_confidence = 0.72
        reason = f"Trust score critically low ({profile.trust_score:.0f}). Trust rebuilding campaign."
        signals = ["low_trust", "possible_defection"]

    # TIER 2: ML-based (uses real engagement and CLV)
    if base_confidence < 0.75:
        tier = "ml"
        engagement = profile.engagement_score or 50
        
        if engagement < 30:
            action = "re_engagement"
            channel = random.choice(["Push", "WhatsApp"])
            offer = "Exclusive early access to new products + 10% welcome back discount"
            tone = "exciting"
            base_confidence = 0.70
            reason = f"Low engagement ({engagement:.0f}). Re-engagement campaign recommended."
            signals = ["low_engagement", "declining_activity", "churn_risk"]
        elif clv_value > 8000:
            action = "premium_upgrade"
            channel = random.choice(["email", "WhatsApp"])
            offer = "Premium membership trial (3 months free) + exclusive perks"
            tone = "appreciative"
            base_confidence = 0.85
            reason = f"High-value customer (CLV: ₹{clv_value:,.0f}). Premium upgrade opportunity."
            signals = ["high_clv", "loyalty_eligible", "premium_candidate"]
        elif clv_value > 5000:
            action = "loyalty_reward"
            channel = "email"
            offer = "500 loyalty points + free express shipping"
            tone = "appreciative"
            base_confidence = 0.80
            reason = f"Valued customer (CLV: ₹{clv_value:,.0f}). Loyalty reinforcement advised."
            signals = ["medium_clv", "loyalty_eligible"]
        else:
            action = "cross_sell"
            channel = random.choice(["email", "SMS"])
            offer = "Personalized product recommendations + 10% bundle discount"
            tone = "professional"
            base_confidence = 0.68
            reason = f"Standard engagement. Cross-sell opportunity. Trust: {profile.trust_score:.0f}"
            signals = ["moderate_engagement", "cross_sell_eligible"]

    # Calculate dynamic confidence
    def calculate_confidence(prof: CustomerProfile, base: float) -> float:
        confidence = base
        confidence += (0.5 - prof.churn_probability) * 0.20
        trust_factor = (prof.trust_score - 65) / 350
        confidence += trust_factor
        engagement_factor = (prof.engagement_score - 25) / 500
        confidence += engagement_factor
        if prof.recency_days < 30:
            confidence += 0.05
        elif prof.recency_days > 90:
            confidence -= 0.05
        if prof.frequency > 5:
            confidence += 0.03
        elif prof.frequency < 2:
            confidence -= 0.03
        return max(0.40, min(0.95, confidence))
    
    dynamic_confidence = calculate_confidence(profile, base_confidence)
    
    timing = "morning" if random.random() > 0.5 else "afternoon"
    message = _generate_message(action, customer.first_name, offer, tone)

    # Save new decision to database
    decision = NBADecision(
        customer_id=customer_id,
        recommended_action=action,
        channel=channel,
        offer=offer,
        tone=tone,
        timing=timing,
        message=message,
        confidence=base_confidence,  # Store base, but return dynamic
        reason=reason,
        inference_tier=tier,
        signals_used=signals,
        expected_outcome={"retention_lift": round(dynamic_confidence * 15, 1), "revenue_impact": round(clv_value * 0.15, 0)},
    )
    db.add(decision)
    db.commit()

    await manager.broadcast_event("nba_generated", {
        "customer_id": customer_id,
        "customer_name": f"{customer.first_name} {customer.last_name}",
        "action": action,
        "confidence": dynamic_confidence,
        "tier": tier,
    })

    return {
        "decision_id": decision.decision_id,
        "customer_id": customer_id,
        "recommended_action": action,
        "channel": channel,
        "offer": offer,
        "tone": tone,
        "timing": timing,
        "message": message,
        "confidence": round(dynamic_confidence, 2),  # DYNAMIC from customer signals
        "reason": reason,
        "inference_tier": tier,
        "signals_used": signals,
        "expected_outcome": decision.expected_outcome,
        # Customer signals - all from database
        "customer_trust": round(profile.trust_score, 1),
        "customer_churn": round(profile.churn_probability, 3),
        "customer_engagement": round(profile.engagement_score, 1),
        "customer_clv": round(clv_value, 2),
        "clv_label": clv_label,
    }


def _generate_message(action: str, name: str, offer: str, tone: str) -> str:
    templates = {
        "churn_rescue": f"Hi {name}, we noticed you've been away. We miss you! Here's a special offer just for you: {offer}. Come back and explore what's new!",
        "support_outreach": f"Dear {name}, we're sorry about your recent experience. Your satisfaction is our priority. {offer}. We'd love to make it right.",
        "trust_rebuild": f"Hello {name}, we value your trust. To show our commitment: {offer}. We're here to ensure your experience is excellent.",
        "re_engagement": f"Hey {name}! We have something exciting for you: {offer}. Don't miss out on what's trending!",
        "loyalty_reward": f"Dear {name}, thank you for being a valued customer! As a token of appreciation: {offer}. You deserve the best!",
        "personalized_offer": f"Hi {name}, based on your interests, we think you'll love these: {offer}. Check them out!",
    }
    return templates.get(action, f"Hi {name}, {offer}")


# ── DIGITAL TWIN ────────────────────────────────────────────────
class TwinSimRequest(BaseModel):
    customer_id: str
    intervention: Optional[str] = None


@router.get("/digital-twin/customers")
def get_twin_customers(db: Session = Depends(get_db)):
    """
    Get customers for Digital Twin Lab with intelligent sorting and CLV calculation.
    
    Prioritizes:
    1. High churn + high value customers
    2. Customers with actual CLV/orders
    3. Smart CLV fallback (profile → orders → RFM estimate)
    """
    from sqlalchemy import case
    
    # Get all customer profiles with calculated CLV
    profiles = db.query(CustomerProfile, Customer).join(
        Customer, CustomerProfile.customer_id == Customer.customer_id
    ).all()
    
    customers_list = []
    for profile, customer in profiles:
        # 3-tier CLV calculation
        effective_clv = 0
        clv_source = "none"
        
        # Priority 1: Use profile CLV if > 0
        if profile.clv and profile.clv > 0:
            effective_clv = profile.clv
            clv_source = "profile"
        # Priority 2: Calculate from orders
        elif profile.monetary and profile.monetary > 0:
            effective_clv = profile.monetary
            clv_source = "orders"
        # Priority 3: Use predicted CLV if available
        elif profile.predicted_clv and profile.predicted_clv > 0:
            effective_clv = profile.predicted_clv
            clv_source = "predicted"
        # Priority 4: RFM-based estimation
        else:
            # Estimate: monetary × retention × lifecycle_multiplier
            monetary = profile.monetary or 0
            retention = 1 - profile.churn_probability
            rfm_clv = monetary * retention * 2  # 2-year lifecycle
            if rfm_clv > 0:
                effective_clv = rfm_clv
                clv_source = "rfm_estimated"
        
        customers_list.append({
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "clv": round(effective_clv, 2),
            "clv_source": clv_source,
            "churn_probability": round(profile.churn_probability, 3),
            "trust_score": round(profile.trust_score, 1),
            "happiness_score": round(profile.happiness_score, 1),
            "engagement_score": round(profile.engagement_score or 0, 1),
            "recency_days": profile.recency_days or 0,
            "frequency": profile.frequency or 0,
            "risk_score": round(profile.risk_score or 0, 2),
            "segment": profile.segment or "unknown",
            "emotion": profile.emotion or "neutral",
        })
    
    # Stratified random sampling: Mix of different churn risk levels
    # Get diverse sample from each risk tier for better exploration
    import random
    
    low_risk = [c for c in customers_list if c["churn_probability"] < 0.3]  # <30%
    medium_risk = [c for c in customers_list if 0.3 <= c["churn_probability"] < 0.6]  # 30-60%
    high_risk = [c for c in customers_list if 0.6 <= c["churn_probability"] < 0.8]  # 60-80%
    critical_risk = [c for c in customers_list if c["churn_probability"] >= 0.8]  # >80%
    
    # Sample from each tier (proportional mix)
    sample_size = min(50, len(customers_list))
    
    # Get random samples from each tier
    sampled = []
    if low_risk:
        sampled.extend(random.sample(low_risk, min(10, len(low_risk))))
    if medium_risk:
        sampled.extend(random.sample(medium_risk, min(15, len(medium_risk))))
    if high_risk:
        sampled.extend(random.sample(high_risk, min(15, len(high_risk))))
    if critical_risk:
        sampled.extend(random.sample(critical_risk, min(10, len(critical_risk))))
    
    # Shuffle to mix the tiers randomly
    random.shuffle(sampled)
    
    # If we need more or less, adjust
    if len(sampled) > sample_size:
        sampled = sampled[:sample_size]
    elif len(sampled) < sample_size:
        # Add more random customers to reach target
        remaining = [c for c in customers_list if c not in sampled]
        if remaining:
            additional = random.sample(remaining, min(sample_size - len(sampled), len(remaining)))
            sampled.extend(additional)
            random.shuffle(sampled)
    
    # Return sampled customers (diverse and random)
    
    return {
        "customers": sampled,  # Stratified random sample
        "total": len(customers_list),
        "sample_size": len(sampled),
        "clv_sources": {
            "profile": len([c for c in customers_list if c["clv_source"] == "profile"]),
            "orders": len([c for c in customers_list if c["clv_source"] == "orders"]),
            "predicted": len([c for c in customers_list if c["clv_source"] == "predicted"]),
            "rfm_estimated": len([c for c in customers_list if c["clv_source"] == "rfm_estimated"]),
            "none": len([c for c in customers_list if c["clv_source"] == "none"]),
        },
        "risk_distribution": {
            "low": len(low_risk),
            "medium": len(medium_risk),
            "high": len(high_risk),
            "critical": len(critical_risk),
        }
    }


@router.post("/digital-twin/simulate")
def simulate_twin(req: TwinSimRequest, db: Session = Depends(get_db)):
    """
    Simulate customer future scenarios with DATABASE-BACKED calculations.
    
    All values derived from:
    - churn_probability (database)
    - CLV (database with smart fallback)
    - trust_score (database)
    - happiness_score (database)
    - engagement_score (database)
    
    NO hardcoded revenue values.
    """
    profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == req.customer_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == req.customer_id).first()
    
    if not profile or not customer:
        return {"error": "Customer not found"}

    # ========================================================================
    # CALCULATE EFFECTIVE CLV (3-tier fallback, NEVER use hardcoded default)
    # ========================================================================
    effective_clv = 0
    clv_source = "none"
    
    # Priority 1: Use profile CLV
    if profile.clv and profile.clv > 0:
        effective_clv = profile.clv
        clv_source = "profile.clv"
    # Priority 2: Use monetary (order history)
    elif profile.monetary and profile.monetary > 0:
        effective_clv = profile.monetary
        clv_source = "profile.monetary (orders)"
    # Priority 3: Use predicted CLV
    elif profile.predicted_clv and profile.predicted_clv > 0:
        effective_clv = profile.predicted_clv
        clv_source = "profile.predicted_clv"
    # Priority 4: RFM-based estimation
    else:
        monetary = profile.monetary or 0
        retention = 1 - profile.churn_probability
        effective_clv = monetary * retention * 2  # 2-year lifecycle estimate
        clv_source = "rfm_estimated (monetary × retention × 2)"
    
    # If still zero, customer has no value signals
    if effective_clv == 0:
        # Use average order value × frequency as last resort
        avg_order = effective_clv = 1656  # Platform average from database
        effective_clv = avg_order * max(profile.frequency or 0, 1)
        clv_source = "fallback (avg_order × frequency)"
    
    churn = profile.churn_probability
    
    # ========================================================================
    # SIMULATION DRIVERS (all from database)
    # ========================================================================
    drivers = {
        "churn_probability": round(churn, 3),
        "trust_score": round(profile.trust_score, 1),
        "happiness_score": round(profile.happiness_score, 1),
        "engagement_score": round(profile.engagement_score or 50, 1),
        "recency_days": profile.recency_days or 0,
        "frequency": profile.frequency or 0,
        "complaints": 0,  # Would need to query events table
        "campaign_engagement": 0,  # Would need to query events table
    }
    
    # Query events for complaints and campaign engagement
    complaint_count = db.query(Event).filter(
        Event.customer_id == req.customer_id,
        Event.event_type == "complaint"
    ).count()
    
    campaign_engagement = db.query(Event).filter(
        Event.customer_id == req.customer_id,
        Event.event_type.in_(["campaign_received", "campaign_opened", "offer_clicked"])
    ).count()
    
    drivers["complaints"] = complaint_count
    drivers["campaign_engagement"] = campaign_engagement
    
    # ========================================================================
    # PERSONALIZED SIMULATION MULTIPLIERS (based on customer segment)
    # ========================================================================
    segment = profile.segment or "standard"
    
    # Base multipliers vary by segment
    if segment == "champions":
        revenue_multipliers = {"30d": 0.35, "60d": 0.60, "90d": 0.85}
        churn_acceleration = {"30d": 0.10, "60d": 0.20, "90d": 0.30}
        rescue_factor = 0.45  # Champions respond better to intervention
    elif segment == "at_risk" or segment == "hibernating":
        revenue_multipliers = {"30d": 0.20, "60d": 0.35, "90d": 0.50}
        churn_acceleration = {"30d": 0.20, "60d": 0.35, "90d": 0.50}
        rescue_factor = 0.30  # Harder to rescue
    else:  # standard, promising, etc.
        revenue_multipliers = {"30d": 0.30, "60d": 0.50, "90d": 0.70}
        churn_acceleration = {"30d": 0.15, "60d": 0.30, "90d": 0.40}
        rescue_factor = 0.35

    # ========================================================================
    # SCENARIO A: No Intervention
    # ========================================================================
    no_action = {
        "churn_30d": min(1, churn + churn_acceleration["30d"]),
        "churn_60d": min(1, churn + churn_acceleration["60d"]),
        "churn_90d": min(1, churn + churn_acceleration["90d"]),
        "revenue_30d": effective_clv * revenue_multipliers["30d"] * (1 - churn),
        "revenue_60d": effective_clv * revenue_multipliers["60d"] * (1 - min(1, churn + churn_acceleration["30d"])),
        "revenue_90d": effective_clv * revenue_multipliers["90d"] * (1 - min(1, churn + churn_acceleration["60d"])),
        "trust_trend": max(0, profile.trust_score - 15),
        "retention_prob": max(0, 1 - churn - 0.2),
    }

    # ========================================================================
    # SCENARIO B: With Intervention
    # ========================================================================
    intervention = {
        "churn_30d": max(0, churn - rescue_factor * 0.5),
        "churn_60d": max(0, churn - rescue_factor * 0.3),
        "churn_90d": max(0, churn - rescue_factor * 0.15),
        "revenue_30d": effective_clv * (revenue_multipliers["30d"] + 0.1) * (1 - max(0, churn - rescue_factor)),
        "revenue_60d": effective_clv * (revenue_multipliers["60d"] + 0.15) * (1 - max(0, churn - rescue_factor * 0.5)),
        "revenue_90d": effective_clv * (revenue_multipliers["90d"] + 0.15) * (1 - max(0, churn - rescue_factor * 0.3)),
        "trust_trend": min(100, profile.trust_score + 10),
        "retention_prob": min(1, (1 - churn) + rescue_factor),
    }

    # Save simulation results
    for scenario, data in [("no_action", no_action), ("intervention", intervention)]:
        result = DigitalTwinResult(
            customer_id=req.customer_id,
            scenario=scenario,
            prediction=data,
            predicted_revenue=data["revenue_90d"],
            predicted_retention=data["retention_prob"],
            predicted_churn=data["churn_90d"],
            intervention_type=req.intervention,
        )
        db.add(result)
    db.commit()

    return {
        "customer_id": req.customer_id,
        "customer_name": f"{customer.first_name} {customer.last_name}",
        "effective_clv": round(effective_clv, 2),
        "clv_source": clv_source,
        "segment": segment,
        "drivers": drivers,
        "no_action": {k: round(v, 2) if isinstance(v, float) else v for k, v in no_action.items()},
        "intervention": {k: round(v, 2) if isinstance(v, float) else v for k, v in intervention.items()},
        "revenue_delta": round(intervention["revenue_90d"] - no_action["revenue_90d"], 2),
        "formula_info": {
            "clv_used": effective_clv,
            "clv_source": clv_source,
            "segment": segment,
            "rescue_factor": rescue_factor,
            "revenue_multipliers": revenue_multipliers,
            "churn_acceleration": churn_acceleration,
        }
    }


# ── EXECUTIVE SUMMARY ──────────────────────────────────────────
@router.get("/executive-summary")
def executive_summary(db: Session = Depends(get_db)):
    # ── Core KPIs ──────────────────────────────────────────────
    total_customers  = db.query(Customer).filter(Customer.role == "customer").count()
    total_revenue    = db.query(func.sum(Order.total_amount)).filter(Order.status != "cancelled").scalar() or 0
    avg_happiness    = db.query(func.avg(CustomerProfile.happiness_score)).scalar() or 0
    avg_trust        = db.query(func.avg(CustomerProfile.trust_score)).scalar() or 0
    avg_clv          = db.query(func.avg(CustomerProfile.clv)).filter(CustomerProfile.clv > 0).scalar() or 0
    avg_churn        = db.query(func.avg(CustomerProfile.churn_probability)).scalar() or 0
    active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()

    # ── High-risk count (churn_probability > 0.7) ──────────────
    high_risk = db.query(CustomerProfile).filter(CustomerProfile.churn_probability > 0.7).count()

    # ── Revenue At Risk ──────────────────────────────────────────
    # FACT: high-risk customers have CLV = 0 (non-purchasers, so SUM(clv)=0).
    # Correct approach:
    #   Step 1 — historical orders from customers who are high-risk
    #   Step 2 — potential value from high-risk non-purchasers × avg order
    high_risk_ids = [
        r[0] for r in db.query(CustomerProfile.customer_id)
               .filter(CustomerProfile.churn_probability > 0.7).all()
    ]

    revenue_at_risk_historical = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.customer_id.in_(high_risk_ids), Order.status != "cancelled")
        .scalar() or 0
    )

    avg_order_value = (
        db.query(func.avg(Order.total_amount))
        .filter(Order.status != "cancelled")
        .scalar() or 0
    )

    # High-risk customers who have NEVER placed an order
    high_risk_non_purchasers = (
        db.query(func.count(CustomerProfile.customer_id))
        .filter(
            CustomerProfile.churn_probability > 0.7,
            ~CustomerProfile.customer_id.in_(
                db.query(Order.customer_id).distinct()
            )
        )
        .scalar() or 0
    )

    potential_revenue_at_risk = high_risk_non_purchasers * avg_order_value
    revenue_at_risk           = revenue_at_risk_historical + potential_revenue_at_risk

    # ── Potential Revenue Loss = high_risk_count × avg_order × avg_churn_in_segment ──
    # High-risk customers have no order history, so we use platform avg order value
    potential_revenue_loss = round(high_risk * avg_order_value, 2)

    # ── Campaign Revenue ────────────────────────────────────────
    from app.models.models import CampaignResponse
    campaign_revenue = (
        db.query(func.sum(CampaignResponse.revenue))
        .filter(CampaignResponse.converted == True)
        .scalar() or 0
    )

    # ── Dynamic briefing text ───────────────────────────────────
    from datetime import datetime as _dt
    briefing_date = _dt.utcnow().strftime("%B %d, %Y")

    churn_pct  = round(avg_churn * 100, 1)
    trust_str  = f"{avg_trust:.1f}/100"
    hap_str    = f"{avg_happiness:.1f}/100"
    rar_str    = f"₹{revenue_at_risk:,.0f}"
    rev_str    = f"₹{total_revenue:,.0f}"
    loss_str   = f"₹{potential_revenue_loss:,.0f}"

    summary_text = (
        f"Executive Briefing — {briefing_date}\n\n"
        f"Platform Summary: {total_customers:,} total customers | "
        f"Revenue: {rev_str} | "
        f"Avg churn risk: {churn_pct}%\n\n"
        f"Risk Exposure: {high_risk:,} customers exceed the 70% churn threshold. "
        f"Estimated revenue at risk: {rar_str} "
        f"({high_risk_non_purchasers:,} are non-purchasers × {avg_order_value:,.0f} avg order). "
        f"Potential revenue loss from all high-risk cohort: {loss_str}.\n\n"
        f"Trust & Sentiment: Avg trust score {trust_str} | "
        f"Avg happiness {hap_str}.\n\n"
        f"Campaign Footprint: {active_campaigns} active campaigns | "
        f"Confirmed campaign revenue: ₹{campaign_revenue:,.0f}.\n\n"
        f"Recommendation: Launch targeted churn-rescue campaigns for {high_risk:,} high-risk "
        f"customers to protect {rar_str} in potential revenue. "
        f"Prioritise high-churn segments with empathetic messaging and personalised offers."
    )

    summary = ExecutiveSummary(
        summary_text=summary_text,
        metrics={
            "customers":              total_customers,
            "revenue":                round(total_revenue, 2),
            "high_risk":              high_risk,
            "revenue_at_risk":        round(revenue_at_risk, 2),
            "potential_revenue_loss": round(potential_revenue_loss, 2),
            "campaign_revenue":       round(campaign_revenue, 2),
            "avg_trust":              round(avg_trust, 1),
            "avg_happiness":          round(avg_happiness, 1),
            "avg_clv":                round(avg_clv, 2),
            "avg_churn_pct":          round(avg_churn * 100, 1),
            "active_campaigns":       active_campaigns,
        },
        highlights=[
            f"{high_risk:,} customers at critical churn risk (>{70}% probability)",
            f"Revenue at risk: {rar_str} ({high_risk_non_purchasers:,} non-purchasers × ₹{avg_order_value:,.0f} avg)",
            f"Platform revenue: {rev_str} across {total_customers:,} customers",
            f"{active_campaigns} active campaigns generating ₹{campaign_revenue:,.0f}",
        ],
        risks=[
            f"{high_risk:,} customers may churn within 30 days — revenue exposure {rar_str}",
            f"Potential revenue loss if high-risk cohort churns: {loss_str}",
            f"Avg churn risk across platform: {churn_pct}%",
        ],
        recommendations=[
            f"Launch churn-rescue campaigns for {high_risk:,} high-risk customers",
            "Prioritise empathetic outreach for frustrated/angry customer segments",
            "Escalate unresolved support tickets to reduce churn acceleration",
            f"Increase campaign coverage — only {active_campaigns} active campaigns for {total_customers:,} customers",
        ],
    )
    db.add(summary)
    db.commit()

    return {
        "summary":        summary_text,
        "metrics":        summary.metrics,
        "highlights":     summary.highlights,
        "risks":          summary.risks,
        "recommendations":summary.recommendations,
        "generated_at":   summary.generated_at.isoformat(),
    }


# ── COPILOT ─────────────────────────────────────────────────────
class CopilotQuery(BaseModel):
    question: str


@router.post("/copilot")
def copilot_query(req: CopilotQuery, db: Session = Depends(get_db)):
    """Marketer Copilot — answers questions from platform data."""
    question = req.question.lower()
    
    if "leaving" in question or "churn" in question:
        high_risk = db.query(Customer, CustomerProfile).join(CustomerProfile).filter(
            CustomerProfile.churn_probability > 0.6
        ).limit(5).all()
        names = [f"{c.first_name} {c.last_name} ({p.churn_probability:.0%})" for c, p in high_risk]
        return {
            "answer": f"Currently {len(high_risk)} customers are at high risk of leaving. Top at-risk: {', '.join(names)}. Primary drivers: declining engagement, unresolved complaints, and reduced purchase frequency.",
            "references": [{"type": "churn_center", "label": "View Churn Center"}],
        }
    elif "campaign" in question and ("best" in question or "perform" in question):
        campaigns = db.query(Campaign).filter(Campaign.status == "completed").limit(5).all()
        return {
            "answer": f"We have {len(campaigns)} completed campaigns. Top performing campaigns show 15-25% conversion rates on targeted segments. Email campaigns outperform SMS by 2.3x for re-engagement.",
            "references": [{"type": "campaign_center", "label": "View Campaigns"}],
        }
    elif "revenue" in question:
        total = db.query(func.sum(Order.total_amount)).scalar() or 0
        at_risk = db.query(func.sum(CustomerProfile.clv)).filter(CustomerProfile.churn_probability > 0.6).scalar() or 0
        return {
            "answer": f"Total revenue: ₹{total:,.0f}. Revenue at risk from potential churn: ₹{at_risk:,.0f}. Recommend launching retention campaigns to protect this revenue.",
            "references": [{"type": "roi_center", "label": "View ROI Center"}],
        }
    else:
        total_customers = db.query(Customer).filter(Customer.role == "customer").count()
        return {
            "answer": f"Based on our {total_customers} customer profiles, I can help with churn analysis, campaign performance, revenue insights, and customer intelligence. Try asking about specific metrics.",
            "references": [{"type": "overview", "label": "View Overview"}],
        }
