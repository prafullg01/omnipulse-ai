"""
RESTORE CUSTOMER ACTIVITY DATA
================================
Adds back all the missing seeded customer activity that was removed:
  - Support tickets with realistic sentiments and messages
  - Campaigns aligned with the dataset (Diwali Sale, Big Billion Days, etc.)
  - Campaign responses linked to real customers
  - Messages across channels (email, sms, push, in_app)
  - Journeys of all types (churn_rescue, onboarding, re_engagement, loyalty)
  - Digital twin results for high-risk customers
  - Executive summaries

All data is aligned with the actual dataset customer IDs (CUST-XXXXXXXX format)
and uses the real sentiments, emotions, campaigns, and channels from the master events CSV.
"""

import sys
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base, init_db
from app.config import get_settings
from app.models.models import (
    Customer, Product, Order, OrderItem, Event, Campaign, CampaignResponse,
    SupportTicket, CustomerProfile, NBADecision, Journey, Message,
    DigitalTwinResult, ExecutiveSummary
)

random.seed(42)

settings = get_settings()
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS ALIGNED WITH DATASETS
# ═══════════════════════════════════════════════════════════════════════════════

# From omnipulse_master_events.csv
DATASET_CAMPAIGNS = [
    ("Diwali Sale", "email", "Up to 60% off on Electronics & Fashion", "completed"),
    ("Big Billion Days", "email", "Biggest sale of the year - up to 80% off", "completed"),
    ("Great Indian Festival", "sms", "Festival special deals across all categories", "active"),
    ("Independence Day Sale", "push", "Freedom sale - flat 50% off", "completed"),
    ("Republic Day Sale", "email", "Republic Day special - extra 20% cashback", "active"),
    ("Monsoon Mega Sale", "sms", "Monsoon deals - waterproof electronics & fashion", "active"),
    ("New Year Sale", "push", "Start 2025 with amazing deals", "completed"),
]

DATASET_SENTIMENTS = ["Positive", "Neutral", "Negative"]
DATASET_EMOTIONS = ["Happy", "Neutral", "Excited", "Frustrated", "Angry"]
DATASET_CHANNELS = ["WhatsApp", "Email", "SMS", "Push Notification", "Support Chat"]

# Realistic Indian e-commerce support ticket messages aligned with dataset sentiments
TICKET_MESSAGES = {
    "angry": [
        "This is absolutely unacceptable! I ordered 5 days ago and still no delivery. I want a full refund immediately!",
        "Worst experience ever. The product was damaged and customer care kept me waiting for 45 minutes. This is a scam!",
        "I am furious about the quality. This is not what was advertised. I demand a refund and compensation!",
        "Three times I have called your helpline and nobody resolves my issue. This is the worst service I have ever seen!",
        "You charged me twice for the same order! I want my money back RIGHT NOW or I will file a consumer complaint!",
        "The delivery person was extremely rude and threw my package at the door. I am filing a formal complaint!",
        "I ordered a Samsung phone but received a cheap duplicate. This is fraud! I am contacting consumer forum!",
    ],
    "frustrated": [
        "I've been waiting for my order for over a week now. The tracking hasn't updated in 3 days. Very disappointed.",
        "The product I received is the wrong color. I've tried contacting support twice with no response. Very annoying.",
        "My payment was deducted but the order shows as failed. This is really frustrating. Please help.",
        "I requested a return 10 days ago and still no pickup scheduled. How long does this take?",
        "The app keeps crashing when I try to track my order. I don't know what's happening with my delivery.",
        "I applied a coupon code but the discount was not applied. Now customer care says nothing can be done. Unfair!",
    ],
    "happy": [
        "Excellent service! The product arrived a day early and was exactly as described. Thank you!",
        "Love the quality of the product. Great packaging too. Will definitely order again!",
        "Your customer support team was incredibly helpful. They resolved my issue in minutes. Amazing!",
        "The Diwali Sale deals were fantastic! Got amazing products at great prices. Very happy customer!",
        "Fast delivery, great quality, and the return process was so smooth. Best shopping experience!",
        "I've been shopping here for 2 years and the service keeps getting better. Highly recommended!",
    ],
    "neutral": [
        "I'd like to know the status of my return request. Order placed last week.",
        "Can you help me understand the warranty policy for electronics?",
        "I need to change the delivery address for my recent order. Is that possible?",
        "When will the iPhone 15 Pro be back in stock? I've been waiting for a while.",
        "I want to know about the exchange policy for fashion items.",
        "Please provide an update on my refund. It was supposed to be processed 5 days ago.",
        "How do I redeem my loyalty points? The app doesn't show the option clearly.",
    ],
    "excited": [
        "Just got my new MacBook Air and it's AMAZING! The Big Billion Days deal was incredible!",
        "OMG the new collection is beautiful! Already added 5 items to my cart! Can't wait for the sale!",
        "Your recommendation engine is spot on! Found exactly what I was looking for. Love this platform!",
        "The Great Indian Festival deals are mind-blowing! Already placed 3 orders today! 🎉",
    ],
}

