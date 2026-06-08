"""
OMNIPULSE AI - DISTRIBUTION REBALANCING
Phases 3-6: Fix unrealistic 100% churn by adjusting scoring algorithms
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

DATABASE_URL = "sqlite:///omnipulse.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

print("="*80)
print("OMNIPULSE AI - DISTRIBUTION REBALANCING")
print("="*80)

# ============================================================================
# PHASE 3: CHURN ENGINE REBUILD
# ============================================================================
print("\n[PHASE 3] CHURN ENGINE REBUILD - Fixing 100% Critical churn...")
print("-"*80)

session = Session()

# Get all customer profiles with their data
profiles_df = pd.read_sql(text("""
    SELECT 
        cp.customer_id,
        cp.clv,
        cp.engagement_score,
        cp.trust_score,
        COUNT(DISTINCT o.order_id) as order_count,
        SUM(o.total_amount) as total_revenue,
        COUNT(DISTINCT e.event_id) as event_count
    FROM customer_profiles cp
    LEFT JOIN orders o ON cp.customer_id = o.customer_id AND o.status != 'cancelled'
    LEFT JOIN events e ON cp.customer_id = e.customer_id
    GROUP BY cp.customer_id
"""), engine)

print(f"  [INFO] Rebalancing churn for {len(profiles_df)} customers...")

# Calculate percentiles for realistic segmentation
profiles_df['revenue_percentile'] = profiles_df['total_revenue'].rank(pct=True)
profiles_df['order_percentile'] = profiles_df['order_count'].rank(pct=True)
profiles_df['event_percentile'] = profiles_df['event_count'].rank(pct=True)
profiles_df['engagement_percentile'] = profiles_df['engagement_score'].rank(pct=True)

profiles_updated = 0

for idx, profile in profiles_df.iterrows():
    # New percentile-based churn calculation
    # Low performers = high churn, high performers = low churn
    
    # Weighted percentile score (higher = better customer)
    customer_score = (
        profile['revenue_percentile'] * 0.30 +
        profile['order_percentile'] * 0.25 +
        profile['event_percentile'] * 0.20 +
        profile['engagement_percentile'] * 0.15 +
        (profile['trust_score'] / 100) * 0.10
    )
    
    # Invert to get churn (high score = low churn)
    churn_probability = 1 - customer_score
    
    # Add some randomness for realism (+/- 0.1)
    churn_probability += np.random.uniform(-0.1, 0.1)
    churn_probability = max(0.05, min(0.95, churn_probability))
    
    # Calculate risk level
    if churn_probability < 0.3:
        risk_level = 'Low'
    elif churn_probability < 0.6:
        risk_level = 'Medium'
    elif churn_probability < 0.75:
        risk_level = 'High'
    else:
        risk_level = 'Critical'
    
    # Update profile
    try:
        update_query = text("""
            UPDATE customer_profiles 
            SET churn_probability = :churn_probability,
                risk_score = :risk_score
            WHERE customer_id = :customer_id
        """)
        
        session.execute(update_query, {
            'customer_id': profile['customer_id'],
            'churn_probability': float(churn_probability),
            'risk_score': float(churn_probability * 100)
        })
        
        profiles_updated += 1
        
        if profiles_updated % 500 == 0:
            session.commit()
            print(f"  [INFO] Rebalanced {profiles_updated} profiles...")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        continue

session.commit()
print(f"\n[SUCCESS] Rebalanced churn for {profiles_updated} customers")

# ============================================================================
# PHASE 4: EMOTION ENGINE REBUILD
# ============================================================================
print("\n[PHASE 4] EMOTION ENGINE REBUILD - Creating balanced distribution...")
print("-"*80)

# Get updated profiles with new churn scores
profiles_df = pd.read_sql(text("""
    SELECT customer_id, churn_probability, trust_score, engagement_score, clv
    FROM customer_profiles
