"""
REGENERATE NBA DECISIONS WITH DIVERSITY
Generate realistic NBA recommendations based on customer signals
"""
import sqlite3
import random
import uuid
from datetime import datetime, timedelta

conn = sqlite3.connect('omnipulse.db')
cur = conn.cursor()

print("="*80)
print("REGENERATING NBA DECISIONS")
print("="*80)

# Delete existing NBA decisions
print("\n[1] Deleting existing NBA decisions...")
cur.execute("DELETE FROM nba_decisions")
conn.commit()
print(f"✓ Deleted old decisions")

# Get all customer profiles
cur.execute("""
    SELECT 
        customer_id,
        churn_probability,
        trust_score,
        engagement_score,
        frequency,
        recency_days,
        monetary,
        clv,
        persona,
        emotion
    FROM customer_profiles
""")
customers = cur.fetchall()
print(f"\n[2] Found {len(customers):,} customers")

# Define action logic based on customer signals
def determine_action(churn, trust, engagement, frequency, clv, persona):
    """Determine NBA action based on customer signals"""
    
    # Critical churn (>80%)
    if churn > 0.80:
        if clv > 10000:
            return "winback_offer"  # High value churners get winback
        elif trust < 50:
            return "trust_recovery"  # Low trust needs trust recovery
        else:
            return "churn_rescue"  # Standard churn rescue
    
    # High churn (60-80%)
    elif churn > 0.60:
        if engagement < 20:
            return "re_engagement"  # Low engagement needs re-engagement
        elif frequency > 5:
            return "retention_bonus"  # Frequent buyers get retention bonus
        else:
            return "loyalty_reward"  # Others get loyalty reward
    
    # Medium churn (30-60%)
    elif churn > 0.30:
        if clv > 5000:
            return "premium_upgrade"  # Mid-value customers get premium upgrade
        elif persona in ['bargain_hunter', 'price_sensitive']:
            return "loyalty_reward"  # Price sensitive get loyalty reward
        else:
            return "cross_sell"  # Others get cross-sell
    
    # Low churn (<30%)
    else:
        if clv > 8000:
            return "premium_upgrade"  # High value get premium upgrade
        elif engagement > 60:
            return "upsell"  # High engagement get upsell
        else:
            return "cross_sell"  # Others get cross-sell

# Define channel logic based on customer signals
def determine_channel(engagement, trust, persona, age_group):
    """Determine channel based on customer signals"""
    
    # High engagement customers prefer digital
    if engagement > 60:
        return random.choice(['WhatsApp', 'Push', 'SMS'])
    
    # Low trust customers prefer human touch
    elif trust < 50:
        return random.choice(['Email', 'Call'])
    
    # Tech-savvy personas
    elif persona in ['tech_enthusiast', 'early_adopter']:
        return random.choice(['WhatsApp', 'Push'])
    
    # Traditional personas
    elif persona in ['traditional', 'bargain_hunter']:
        return random.choice(['Email', 'SMS'])
    
    # Default distribution
    else:
        return random.choice(['Email', 'SMS', 'WhatsApp', 'Push'])

# Define offer logic based on action and customer value
def determine_offer(action, churn, trust, clv, persona):
    """Determine offer based on action and customer value"""
    
    if action == "winback_offer":
        if clv > 15000:
            return "40% discount + free premium membership for 6 months"
        elif clv > 10000:
            return "35% discount + free shipping for 3 months"
        else:
            return "30% discount + exclusive gift"
    
    elif action == "churn_rescue":
        if churn > 0.85:
            return "25% discount + priority support for 1 month"
        else:
            return "20% discount + free shipping"
    
    elif action == "trust_recovery":
        return "Personal account manager + 15% loyalty discount"
    
    elif action == "retention_bonus":
        if clv > 8000:
            return "500 loyalty points + free express shipping"
        else:
            return "300 loyalty points + 10% next purchase"
    
    elif action == "loyalty_reward":
        if persona in ['bargain_hunter', 'price_sensitive']:
            return "15% discount + double reward points"
        else:
            return "Free product upgrade + extended warranty"
    
    elif action == "premium_upgrade":
        return "Premium membership trial (3 months free) + exclusive perks"
    
    elif action == "upsell":
        return "Bundle deal: Buy 2 get 20% off + free accessories"
    
    elif action == "cross_sell":
        return "Personalized product recommendations + 10% bundle discount"
    
    elif action == "re_engagement":
        return "Exclusive comeback offer: 25% off + surprise gift"
    
    else:
        return "Special offer based on your preferences"