TICKET_SUBJECTS = {
    "angry": [
        "URGENT: Order not delivered - Demand refund",
        "Damaged product received - Extremely disappointed",
        "Double charged for order - Need immediate resolution",
        "Fraud complaint - Wrong product delivered",
    ],
    "frustrated": [
        "Order tracking not updating for 3 days",
        "Wrong product color received",
        "Payment deducted but order failed",
        "Return pickup not scheduled after 10 days",
    ],
    "happy": [
        "Great service - Thank you!",
        "Amazing product quality",
        "Excellent customer support experience",
        "Love the Diwali Sale deals!",
    ],
    "neutral": [
        "Return request status inquiry",
        "Warranty policy question",
        "Delivery address change request",
        "Product availability inquiry",
    ],
    "excited": [
        "Amazing product received!",
        "Love the new collection!",
        "Great Indian Festival - Best deals!",
    ],
}

# Journey step templates
JOURNEY_TEMPLATES = {
    "churn_rescue": [
        {"step": "Churn Risk Detected", "status": "completed"},
        {"step": "WhatsApp Reminder Sent", "status": "completed"},
        {"step": "Discount Coupon Delivered", "status": "completed"},
        {"step": "Customer Response Tracked", "status": "pending"},
        {"step": "Retention Outcome Measured", "status": "pending"},
    ],
    "onboarding": [
        {"step": "Welcome Email Sent", "status": "completed"},
        {"step": "Profile Setup Nudge", "status": "completed"},
        {"step": "First Product Recommendation", "status": "completed"},
        {"step": "First Purchase Incentive", "status": "pending"},
    ],
    "re_engagement": [
        {"step": "Inactivity Detected", "status": "completed"},
        {"step": "Push Notification Sent", "status": "completed"},
        {"step": "Personalized Offer Delivered", "status": "completed"},
        {"step": "Customer Re-engaged", "status": "pending"},
    ],
    "loyalty": [
        {"step": "Loyalty Tier Upgraded", "status": "completed"},
        {"step": "Exclusive Access Granted", "status": "completed"},
        {"step": "VIP Rewards Delivered", "status": "completed"},
        {"step": "Repeat Purchase Tracked", "status": "completed"},
    ],
}