"""), engine)

emotions_updated = 0

for idx, profile in profiles_df.iterrows():
    # Emotion based on combined factors
    combined_score = (
        (1 - profile['churn_probability']) * 0.4 +
        (profile['trust_score'] / 100) * 0.3 +
        (profile['engagement_score'] / 100) * 0.3
    )
    
    # Map to emotions with balanced distribution
    if combined_score > 0.75:
        emotion = np.random.choice(['happy', 'excited'], p=[0.7, 0.3])
    elif combined_score > 0.55:
        emotion = np.random.choice(['happy', 'neutral'], p=[0.6, 0.4])
    elif combined_score > 0.40:
        emotion = 'neutral'
    elif combined_score > 0.25:
        emotion = np.random.choice(['neutral', 'frustrated'], p=[0.4, 0.6])
    else:
        emotion = np.random.choice(['frustrated', 'angry'], p=[0.7, 0.3])
    
    # Happiness score from emotion
    emotion_happiness_map = {
        'angry': 20,
        'frustrated': 40,
        'neutral': 55,
        'happy': 75,
        'excited': 90
    }
    happiness_score = emotion_happiness_map[emotion]
    
    try:
        update_query = text("""
            UPDATE customer_profiles 
            SET emotion = :emotion,
                happiness_score = :happiness_score
            WHERE customer_id = :customer_id
        """)
        
        session.execute(update_query, {
            'customer_id': profile['customer_id'],
            'emotion': emotion,
            'happiness_score': float(happiness_score)
        })
        
        emotions_updated += 1
        
        if emotions_updated % 500 == 0:
            session.commit()
            print(f"  [INFO] Updated {emotions_updated} emotions...")
        
    except Exception as e:
        continue

session.commit()
print(f"\n[SUCCESS] Rebalanced emotions for {emotions_updated} customers")

# ============================================================================
# PHASE 5: TRUST ENGINE REBUILD
# ============================================================================
print("\n[PHASE 5] TRUST ENGINE REBUILD - Creating balanced distribution...")
print("-"*80)

profiles_df = pd.read_sql(text("""
    SELECT 
        cp.customer_id,
        COUNT(DISTINCT o.order_id) as order_count,
        SUM(o.total_amount) as total_revenue,
        COUNT(DISTINCT e.event_id) as event_count,
        COUNT(DISTINCT st.ticket_id) as ticket_count
    FROM customer_profiles cp
    LEFT JOIN orders o ON cp.customer_id = o.customer_id AND o.status != 'cancelled'
    LEFT JOIN events e ON cp.customer_id = e.customer_id
    LEFT JOIN support_tickets st ON cp.customer_id = st.customer_id
    GROUP BY cp.customer_id
"""), engine)

# Calculate trust percentiles
profiles_df['trust_percentile'] = (
    profiles_df['order_count'].rank(pct=True) * 0.35 +
    profiles_df['total_revenue'].rank(pct=True) * 0.30 +
    profiles_df['event_count'].rank(pct=True) * 0.25 +
    (1 - profiles_df['ticket_count'].rank(pct=True)) * 0.10
)

trust_updated = 0

for idx, profile in profiles_df.iterrows():
    # Convert percentile to trust score (0-100)
    base_trust = profile['trust_percentile'] * 100
    
    # Add small random variation
    trust_score = base_trust + np.random.uniform(-5, 5)
    trust_score = max(20, min(100, trust_score))
    
    # Trust level
    if trust_score < 40:
        trust_level = 'Low'
    elif trust_score < 70:
        trust_level = 'Medium'
    else:
        trust_level = 'High'
    
    try:
        update_query = text("""
            UPDATE customer_profiles 
            SET trust_score = :trust_score
            WHERE customer_id = :customer_id
        """)
        
        session.execute(update_query, {
            'customer_id': profile['customer_id'],
            'trust_score': float(trust_score)
        })
        
        trust_updated += 1
        
        if trust_updated % 500 == 0:
            session.commit()
            print(f"  [INFO] Updated {trust_updated} trust scores...")
        
    except Exception as e:
        continue

session.commit()
print(f"\n[SUCCESS] Rebalanced trust for {trust_updated} customers")

# ============================================================================
# PHASE 6: PERSONA & SEGMENT REBALANCING
# ============================================================================
print("\n[PHASE 6] PERSONA & SEGMENT REBUILD - Creating realistic distribution...")
print("-"*80)

profiles_df = pd.read_sql(text("""
    SELECT customer_id, clv, churn_probability, trust_score, engagement_score
    FROM customer_profiles
