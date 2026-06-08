"""Comprehensive data seeder for OmniPulse AI demo.
Generates realistic Indian customers, products, events, tickets, campaigns, and profiles.
Aligned with the actual datasets (omnipulse_master_events.csv, ai_predictions.csv).
"""
import random
import uuid
from datetime import datetime, timedelta
from app.database.connection import SessionLocal, init_db
from app.models.models import *
from app.utils.auth import hash_password

random.seed(42)


FIRST_NAMES_M = ["Rahul", "Arjun", "Vikram", "Aditya", "Rohan", "Karan", "Siddharth", "Aarav", "Dev", "Nikhil",
                  "Pranav", "Harsh", "Varun", "Ishaan", "Dhruv", "Manish", "Rajesh", "Suresh", "Ankit", "Amit"]
FIRST_NAMES_F = ["Priya", "Ananya", "Sneha", "Kavya", "Ishita", "Meera", "Nisha", "Pooja", "Riya", "Shruti",
                  "Divya", "Neha", "Aisha", "Tanya", "Simran", "Pallavi", "Deepika", "Sakshi", "Kritika", "Lavanya"]
LAST_NAMES = ["Sharma", "Patel", "Gupta", "Singh", "Kumar", "Mehta", "Joshi", "Reddy", "Nair", "Iyer",
              "Kapoor", "Malhotra", "Bhat", "Rao", "Verma", "Chopra", "Desai", "Pillai", "Menon", "Shah"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
LANGUAGES = ["en", "hi", "kn", "ta", "te", "ml", "mr"]

CATEGORIES = {
    "Electronics": [
        ("iPhone 15 Pro", 134900, "Apple", "Latest iPhone with A17 Pro chip, titanium design, 48MP camera system"),
        ("Samsung Galaxy S24 Ultra", 129999, "Samsung", "6.8 inch AMOLED, S Pen, AI features, 200MP camera"),
        ("MacBook Air M3", 114900, "Apple", "15-inch Liquid Retina, M3 chip, 18hr battery, 8GB unified memory"),
        ("Sony WH-1000XM5", 29990, "Sony", "Industry-leading noise cancelling headphones with 30hr battery"),
        ("iPad Air M2", 74900, "Apple", "11-inch Liquid Retina, M2 chip, Apple Pencil support"),
        ("JBL Flip 6", 9999, "JBL", "Portable waterproof Bluetooth speaker with 12hr playtime"),
    ],
    "Fashion": [
        ("Nike Air Max 270", 12995, "Nike", "Lifestyle sneaker with Max Air unit for all-day comfort"),
        ("Levi's 511 Slim Jeans", 4599, "Levi's", "Classic slim fit jeans in dark indigo wash"),
        ("Ray-Ban Aviator", 8490, "Ray-Ban", "Classic aviator sunglasses with polarized lenses"),
        ("Adidas Ultraboost", 16999, "Adidas", "Premium running shoes with Boost midsole technology"),
        ("Tommy Hilfiger Polo", 5999, "Tommy Hilfiger", "Classic fit cotton polo with signature flag logo"),
        ("Casio G-Shock GA-2100", 10995, "Casio", "Carbon Core Guard structure, 200m water resistance"),
    ],
    "Home & Kitchen": [
        ("Dyson V15 Detect", 62900, "Dyson", "Cordless vacuum with laser dust detection and LCD screen"),
        ("Instant Pot Duo 7-in-1", 8999, "Instant Pot", "Multi-use pressure cooker, slow cooker, rice cooker"),
        ("Philips Air Fryer XXL", 14999, "Philips", "Family-size air fryer with rapid air technology"),
        ("Nespresso Vertuo Next", 15900, "Nespresso", "Coffee and espresso machine with centrifusion technology"),
    ],
    "Books": [
        ("Atomic Habits", 499, "Penguin", "James Clear's guide to building good habits and breaking bad ones"),
        ("Psychology of Money", 399, "Jaico", "Morgan Housel's timeless lessons on wealth and happiness"),
        ("Deep Work", 450, "Piatkus", "Cal Newport's rules for focused success in a distracted world"),
        ("Sapiens", 599, "Vintage", "Yuval Noah Harari's brief history of humankind"),
    ],
    "Beauty & Personal Care": [
        ("Dyson Airwrap Complete", 44900, "Dyson", "Multi-styler with Coanda airflow technology"),
        ("Forest Essentials Facial Kit", 3750, "Forest Essentials", "Luxury Ayurvedic facial care collection"),
        ("Kama Ayurveda Night Cream", 1895, "Kama Ayurveda", "Rejuvenating night cream with saffron and rose"),
    ],
}

SENTIMENTS = ["happy", "neutral", "frustrated", "angry", "excited"]
TICKET_MESSAGES = {
    "angry": [
        "This is absolutely unacceptable! I ordered 5 days ago and still no delivery. I want a full refund immediately!",
        "Worst experience ever. The product was damaged and customer care kept me waiting for 45 minutes. This is a scam!",
        "I am furious about the quality. This is not what was advertised. I demand a refund and compensation!",
        "Three times I have called your helpline and nobody resolves my issue. This is the worst service I have ever seen!",
        "You charged me twice for the same order! I want my money back RIGHT NOW or I will file a consumer complaint!",
    ],
    "frustrated": [
        "I've been waiting for my order for over a week now. The tracking hasn't updated in 3 days. Very disappointed.",
        "The product I received is the wrong color. I've tried contacting support twice with no response. Very annoying.",
        "My payment was deducted but the order shows as failed. This is really frustrating. Please help.",
        "I requested a return 10 days ago and still no pickup scheduled. How long does this take?",
        "The app keeps crashing when I try to track my order. I don't know what's happening with my delivery.",
    ],
    "happy": [
        "Excellent service! The product arrived a day early and was exactly as described. Thank you!",
        "Love the quality of the product. Great packaging too. Will definitely order again!",
        "Your customer support team was incredibly helpful. They resolved my issue in minutes. Amazing!",
        "The Diwali Sale deals were fantastic! Got amazing products at great prices. Very happy customer!",
        "Fast delivery, great quality, and the return process was so smooth. Best shopping experience!",
    ],
    "neutral": [
        "I'd like to know the status of my return request. Order #12345.",
        "Can you help me understand the warranty policy for electronics?",
        "I need to change the delivery address for my recent order. Is that possible?",
        "When will the iPhone 15 Pro be back in stock? I've been waiting for a while.",
        "Please provide an update on my refund. It was supposed to be processed 5 days ago.",
    ],
    "excited": [
        "Just got my new MacBook Air and it's AMAZING! The Big Billion Days deal was incredible!",
        "OMG the new collection is beautiful! Already added 5 items to my cart! Can't wait for the sale!",
        "Your recommendation engine is spot on! Found exactly what I was looking for. Love this platform!",
    ],
}
TICKET_SUBJECTS = {
    "angry": ["URGENT: Order not delivered - Demand refund", "Damaged product - Extremely disappointed", "Double charged - Need immediate resolution"],
    "frustrated": ["Order tracking not updating", "Wrong product received", "Payment deducted but order failed"],
    "happy": ["Great service - Thank you!", "Amazing product quality", "Excellent support experience"],
    "neutral": ["Return request status inquiry", "Warranty policy question", "Delivery address change request"],
    "excited": ["Amazing product received!", "Love the new collection!", "Best deals ever!"],
}

PERSONAS = ["Weekend Shopper", "Discount Seeker", "Premium Buyer", "Impulse Buyer", "Loyal Customer", "Value Seeker", "High-Risk Customer", "Brand Enthusiast"]
SEGMENTS = ["high_value", "medium", "low", "at_risk", "new"]
EVENT_TYPES = ["product_view", "search", "cart_add", "cart_remove", "wishlist_add", "purchase", "review_submit", "ticket_created", "offer_click", "message_open"]

# Campaign data aligned with the omnipulse_master_events.csv dataset
DATASET_CAMPAIGNS = [
    ("Diwali Sale", "email", "Up to 60% off on Electronics & Fashion", "completed"),
    ("Big Billion Days", "email", "Biggest sale of the year - up to 80% off", "completed"),
    ("Great Indian Festival", "sms", "Festival special deals across all categories", "active"),
    ("Independence Day Sale", "push", "Freedom sale - flat 50% off", "completed"),
    ("Republic Day Sale", "email", "Republic Day special - extra 20% cashback", "active"),
    ("Monsoon Mega Sale", "sms", "Monsoon deals - waterproof electronics & fashion", "active"),
    ("New Year Sale", "push", "Start 2025 with amazing deals", "completed"),
    ("Win-Back High Risk", "email", "20% off next purchase for at-risk customers", "active"),
    ("VIP Loyalty Rewards", "email", "Exclusive rewards for VIP segment", "active"),
    ("Trust Builder", "sms", "Service recovery offers for low-trust customers", "active"),
    ("First Purchase Incentive", "push", "15% off first order for new customers", "active"),
    ("Cross-Sell Campaign", "email", "Personalized product recommendations", "active"),
    ("Cart Rescue Campaign", "push", "Complete your purchase - 10% off", "active"),
]

# Journey templates with detailed steps
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

# Message templates across channels
MESSAGE_TEMPLATES = {
    "email": [
        ("Exclusive Deal Just For You!", "We've handpicked amazing deals based on your preferences. Up to 40% off on your favorite brands!", "exciting"),
        ("Your Cart Misses You", "You left some items in your cart. Complete your purchase now and get free delivery!", "empathetic"),
        ("Loyalty Reward Unlocked!", "You've earned 500 bonus loyalty points. Redeem them on your next order!", "professional"),
    ],
    "sms": [
        ("Flash Sale LIVE", "Extra 20% off on Electronics. Use code FLASH20. Shop now!", "exciting"),
        ("Order Update", "Your order has been shipped and will arrive by tomorrow.", "professional"),
    ],
    "push": [
        ("Price Drop Alert!", "The item you were eyeing just dropped in price! Get it before stock runs out.", "exciting"),
        ("Your Wishlist Item is Back", "Great news! Your wishlisted item is back in stock. Grab it now!", "empathetic"),
    ],
    "in_app": [
        ("Welcome Back!", "We missed you! Here's a special 15% discount to welcome you back.", "empathetic"),
        ("Rate Your Experience", "How was your recent purchase? Rate now and earn loyalty points!", "professional"),
    ],
}


def seed_database():
    """Seed the entire database with realistic demo data."""
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Customer).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding OmniPulse AI database...")

        # -- ADMIN USER --
        admin = Customer(
            customer_id="admin-001",
            first_name="Admin",
            last_name="OmniPulse",
            email="admin@omnipulse.ai",
            password_hash=hash_password("admin123"),
            role="admin",
            city="Bangalore",
            age=35,
            gender="male",
        )
        db.add(admin)
        db.add(CustomerProfile(customer_id="admin-001", trust_score=100, happiness_score=100))

        # -- PRODUCTS --
        products = []
        for category, items in CATEGORIES.items():
            for name, price, brand, desc in items:
                p = Product(
                    name=name,
                    category=category,
                    price=price,
                    original_price=round(price * random.uniform(1.1, 1.4), 0),
                    brand=brand,
                    description=desc,
                    rating=round(random.uniform(3.5, 5.0), 1),
                    review_count=random.randint(10, 500),
                    image_url=f"https://placehold.co/400x400/1a1d27/3b82f6?text={name.replace(' ', '+')[:15]}",
                )
                db.add(p)
                products.append(p)
        db.flush()
        print(f"  [OK] {len(products)} products created")

        # -- CUSTOMERS --
        customers = []
        for i in range(50):
            is_female = random.random() > 0.5
            fn = random.choice(FIRST_NAMES_F if is_female else FIRST_NAMES_M)
            ln = random.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}{random.randint(1,99)}@gmail.com"

            c = Customer(
                first_name=fn,
                last_name=ln,
                email=email,
                password_hash=hash_password("password123"),
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                gender="female" if is_female else "male",
                age=random.randint(18, 55),
                city=random.choice(CITIES),
                preferred_language=random.choice(LANGUAGES),
                registration_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            )
            db.add(c)
            customers.append(c)
        db.flush()
        print(f"  [OK] {len(customers)} customers created")

        # -- CUSTOMER PROFILES --
        for c in customers:
            churn = round(random.uniform(0.05, 0.95), 3)
            trust = round(random.uniform(20, 95), 1)
            happiness = round(random.uniform(20, 95), 1)
            clv = round(random.uniform(500, 50000), 0)

            profile = CustomerProfile(
                customer_id=c.customer_id,
                risk_score=round(churn * 100, 1),
                trust_score=trust,
                happiness_score=happiness,
                clv=clv,
                predicted_clv=round(clv * random.uniform(1.1, 1.8), 0),
                churn_probability=churn,
                persona=random.choice(PERSONAS),
                emotion=random.choice(SENTIMENTS),
                segment=random.choice(SEGMENTS),
                engagement_score=round(random.uniform(15, 95), 1),
                competitive_risk=round(random.uniform(0, 60), 1),
                recency_days=random.randint(1, 90),
                frequency=random.randint(1, 30),
                monetary=round(random.uniform(500, 30000), 0),
            )
            db.add(profile)
        print("  [OK] Customer profiles created")

        # -- ORDERS --
        orders_created = 0
        for c in customers:
            for _ in range(random.randint(1, 8)):
                prod = random.choice(products)
                qty = random.randint(1, 3)
                order = Order(
                    customer_id=c.customer_id,
                    total_amount=prod.price * qty,
                    status=random.choice(["delivered", "delivered", "shipped", "confirmed", "cancelled"]),
                    payment_method=random.choice(["card", "upi", "netbanking", "cod"]),
                    order_date=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                )
                db.add(order)
                db.flush()
                oi = OrderItem(order_id=order.order_id, product_id=prod.product_id, quantity=qty, price=prod.price)
                db.add(oi)
                orders_created += 1
        print(f"  [OK] {orders_created} orders created")

        # -- EVENTS --
        events_created = 0
        for c in customers:
            for _ in range(random.randint(20, 100)):
                et = random.choice(EVENT_TYPES)
                prod = random.choice(products)
                event = Event(
                    customer_id=c.customer_id,
                    event_type=et,
                    event_value=prod.name if et in ["product_view", "cart_add", "wishlist_add"] else None,
                    metadata_json={"product_id": prod.product_id, "category": prod.category} if et in ["product_view", "cart_add"] else {},
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
                )
                db.add(event)
                events_created += 1
        print(f"  [OK] {events_created} events created")

        # -- SUPPORT TICKETS --
        tickets_created = 0
        for c in customers[:30]:
            sentiment = random.choice(SENTIMENTS)
            msgs = TICKET_MESSAGES.get(sentiment, TICKET_MESSAGES["neutral"])
            subjects = TICKET_SUBJECTS.get(sentiment, TICKET_SUBJECTS["neutral"])

            # Sentiment score mapping
            score_map = {"angry": 0.15, "frustrated": 0.35, "neutral": 0.55, "happy": 0.80, "excited": 0.92}
            priority_map = {"angry": "high", "frustrated": "medium", "neutral": "medium", "happy": "low", "excited": "low"}

            if sentiment in ["angry", "frustrated"]:
                status = random.choice(["open", "open", "in_progress", "resolved"])
            else:
                status = random.choice(["open", "in_progress", "resolved", "resolved", "closed"])

            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 60))
            resolved_at = created_at + timedelta(hours=random.randint(1, 72)) if status in ["resolved", "closed"] else None

            ticket = SupportTicket(
                customer_id=c.customer_id,
                subject=random.choice(subjects),
                message=random.choice(msgs),
                sentiment=sentiment,
                sentiment_score=round(score_map[sentiment] + random.uniform(-0.1, 0.1), 2),
                status=status,
                priority=priority_map[sentiment],
                created_at=created_at,
                resolved_at=resolved_at,
            )
            db.add(ticket)
            tickets_created += 1

            # Some angry/frustrated customers have follow-up tickets
            if sentiment in ["angry", "frustrated"] and random.random() > 0.6:
                ticket2 = SupportTicket(
                    customer_id=c.customer_id,
                    subject=random.choice(subjects),
                    message=random.choice(msgs),
                    sentiment=sentiment,
                    sentiment_score=round(score_map[sentiment] + random.uniform(-0.05, 0.05), 2),
                    status=random.choice(["open", "in_progress"]),
                    priority="high",
                    created_at=created_at + timedelta(days=random.randint(1, 5)),
                )
                db.add(ticket2)
                tickets_created += 1
        print(f"  [OK] {tickets_created} support tickets created")

        # -- CAMPAIGNS (aligned with dataset) --
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
        db.flush()

        # Campaign responses
        for camp in campaigns:
            for c in random.sample(customers, min(20, len(customers))):
                opened = random.random() > 0.35
                clicked = opened and random.random() > 0.5
                converted = clicked and random.random() > 0.7

                resp = CampaignResponse(
                    campaign_id=camp.campaign_id,
                    customer_id=c.customer_id,
                    opened=opened,
                    clicked=clicked,
                    converted=converted,
                    revenue=round(random.uniform(500, 5000), 0) if converted else 0,
                    timestamp=camp.created_at + timedelta(hours=random.randint(1, 168)),
                )
                db.add(resp)
        print(f"  [OK] {len(campaigns)} campaigns created with responses")

        # -- MESSAGES --
        messages_created = 0
        for c in customers[:35]:
            for _ in range(random.randint(1, 4)):
                channel = random.choice(["email", "sms", "push", "in_app"])
                templates = MESSAGE_TEMPLATES[channel]
                subject, content, tone = random.choice(templates)

                msg = Message(
                    customer_id=c.customer_id,
                    channel=channel,
                    subject=subject,
                    content=content,
                    tone=tone,
                    opened=random.random() > 0.4,
                    clicked=random.random() > 0.65,
                    campaign_id=random.choice(campaigns).campaign_id if random.random() > 0.5 else None,
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                )
                db.add(msg)
                messages_created += 1
        print(f"  [OK] {messages_created} messages created")

        # -- JOURNEYS (all 4 types) --
        journeys_created = 0
        journey_types = list(JOURNEY_TEMPLATES.keys())
        for c in customers[:40]:
            jtype = random.choice(journey_types)
            steps = [dict(s) for s in JOURNEY_TEMPLATES[jtype]]

            # Randomly complete some steps
            completed = random.randint(1, len(steps))
            for i in range(completed):
                steps[i]["status"] = "completed"

            jstatus = "completed" if completed == len(steps) else "active"

            journey = Journey(
                customer_id=c.customer_id,
                journey_type=jtype,
                journey_stage=random.choice(["awareness", "consideration", "decision", "retention"]),
                journey_status=jstatus,
                steps=steps,
                current_step=completed - 1,
                created_at=datetime.utcnow() - timedelta(days=random.randint(5, 90)),
                completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 5)) if jstatus == "completed" else None,
            )
            db.add(journey)
            journeys_created += 1
        print(f"  [OK] {journeys_created} journeys created ({', '.join(journey_types)})")

        # -- DIGITAL TWIN RESULTS --
        dt_created = 0
        for c in customers[:20]:
            profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == c.customer_id).first()
            churn_prob = profile.churn_probability if profile and profile.churn_probability else 0.5
            clv = profile.clv if profile and profile.clv else 5000

            # No-action scenario
            dt_no = DigitalTwinResult(
                customer_id=c.customer_id,
                scenario="no_action",
                prediction={"outcome": "Customer Likely To Churn" if churn_prob > 0.6 else "Gradual Disengagement", "churn_probability": round(churn_prob, 3)},
                predicted_revenue=round(clv * (1 - churn_prob), 0),
                predicted_retention=round(1 - churn_prob, 3),
                predicted_churn=round(churn_prob, 3),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.add(dt_no)

            # Intervention scenario
            improved_churn = churn_prob * random.uniform(0.3, 0.7)
            intervention = random.choice(["Personalized Discount", "Customer Success Call", "VIP Upgrade Offer", "Loyalty Points Boost"])
            dt_int = DigitalTwinResult(
                customer_id=c.customer_id,
                scenario="intervention",
                prediction={"outcome": "Retention Improved", "intervention": intervention, "churn_reduction": round((churn_prob - improved_churn) * 100, 1)},
                predicted_revenue=round(clv * (1 - improved_churn) * 1.1, 0),
                predicted_retention=round(1 - improved_churn, 3),
                predicted_churn=round(improved_churn, 3),
                intervention_type=intervention,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.add(dt_int)

            # Comparison scenario
            dt_comp = DigitalTwinResult(
                customer_id=c.customer_id,
                scenario="comparison",
                prediction={"no_action_churn": round(churn_prob, 3), "intervention_churn": round(improved_churn, 3), "revenue_saved": round(clv * (churn_prob - improved_churn), 0), "recommended_intervention": intervention},
                predicted_revenue=round(clv * (churn_prob - improved_churn), 0),
                predicted_retention=round((churn_prob - improved_churn), 3),
                predicted_churn=round(improved_churn, 3),
                intervention_type=intervention,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            db.add(dt_comp)
            dt_created += 3
        print(f"  [OK] {dt_created} digital twin results created")

        # -- EXECUTIVE SUMMARIES --
        summaries = [
            ExecutiveSummary(
                summary_text="Weekly Business Intelligence Report - OmniPulse AI Platform",
                metrics={"total_customers": len(customers), "total_revenue": sum(p.price for p in products) * 2, "avg_order_value": 5200, "nps_score": 42, "churn_rate": 8.3},
                highlights=["AI-driven churn rescue journeys saved Rs 2.3M", "Diwali Sale campaign achieved 65% open rate", "Customer trust score improved 12%"],
                risks=["15 customers at-risk of churning", "Cart abandonment rate at 68%", "Support ticket volume increased 15%"],
                recommendations=["Deploy WhatsApp campaigns for at-risk segment", "Implement cart rescue with dynamic pricing", "Scale customer success calls for top accounts"],
                generated_at=datetime.utcnow(),
            ),
            ExecutiveSummary(
                summary_text="AI/ML Performance Dashboard - Model Accuracy & Impact Report",
                metrics={"churn_model_accuracy": 87.3, "nba_acceptance_rate": 72.1, "sentiment_accuracy": 91.5, "clv_prediction_mape": 12.8},
                highlights=["Churn prediction model at 87.3% accuracy", "NBA engine: 72.1% acceptance rate", "Digital twin simulations show 40% churn reduction"],
                risks=["CLV prediction needs recalibration", "Cold-start problem for new customers"],
                recommendations=["Retrain CLV model with latest data", "A/B test NBA engine v2"],
                generated_at=datetime.utcnow() - timedelta(days=3),
            ),
        ]
        for s in summaries:
            db.add(s)
        print(f"  [OK] {len(summaries)} executive summaries created")

        db.commit()
        print("\nDatabase seeded successfully!")
        print(f"   Admin login: admin@omnipulse.ai / admin123")
        print(f"   Customer login: {customers[0].email} / password123")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