# Message templates
MESSAGE_TEMPLATES = {
    "email": [
        ("🎉 Exclusive Deal Just For You!", "Hi {name}, we've handpicked amazing deals based on your preferences. Up to 40% off on your favorite brands!", "exciting"),
        ("Your Cart Misses You 🛒", "Hi {name}, you left some items in your cart. Complete your purchase now and get free delivery!", "empathetic"),
        ("Loyalty Reward Unlocked! ⭐", "Congratulations {name}! You've earned 500 bonus loyalty points. Redeem them on your next order!", "professional"),
        ("New Arrivals in {category}", "Hi {name}, check out the latest arrivals in {category}. Hand-picked recommendations just for you!", "professional"),
    ],
    "sms": [
        ("OmniPulse Deal Alert", "Flash Sale LIVE! Extra 20% off on Electronics. Use code FLASH20. Shop now!", "exciting"),
        ("Order Update", "Your order has been shipped and will arrive by tomorrow. Track: omnipulse.ai/track", "professional"),
        ("Festive Offer", "Diwali Special! Flat 50% off on top brands. Limited time only. Shop now at omnipulse.ai", "exciting"),
    ],
    "push": [
        ("Price Drop Alert! 📉", "The {product} you were eyeing just dropped in price! Get it before stock runs out.", "exciting"),
        ("Your Wishlist Item is Back", "Great news! {product} is back in stock. Grab it now!", "empathetic"),
        ("Weekend Special 🎊", "This weekend only - flat 30% off on all Fashion items. Don't miss out!", "exciting"),
    ],
    "in_app": [
        ("Welcome Back!", "We missed you, {name}! Here's a special 15% discount to welcome you back.", "empathetic"),
        ("Rate Your Experience", "How was your recent purchase? Rate now and earn loyalty points!", "professional"),
        ("Recommendation", "Based on your browsing, you might love these products!", "professional"),
    ],
}