# Generate NBA decisions for each customer
print("\n[3] Generating NBA decisions...")
decisions_created = 0
inference_tiers = {'rules': 0, 'ml': 0}
actions_count = {}
channels_count = {}

for customer in customers:
    customer_id, churn, trust, engagement, frequency, recency, monetary, clv, persona, emotion = customer
    
    # Determine action
    action = determine_action(churn, trust, engagement, frequency, clv, persona)
    
    # Determine channel
    age_group = "unknown"  # We don't have age in profiles
    channel = determine_channel(engagement, trust, persona, age_group)
    
    # Determine offer
    offer = determine_offer(action, churn, trust, clv, persona)
    
    # Determine inference tier (10% ML, 90% rules)
    inference_tier = "ml" if random.random() < 0.10 else "rules"
    
    # Calculate base confidence (will be replaced by dynamic calculation in API)
    # But we'll store a reasonable base value
    base_confidence = 0.75 + (random.random() * 0.15)  # 0.75-0.90
    
    # Determine tone
    if emotion in ['angry', 'frustrated']:
        tone = 'apologetic'
    elif emotion in ['happy', 'satisfied']:
        tone = 'celebratory'
    elif trust < 50:
        tone = 'reassuring'
    else:
        tone = 'friendly'
    
    # Determine timing
    if recency > 60:
        timing = 'immediate'
    elif engagement < 20:
        timing = 'morning'
    else:
        timing = 'afternoon'
    
    # Create decision
    decision_id = str(uuid.uuid4())
    timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 72))
    
    cur.execute("""
        INSERT INTO nba_decisions (
            decision_id, customer_id, recommended_action, channel, offer,
            confidence, inference_tier, tone, timing, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision_id, customer_id, action, channel, offer,
        base_confidence, inference_tier, tone, timing, timestamp
    ))
    
    decisions_created += 1
    inference_tiers[inference_tier] += 1
    actions_count[action] = actions_count.get(action, 0) + 1
    channels_count[channel] = channels_count.get(channel, 0) + 1

conn.commit()

print(f"✓ Created {decisions_created:,} NBA decisions")

print("\n[4] DISTRIBUTION SUMMARY:")
print("-"*80)

print("\nInference Tiers:")
for tier, count in sorted(inference_tiers.items()):
    pct = count / decisions_created * 100
    print(f"  {tier}: {count:,} ({pct:.1f}%)")

print("\nActions:")
for action, count in sorted(actions_count.items(), key=lambda x: x[1], reverse=True):
    pct = count / decisions_created * 100
    print(f"  {action}: {count:,} ({pct:.1f}%)")

print("\nChannels:")
for channel, count in sorted(channels_count.items(), key=lambda x: x[1], reverse=True):
    pct = count / decisions_created * 100
    print(f"  {channel}: {count:,} ({pct:.1f}%)")

# Verify diversity
print("\n[5] DIVERSITY VERIFICATION:")
print("-"*80)
print(f"Unique actions: {len(actions_count)}")
print(f"Unique channels: {len(channels_count)}")
print(f"ML decisions: {inference_tiers['ml']:,} ({inference_tiers['ml']/decisions_created*100:.1f}%)")
print(f"Rules decisions: {inference_tiers['rules']:,} ({inference_tiers['rules']/decisions_created*100:.1f}%)")

# Sample high churn customers
print("\n[6] SAMPLE HIGH-RISK RECOMMENDATIONS:")
print("-"*80)
cur.execute("""
    SELECT 
        p.customer_id,
        p.churn_probability,
        n.recommended_action,
        n.channel,
        n.confidence
    FROM customer_profiles p
    JOIN nba_decisions n ON p.customer_id = n.customer_id
    WHERE p.churn_probability > 0.80
    ORDER BY p.churn_probability DESC
    LIMIT 10
""")
print(f"{'Customer ID':<15} {'Churn':>6} {'Action':<20} {'Channel':<10} {'Conf':>6}")
print("-"*65)
for row in cur.fetchall():
    print(f"{row[0]:<15} {row[1]:>6.2f} {row[2]:<20} {row[3]:<10} {row[4]:>6.2f}")

conn.close()

print("\n" + "="*80)
print("NBA DECISIONS REGENERATION COMPLETE")
print("="*80)
print("\nNext steps:")
print("1. Restart backend server to reload API")
print("2. Test NBA endpoint: python test_nba_endpoint.py")
print("3. Refresh NBA Center frontend to see diverse recommendations")
print("="*80)