"""), engine)

personas_updated = 0

for idx, profile in profiles_df.iterrows():
    # Determine persona based on CLV, churn, and engagement
    if profile['clv'] > 10000 and profile['churn_probability'] < 0.5:
        persona = 'VIP'
        segment = 'VIP'
    elif profile['clv'] > 5000 and profile['churn_probability'] < 0.6:
        persona = 'Loyal'
        segment = 'Loyal'
    elif profile['churn_probability'] > 0.70:
        persona = 'At-Risk'
        segment = 'At-Risk'
    elif profile['engagement_score'] < 30:
        persona = 'Inactive'
        segment = 'Inactive'
    elif profile['clv'] > 1000:
        persona = 'Regular'
        segment = 'Active'
    elif profile['clv'] > 0:
        persona = 'New'
        segment = 'Active'
    else:
        persona = 'Visitor'
        segment = 'Visitor'
    
    # Journey stage
    if persona == 'Visitor':
        journey_stage = 'visitor'
    elif persona == 'New':
        journey_stage = 'first_purchase'
    elif persona in ['VIP', 'Loyal']:
        journey_stage = 'loyal'
    elif persona == 'At-Risk':
        journey_stage = 'at_risk'
    elif persona == 'Inactive':
        journey_stage = 'inactive'
    else:
        journey_stage = 'active'
    
    try:
        update_query = text("""
            UPDATE customer_profiles 
            SET persona = :persona,
                segment = :segment,
                journey_stage = :journey_stage
            WHERE customer_id = :customer_id
        """)
        
        session.execute(update_query, {
            'customer_id': profile['customer_id'],
            'persona': persona,
            'segment': segment,
            'journey_stage': journey_stage
        })
        
        personas_updated += 1
        
        if personas_updated % 500 == 0:
            session.commit()
            print(f"  [INFO] Updated {personas_updated} personas...")
        
    except Exception as e:
        continue

session.commit()
print(f"\n[SUCCESS] Rebalanced personas for {personas_updated} customers")

session.close()

print("\n" + "="*80)
print("[PHASES 3-6 COMPLETE]")
print("="*80)

# ============================================================================
# VALIDATION
# ============================================================================
print("\n[VALIDATION] Checking new distributions...")
print("-"*80)

print("\nChurn Distribution:")
churn_dist = pd.read_sql(text("""
    SELECT 
        CASE 
            WHEN churn_probability < 0.3 THEN 'Low'
            WHEN churn_probability < 0.6 THEN 'Medium'
            WHEN churn_probability < 0.75 THEN 'High'
            ELSE 'Critical'
        END as risk_level,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY risk_level
    ORDER BY 
        CASE risk_level
            WHEN 'Low' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'High' THEN 3
            WHEN 'Critical' THEN 4
        END
"""), engine)
print(churn_dist.to_string(index=False))

print("\nEmotion Distribution:")
emotion_dist = pd.read_sql(text("""
    SELECT emotion, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY emotion
    ORDER BY count DESC
"""), engine)
print(emotion_dist.to_string(index=False))

print("\nTrust Distribution:")
trust_dist = pd.read_sql(text("""
    SELECT 
        CASE 
            WHEN trust_score < 40 THEN 'Low'
            WHEN trust_score < 70 THEN 'Medium'
            ELSE 'High'
        END as trust_level,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY trust_level
    ORDER BY count DESC
"""), engine)
print(trust_dist.to_string(index=False))

print("\nPersona Distribution:")
persona_dist = pd.read_sql(text("""
    SELECT persona, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY persona
    ORDER BY count DESC
"""), engine)
print(persona_dist.to_string(index=False))

print("\nSegment Distribution:")
segment_dist = pd.read_sql(text("""
    SELECT segment, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY segment
    ORDER BY count DESC
"""), engine)
print(segment_dist.to_string(index=False))

print("\nJourney Stage Distribution:")
journey_dist = pd.read_sql(text("""
    SELECT journey_stage, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_profiles), 1) as percentage
    FROM customer_profiles
    GROUP BY journey_stage
    ORDER BY count DESC
"""), engine)
print(journey_dist.to_string(index=False))

print("\n" + "="*80)
print("[DISTRIBUTION REBALANCING COMPLETE]")
print("="*80)