def restore_activity():
    """Restore all missing customer activity data."""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("RESTORING CUSTOMER ACTIVITY DATA")
        print("=" * 80)
        
        # Get existing customers
        customers = db.query(Customer).filter(Customer.role == "customer").all()
        if not customers:
            print("ERROR: No customers found in database!")
            return
        
        print(f"Found {len(customers)} customers")
        
        # Get existing products
        products = db.query(Product).all()
        print(f"Found {len(products)} products")
        
        # ── 1. RESTORE SUPPORT TICKETS ─────────────────────────────────────
        print("\n[1/7] Restoring Support Tickets...")
        
        # Remove old minimal tickets
        db.execute(text("DELETE FROM support_tickets"))
        db.commit()
        
        tickets_created = 0
        # Create tickets for ~15% of customers (realistic ratio)
        ticket_customers = random.sample(customers, min(int(len(customers) * 0.15), 300))
        
        for c in ticket_customers:
            # Determine sentiment based on customer profile
            profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == c.customer_id).first()
            
            if profile and profile.risk_score and profile.risk_score > 70:
                sentiment = random.choice(["angry", "frustrated", "frustrated"])
            elif profile and profile.happiness_score and profile.happiness_score > 70:
                sentiment = random.choice(["happy", "excited", "neutral"])
            else:
                sentiment = random.choice(["neutral", "frustrated", "happy", "neutral"])
            
            # Sentiment score mapping
            score_map = {
                "angry": round(random.uniform(0.1, 0.3), 2),
                "frustrated": round(random.uniform(0.25, 0.45), 2),
                "neutral": round(random.uniform(0.45, 0.65), 2),
                "happy": round(random.uniform(0.7, 0.9), 2),
                "excited": round(random.uniform(0.85, 1.0), 2),
            }
            
            # Priority mapping
            priority_map = {
                "angry": "high",
                "frustrated": random.choice(["high", "medium"]),
                "neutral": "medium",
                "happy": "low",
                "excited": "low",
            }
            
            # Status - angry/frustrated tickets more likely open
            if sentiment in ["angry", "frustrated"]:
                status = random.choice(["open", "open", "in_progress", "resolved"])
            else:
                status = random.choice(["open", "in_progress", "resolved", "resolved", "closed"])
            
            msgs = TICKET_MESSAGES.get(sentiment, TICKET_MESSAGES["neutral"])
            subjects = TICKET_SUBJECTS.get(sentiment, TICKET_SUBJECTS["neutral"])
            
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 90))
            resolved_at = created_at + timedelta(hours=random.randint(1, 72)) if status in ["resolved", "closed"] else None
            
            ticket = SupportTicket(
                customer_id=c.customer_id,
                subject=random.choice(subjects),
                message=random.choice(msgs),
                sentiment=sentiment,
                sentiment_score=score_map[sentiment],
                status=status,
                priority=priority_map[sentiment],
                created_at=created_at,
                resolved_at=resolved_at,
            )
            db.add(ticket)
            tickets_created += 1
            
            # Some angry customers have multiple tickets
            if sentiment in ["angry", "frustrated"] and random.random() > 0.6:
                ticket2 = SupportTicket(
                    customer_id=c.customer_id,
                    subject=random.choice(subjects),
                    message=random.choice(msgs),
                    sentiment=sentiment,
                    sentiment_score=score_map[sentiment],
                    status=random.choice(["open", "in_progress"]),
                    priority="high",
                    created_at=created_at + timedelta(days=random.randint(1, 5)),
                )
                db.add(ticket2)
                tickets_created += 1
        
        db.commit()
        print(f"  ✓ {tickets_created} support tickets created")
        
        # ── 2. RESTORE CAMPAIGNS ──────────────────────────────────────────
        print("\n[2/7] Restoring Campaigns (aligned with dataset)...")
        
        # Remove old campaigns and responses
        db.execute(text("DELETE FROM campaign_responses"))
        db.execute(text("DELETE FROM campaigns"))
        db.commit()
        
        campaigns = []
        for name, channel, offer, status in DATASET_CAMPAIGNS:
            days_ago = random.randint(5, 120)
            started = datetime.utcnow() - timedelta(days=days_ago)
            ended = started + timedelta(days=random.randint(3, 14)) if status == "completed" else None
            
            camp = Campaign(
                campaign_name=name,
                description=f"Automated {channel} campaign: {offer}",
                channel=channel,
                offer=offer,
                status=status,
                discount_pct=random.uniform(5, 50),
                variant=random.choice(["A", "B"]),
                budget=random.uniform(50000, 500000),
                created_at=started - timedelta(days=random.randint(1, 5)),
                started_at=started,
                ended_at=ended,
            )
            db.add(camp)
            campaigns.append(camp)
        
        # Also add the existing campaign types that were in the DB
        extra_campaigns = [
            ("Win-Back High Risk", "email", "20% off next purchase for at-risk customers", "active"),
            ("VIP Loyalty Rewards", "email", "Exclusive rewards for VIP segment", "active"),
            ("Trust Builder", "sms", "Service recovery offers for low-trust customers", "active"),
            ("First Purchase Incentive", "push", "15% off first order for new customers", "active"),
            ("Cross-Sell Campaign", "email", "Personalized product recommendations", "active"),
            ("Cart Rescue Campaign", "push", "Complete your purchase - 10% off", "active"),
        ]
        for name, channel, offer, status in extra_campaigns:
            camp = Campaign(
                campaign_name=name,
                description=f"AI-driven {channel} campaign: {offer}",
                channel=channel,
                offer=offer,
                status=status,
                discount_pct=random.uniform(5, 25),
                variant=random.choice(["A", "B"]),
                budget=random.uniform(25000, 200000),
                created_at=datetime.utcnow() - timedelta(days=random.randint(5, 60)),
            )
            db.add(camp)
            campaigns.append(camp)
        
        db.flush()
        print(f"  ✓ {len(campaigns)} campaigns created")
        
        # ── 3. RESTORE CAMPAIGN RESPONSES ─────────────────────────────────
        print("\n[3/7] Restoring Campaign Responses...")
        
        responses_created = 0
        for camp in campaigns:
            # Each campaign reaches 10-30% of customers
            reach_pct = random.uniform(0.10, 0.30)
            target_customers = random.sample(customers, min(int(len(customers) * reach_pct), 500))
            
            for c in target_customers:
                opened = random.random() > 0.35  # ~65% open rate
                clicked = opened and random.random() > 0.5  # ~50% click rate among openers
                converted = clicked and random.random() > 0.7  # ~30% conversion among clickers
                
                # Revenue based on conversion
                if converted:
                    revenue = round(random.uniform(500, 15000), 0)
                else:
                    revenue = 0
                
                resp = CampaignResponse(
                    campaign_id=camp.campaign_id,
                    customer_id=c.customer_id,
                    opened=opened,
                    clicked=clicked,
                    converted=converted,
                    revenue=revenue,
                    timestamp=camp.created_at + timedelta(hours=random.randint(1, 168)),
                )
                db.add(resp)
                responses_created += 1
            
            if responses_created % 500 == 0:
                db.commit()
        
        db.commit()
        print(f"  ✓ {responses_created} campaign responses created")
        
        # ── 4. RESTORE MESSAGES ───────────────────────────────────────────
        print("\n[4/7] Restoring Messages...")
        
        db.execute(text("DELETE FROM messages"))
        db.commit()
        
        messages_created = 0
        # Send messages to ~40% of customers
        message_customers = random.sample(customers, min(int(len(customers) * 0.4), 800))
        
        for c in message_customers:
            # Each customer gets 1-4 messages
            for _ in range(random.randint(1, 4)):
                channel = random.choice(["email", "sms", "push", "in_app"])
                templates = MESSAGE_TEMPLATES[channel]
                template = random.choice(templates)
                subject, content, tone = template
                
                # Personalize
                product = random.choice(products) if products else None
                name = c.first_name
                category = product.category if product else "Electronics"
                prod_name = product.name if product else "Product"
                
                content = content.replace("{name}", name)
                content = content.replace("{category}", category)
                content = content.replace("{product}", prod_name)
                subject = subject.replace("{product}", prod_name)
                subject = subject.replace("{category}", category)
                
                # Pick a campaign to associate with (50% chance)
                campaign_id = random.choice(campaigns).campaign_id if random.random() > 0.5 else None
                
                msg = Message(
                    customer_id=c.customer_id,
                    channel=channel,
                    subject=subject,
                    content=content,
                    tone=tone,
                    opened=random.random() > 0.4,
                    clicked=random.random() > 0.65,
                    campaign_id=campaign_id,
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23)),
                )
                db.add(msg)
                messages_created += 1
            
            if messages_created % 500 == 0:
                db.commit()
        
        db.commit()
        print(f"  ✓ {messages_created} messages created")
        
        # ── 5. RESTORE JOURNEYS ───────────────────────────────────────────
        print("\n[5/7] Restoring Journeys (diversified types)...")
        
        db.execute(text("DELETE FROM journeys"))
        db.commit()
        
        journeys_created = 0
        journey_types = list(JOURNEY_TEMPLATES.keys())
        
        # Assign journeys based on customer profile
        for c in customers:
            profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == c.customer_id).first()
            
            if not profile:
                continue
            
            # Determine journey type based on customer segment/risk
            if profile.segment in ["At-Risk", "at_risk"]:
                jtype = "churn_rescue"
                probability = 0.7  # 70% of at-risk get a journey
            elif profile.segment in ["Inactive"]:
                jtype = "re_engagement"
                probability = 0.3  # 30% of inactive get a journey
            elif profile.segment in ["VIP", "Loyal", "high_value"]:
                jtype = "loyalty"
                probability = 0.5
            elif profile.segment in ["new"]:
                jtype = "onboarding"
                probability = 0.8
            else:
                jtype = random.choice(journey_types)
                probability = 0.15
            
            if random.random() > probability:
                continue
            
            steps = [dict(s) for s in JOURNEY_TEMPLATES[jtype]]  # Deep copy
            
            # Randomly complete some steps
            completed_steps = random.randint(1, len(steps))
            for i in range(completed_steps):
                steps[i]["status"] = "completed"
            
            jstatus = "completed" if completed_steps == len(steps) else "active"
            
            journey = Journey(
                customer_id=c.customer_id,
                journey_type=jtype,
                journey_stage=random.choice(["awareness", "consideration", "decision", "retention"]),
                journey_status=jstatus,
                steps=steps,
                current_step=completed_steps - 1,
                created_at=datetime.utcnow() - timedelta(days=random.randint(5, 90)),
                completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 5)) if jstatus == "completed" else None,
            )
            db.add(journey)
            journeys_created += 1
            
            if journeys_created % 200 == 0:
                db.commit()
        
        db.commit()
        print(f"  ✓ {journeys_created} journeys created ({', '.join(journey_types)})")
        
        # ── 6. RESTORE DIGITAL TWIN RESULTS ───────────────────────────────
        print("\n[6/7] Restoring Digital Twin Results...")
        
        # Keep existing digital twin results, add more
        existing_dt_count = db.query(DigitalTwinResult).count()
        
        dt_created = 0
        # Create digital twin results for at-risk and high-value customers
        dt_customers = [c for c in customers if db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == c.customer_id,
            CustomerProfile.risk_score > 40
        ).first()]
        
        dt_sample = random.sample(dt_customers, min(200, len(dt_customers)))
        
        for c in dt_sample:
            profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == c.customer_id).first()
            if not profile:
                continue
            
            # Check if already has a result
            existing = db.query(DigitalTwinResult).filter(DigitalTwinResult.customer_id == c.customer_id).first()
            if existing:
                continue
            
            churn_prob = (profile.churn_probability or 0.5)
            clv = (profile.clv or 5000)
            
            # No-action scenario
            dt_no_action = DigitalTwinResult(
                customer_id=c.customer_id,
                scenario="no_action",
                prediction={
                    "outcome": "Customer Likely To Churn" if churn_prob > 0.6 else "Gradual Disengagement",
                    "churn_probability": round(churn_prob, 3),
                    "revenue_impact": round(-clv * churn_prob * 0.5, 0),
                },
                predicted_revenue=round(clv * (1 - churn_prob), 0),
                predicted_retention=round(1 - churn_prob, 3),
                predicted_churn=round(churn_prob, 3),
                intervention_type=None,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.add(dt_no_action)
            
            # Intervention scenario
            intervention_types = [
                "Personalized Discount",
                "Customer Success Call",
                "VIP Upgrade Offer",
                "Loyalty Points Boost",
                "Free Delivery Pass",
            ]
            intervention = random.choice(intervention_types)
            improved_churn = churn_prob * random.uniform(0.3, 0.7)  # 30-70% reduction
            
            dt_intervention = DigitalTwinResult(
                customer_id=c.customer_id,
                scenario="intervention",
                prediction={
                    "outcome": "Retention Improved" if improved_churn < 0.4 else "Partial Recovery",
                    "intervention": intervention,
                    "churn_reduction": round((churn_prob - improved_churn) * 100, 1),
                    "roi_estimate": round(clv * (churn_prob - improved_churn), 0),
                },
                predicted_revenue=round(clv * (1 - improved_churn) * 1.1, 0),
                predicted_retention=round(1 - improved_churn, 3),
                predicted_churn=round(improved_churn, 3),
                intervention_type=intervention,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.add(dt_intervention)
            
            # Comparison scenario
            dt_comparison = DigitalTwinResult(
                customer_id=c.customer_id,
                scenario="comparison",
                prediction={
                    "no_action_churn": round(churn_prob, 3),
                    "intervention_churn": round(improved_churn, 3),
                    "revenue_saved": round(clv * (churn_prob - improved_churn), 0),
                    "recommended_intervention": intervention,
                    "confidence": random.randint(60, 98),
                },
                predicted_revenue=round(clv * (churn_prob - improved_churn), 0),
                predicted_retention=round((churn_prob - improved_churn), 3),
                predicted_churn=round(improved_churn, 3),
                intervention_type=intervention,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.add(dt_comparison)
            dt_created += 3
            
            if dt_created % 100 == 0:
                db.commit()
        
        db.commit()
        print(f"  ✓ {dt_created} digital twin results created (existing: {existing_dt_count})")
        
        # ── 7. RESTORE EXECUTIVE SUMMARIES ────────────────────────────────
        print("\n[7/7] Restoring Executive Summaries...")
        
        existing_es = db.query(ExecutiveSummary).count()
        if existing_es < 5:
            # Only add if we don't have enough
            db.execute(text("DELETE FROM executive_summaries"))
            db.commit()
            
            total_customers = db.query(Customer).filter(Customer.role == "customer").count()
            total_orders = db.query(Order).count()
            total_revenue_result = db.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM orders")).fetchone()
            total_revenue = total_revenue_result[0] if total_revenue_result else 0
            at_risk_count = db.query(CustomerProfile).filter(CustomerProfile.segment.in_(["At-Risk", "at_risk"])).count()
            
            summaries = [
                ExecutiveSummary(
                    summary_text="Weekly Business Intelligence Report - OmniPulse AI Platform",
                    metrics={
                        "total_customers": total_customers,
                        "active_customers": int(total_customers * 0.72),
                        "total_revenue": total_revenue,
                        "avg_order_value": round(total_revenue / max(total_orders, 1), 0),
                        "customer_satisfaction": 78.5,
                        "nps_score": 42,
                        "churn_rate": 8.3,
                        "retention_rate": 91.7,
                    },
                    highlights=[
                        f"Total active customer base: {total_customers:,} customers across 15+ Indian cities",
                        f"Revenue this period: ₹{total_revenue:,.0f} from {total_orders:,} orders",
                        "Diwali Sale campaign achieved 65% open rate and 23% conversion",
                        "AI-driven churn rescue journeys saved ₹2.3M in potential revenue loss",
                        "Customer trust score improved 12% after implementing proactive support",
                    ],
                    risks=[
                        f"{at_risk_count} customers identified as at-risk of churning (segment: At-Risk/Inactive)",
                        "Cart abandonment rate at 68% - above industry average of 60%",
                        "Support ticket volume increased 15% - 40% are high-priority angry/frustrated",
                        "Competitive risk score averaging 35% across premium buyer segment",
                    ],
                    recommendations=[
                        "Deploy personalized WhatsApp campaigns targeting at-risk segment with exclusive discounts",
                        "Implement real-time cart rescue with dynamic pricing for high-CLV customers",
                        "Scale customer success calls for top 50 at-risk accounts (potential save: ₹8.5M CLV)",
                        "Launch loyalty tier upgrade program for medium-value segment to drive retention",
                        "Activate digital twin simulations for all VIP customers before next major sale",
                    ],
                    generated_at=datetime.utcnow(),
                ),
                ExecutiveSummary(
                    summary_text="AI/ML Performance Dashboard - Model Accuracy & Impact Report",
                    metrics={
                        "churn_model_accuracy": 87.3,
                        "nba_acceptance_rate": 72.1,
                        "sentiment_accuracy": 91.5,
                        "clv_prediction_mape": 12.8,
                        "recommendation_ctr": 18.7,
                        "journey_completion_rate": 64.2,
                    },
                    highlights=[
                        "Churn prediction model achieving 87.3% accuracy on holdout set",
                        "NBA engine processed 5,768 decisions with 72.1% customer acceptance rate",
                        "Sentiment analysis accuracy at 91.5% across all support channels",
                        "Digital twin simulations show average 40% churn reduction with interventions",
                    ],
                    risks=[
                        "CLV prediction MAPE at 12.8% - needs recalibration for high-value segment",
                        "Cold-start problem for new customers affecting recommendation quality",
                        "Model drift detected in churn prediction for Tier-2 city customers",
                    ],
                    recommendations=[
                        "Retrain CLV model with latest 90-day transaction data",
                        "Implement collaborative filtering for cold-start customers",
                        "Add city-tier feature engineering to churn model",
                        "A/B test new NBA engine v2 with reinforcement learning",
                    ],
                    generated_at=datetime.utcnow() - timedelta(days=3),
                ),
                ExecutiveSummary(
                    summary_text="Campaign Performance Analysis - Q2 2025",
                    metrics={
                        "total_campaigns": len(campaigns),
                        "total_reach": responses_created,
                        "avg_open_rate": 64.5,
                        "avg_click_rate": 31.2,
                        "avg_conversion_rate": 9.8,
                        "total_campaign_revenue": round(total_revenue * 0.35, 0),
                        "campaign_roi": 3.2,
                    },
                    highlights=[
                        "Big Billion Days campaign generated highest revenue at ₹4.2M",
                        "WhatsApp channel outperforming email by 23% in open rates",
                        "AI-personalized campaigns show 2.4x higher conversion vs generic",
                        "Cart Rescue campaign recovered 15% of abandoned carts",
                    ],
                    risks=[
                        "SMS channel showing declining engagement - potential fatigue",
                        "Push notification opt-out rate increasing month-over-month",
                        "Campaign frequency causing negative sentiment in 8% of customers",
                    ],
                    recommendations=[
                        "Shift budget from SMS to WhatsApp for better ROI",
                        "Implement frequency capping at 3 messages per customer per week",
                        "Test rich media push notifications with product images",
                        "Launch A/B test comparing AI-generated vs template messages",
                    ],
                    generated_at=datetime.utcnow() - timedelta(days=7),
                ),
            ]
            
            for s in summaries:
                db.add(s)
            
            db.commit()
            print(f"  ✓ {len(summaries)} executive summaries created")
        else:
            print(f"  ✓ {existing_es} executive summaries already exist (skipped)")
        
        # ── FINAL STATISTICS ──────────────────────────────────────────────
        print("\n" + "=" * 80)
        print("CUSTOMER ACTIVITY RESTORATION COMPLETE!")
        print("=" * 80)
        print(f"  Customers:          {db.query(Customer).filter(Customer.role == 'customer').count():,}")
        print(f"  Products:           {db.query(Product).count():,}")
        print(f"  Orders:             {db.query(Order).count():,}")
        print(f"  Events:             {db.query(Event).count():,}")
        print(f"  Support Tickets:    {db.query(SupportTicket).count():,}")
        print(f"  Campaigns:          {db.query(Campaign).count():,}")
        print(f"  Campaign Responses: {db.query(CampaignResponse).count():,}")
        print(f"  Messages:           {db.query(Message).count():,}")
        print(f"  Journeys:           {db.query(Journey).count():,}")
        print(f"  NBA Decisions:      {db.query(NBADecision).count():,}")
        print(f"  Digital Twins:      {db.query(DigitalTwinResult).count():,}")
        print(f"  Exec Summaries:     {db.query(ExecutiveSummary).count():,}")
        print("=" * 80)
        
        # Journey type breakdown
        print("\n  Journey Types:")
        for jtype in ["churn_rescue", "onboarding", "re_engagement", "loyalty"]:
            count = db.query(Journey).filter(Journey.journey_type == jtype).count()
            print(f"    {jtype:20s}: {count}")
        
        # Ticket sentiment breakdown
        print("\n  Ticket Sentiments:")
        for sent in ["angry", "frustrated", "neutral", "happy", "excited"]:
            count = db.query(SupportTicket).filter(SupportTicket.sentiment == sent).count()
            print(f"    {sent:15s}: {count}")
        
        # Campaign breakdown
        print("\n  Campaigns:")
        for camp in campaigns:
            resp_count = db.query(CampaignResponse).filter(CampaignResponse.campaign_id == camp.campaign_id).count()
            print(f"    {camp.campaign_name:35s} [{camp.status:10s}] - {resp_count} responses")
        
        print("\n✅ All customer activity data has been restored!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    restore_activity()
