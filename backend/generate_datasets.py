import random
import uuid
import csv
from datetime import datetime, timedelta

random.seed(42)

# ── MASTER DATA ─────────────────────────────────────────────────

FIRST_NAMES = ["Priya","Rahul","Ananya","Amit","Neha","Arjun","Sneha","Rohan","Pooja","Vikram",
                "Ishaan","Kavya","Siddharth","Divya","Manish","Riya","Karan","Meera","Aditya","Nisha",
                "Varun","Shruti","Dhruv","Pallavi","Rajesh","Deepika","Suresh","Sakshi","Ankit","Lavanya",
                "Harsh","Tanya","Pranav","Simran","Dev","Kritika","Nikhil","Aisha","Aarav","Sonal"]

LAST_NAMES = ["Sharma","Verma","Reddy","Kumar","Singh","Patel","Iyer","Gupta","Nair","Rao",
               "Mehta","Joshi","Chopra","Desai","Malhotra","Bhat","Pillai","Menon","Shah","Kapoor"]

CITIES_STATES = [
    ("Mumbai","Maharashtra"),("Delhi","Delhi"),("Bengaluru","Karnataka"),
    ("Hyderabad","Telangana"),("Chennai","Tamil Nadu"),("Pune","Maharashtra"),
    ("Ahmedabad","Gujarat"),("Kolkata","West Bengal"),("Jaipur","Rajasthan"),
    ("Lucknow","Uttar Pradesh"),("Kochi","Kerala"),("Indore","Madhya Pradesh"),
    ("Nagpur","Maharashtra"),("Surat","Gujarat"),("Noida","Uttar Pradesh")
]

PRODUCTS = [
    ("P001","iPhone 15 Pro","Electronics",134900),
    ("P002","Samsung Galaxy S24","Electronics",79999),
    ("P003","boAt Airdopes 141","Electronics",1299),
    ("P004","OnePlus Nord CE4","Electronics",24999),
    ("P005","Lenovo IdeaPad Slim","Electronics",45999),
    ("P006","Levis 511 Slim Jeans","Fashion",2499),
    ("P007","Nike Air Max 270","Fashion",12995),
    ("P008","Fabindia Kurta Set","Fashion",3499),
    ("P009","Raymond Suit","Fashion",8999),
    ("P010","Bata Formal Shoes","Footwear",2299),
    ("P011","Puma Running Shoes","Footwear",5999),
    ("P012","Prestige Induction Cooktop","Home",3299),
    ("P013","Milton Steel Bottle","Home",599),
    ("P014","Godrej Refrigerator","Home",32990),
    ("P015","Lakme Foundation","Beauty",649),
    ("P016","Mamaearth Facewash","Beauty",299),
    ("P017","Biotique Sunscreen","Beauty",399),
    ("P018","Cosco Cricket Bat","Sports",1499),
    ("P019","Nivia Football","Sports",799),
    ("P020","Atomic Habits Book","Books",499),
    ("P021","Rich Dad Poor Dad","Books",399),
    ("P022","Fastrack Watch","Accessories",2199),
    ("P023","Titan Analog Watch","Accessories",4599),
    ("P024","Noise ColorFit Pro","Accessories",5999),
    ("P025","Wildcraft Backpack","Accessories",1899),
]

CAMPAIGNS = ["Diwali Sale","Great Indian Festival","Big Billion Days",
             "Republic Day Sale","Independence Day Sale","Monsoon Mega Sale","New Year Sale"]

CHANNELS = ["Email","SMS","Push Notification","WhatsApp","Support Chat"]

EMOTIONS_MAP = {
    "complaint":       ["Frustrated","Angry","Frustrated","Angry","Neutral"],
    "refund_request":  ["Frustrated","Angry","Neutral"],
    "purchase":        ["Happy","Excited","Happy","Happy"],
    "review_submit":   ["Happy","Neutral","Excited","Happy"],
    "cart_add":        ["Excited","Happy","Neutral"],
    "wishlist_add":    ["Happy","Excited","Neutral"],
    "product_view":    ["Neutral","Happy","Excited","Neutral"],
    "search":          ["Neutral","Neutral","Happy"],
    "cart_remove":     ["Neutral","Frustrated","Neutral"],
    "checkout":        ["Excited","Happy","Neutral"],
    "campaign_received":["Neutral","Happy","Neutral","Excited"],
    "campaign_opened": ["Excited","Happy","Neutral"],
    "offer_clicked":   ["Excited","Happy","Happy"],
    "support_chat":    ["Frustrated","Neutral","Angry","Neutral"],
    "assistant_interaction":["Neutral","Happy","Neutral"],
}

SENTIMENT_MAP = {
    "Happy":"Positive","Excited":"Positive",
    "Neutral":"Neutral",
    "Frustrated":"Negative","Angry":"Negative"
}

TICKET_TEXTS = [
    "My order hasn't arrived yet. It's been 7 days!",
    "Wrong product delivered. I ordered electronics but got something else.",
    "I want to return this item. Quality is very poor.",
    "Payment deducted but order not confirmed. Please help.",
    "The product stopped working after 2 days. Need replacement.",
    "Delivery was delayed by 5 days without any notification.",
    "Customer support is not responding to my emails.",
    "I was charged twice for the same order. Please refund.",
    "Product description was misleading. Not as advertised.",
    "Packaging was damaged. Product might be defective.",
]

MESSAGE_TEXTS = {
    "Email": [
        "Exclusive Diwali offers just for you! Up to 50% off on top brands.",
        "Your wishlist items are on sale today only. Don't miss out!",
        "Claim your loyalty reward before it expires this weekend.",
        "We noticed you left items in your cart. Complete your order now.",
        "New arrivals in Electronics - handpicked for you, {name}!",
    ],
    "SMS": [
        "OmniPulse: 20% OFF on your next order. Use code SAVE20. Valid 24hrs.",
        "Hi {name}, your exclusive offer expires tonight. Shop now!",
        "Flash Sale LIVE! Extra 15% off Electronics. Hurry limited stock.",
        "Your cart is waiting! Complete purchase & get free delivery.",
        "New season fashion is here. Up to 40% off top brands.",
    ],
    "WhatsApp": [
        "Hi {name}! We have a special offer just for you - 15% off your next purchase. Tap to shop.",
        "Your order is on its way! Track it here and get excited.",
        "Festival special: Buy 2 get 1 free on Fashion & Accessories!",
        "We miss you {name}! Come back and enjoy extra 10% off.",
        "Your loyalty points are expiring soon. Use them before they expire!",
    ],
    "Push Notification": [
        "FLASH SALE: 2 hours only! Extra 25% off Electronics.",
        "Price drop alert on your wishlist item!",
        "Limited stock - your saved item selling fast!",
        "Congratulations! You've unlocked a special reward.",
        "Today's deal: Free delivery on all orders above Rs 499.",
    ],
    "Support Chat": [
        "Thank you for contacting support. How can I help you today?",
        "I understand your concern. Let me check your order status right away.",
        "Your refund has been initiated and will reflect in 5-7 business days.",
        "I apologize for the inconvenience. I am escalating this to our team.",
        "Your issue has been resolved. Is there anything else I can help with?",
    ],
}

PERSONAS = ["Discount Hunter","Premium Buyer","Weekend Shopper","Impulse Buyer",
            "Tech Enthusiast","Fashion Explorer","Loyal Customer","High Value Customer"]

NBA_ACTIONS = ["Send Email","Send SMS","Give Discount","Offer Loyalty Points",
               "Recommend Product","Trigger Journey","Customer Success Call","WhatsApp Reminder"]

OFFERS = ["5 Percent Discount","10 Percent Discount","15 Percent Discount",
          "20 Percent Discount","Free Delivery","Bonus Loyalty Points","Exclusive Offer"]

DIGITAL_TWIN_OUTCOMES = ["Customer Likely To Churn","Customer Likely To Stay",
                          "Revenue Growth Expected","High Engagement Predicted","Retention Improved"]

# ── BUILD CUSTOMER PROFILES ─────────────────────────────────────

def make_customer_id():
    return "CUST-" + str(uuid.uuid4())[:8].upper()

def make_name():
    return random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)

def make_timestamp(start_days_ago=365, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end   = datetime.now() - timedelta(days=end_days_ago)
    delta = end - start
    return (start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))).strftime("%Y-%m-%d %H:%M:%S")

# Generate 500 unique customers
NUM_CUSTOMERS = 500
customers = []
for _ in range(NUM_CUSTOMERS):
    name = make_name()
    city, state = random.choice(CITIES_STATES)
    age = random.randint(18, 55)
    gender = random.choice(["Male","Female","Male","Female","Female"])

    # Assign risk profile
    profile_type = random.choices(["at_risk","healthy","neutral"],[0.25,0.50,0.25])[0]

    if profile_type == "at_risk":
        trust   = round(random.uniform(10, 40), 1)
        happy   = round(random.uniform(10, 45), 1)
        risk    = round(random.uniform(65, 95), 1)
        num_events = random.randint(8, 20)
    elif profile_type == "healthy":
        trust   = round(random.uniform(65, 98), 1)
        happy   = round(random.uniform(60, 98), 1)
        risk    = round(random.uniform(5, 30), 1)
        num_events = random.randint(20, 60)
    else:
        trust   = round(random.uniform(35, 70), 1)
        happy   = round(random.uniform(35, 70), 1)
        risk    = round(random.uniform(25, 65), 1)
        num_events = random.randint(10, 30)

    customers.append({
        "customer_id": make_customer_id(),
        "name": name,
        "age": age,
        "gender": gender,
        "city": city,
        "state": state,
        "profile_type": profile_type,
        "trust_score": trust,
        "happiness_score": happy,
        "risk_score": risk,
        "num_events": num_events,
    })

# ── DATASET 1: omnipulse_master_events.csv ──────────────────────

EVENT_TYPES = ["product_view","search","wishlist_add","cart_add","cart_remove",
               "checkout","purchase","review_submit","complaint","refund_request",
               "campaign_received","campaign_opened","offer_clicked","support_chat","assistant_interaction"]

rows_events = []
target_rows = 15000
event_counter = 0

while len(rows_events) < target_rows:
    c = random.choice(customers)
    num_e = random.randint(1, max(1, c["num_events"] // 4))

    for _ in range(num_e):
        if len(rows_events) >= target_rows:
            break

        prod = random.choice(PRODUCTS)
        event_type = random.choices(
            EVENT_TYPES,
            weights=[12,8,6,10,5,4,8,5,4,3,7,6,6,4,3],
            k=1
        )[0]

        emotion = random.choice(EMOTIONS_MAP.get(event_type, ["Neutral"]))
        sentiment = SENTIMENT_MAP[emotion]
        channel   = random.choice(CHANNELS)
        campaign  = random.choice(CAMPAIGNS) if event_type in ["campaign_received","campaign_opened","offer_clicked"] else ""

        # message text
        if event_type in ["campaign_received","campaign_opened","offer_clicked"]:
            msg_pool = MESSAGE_TEXTS.get(channel, MESSAGE_TEXTS["Email"])
            message_text = random.choice(msg_pool).replace("{name}", c["name"].split()[0])
        else:
            message_text = ""

        # ticket text
        ticket_text = random.choice(TICKET_TEXTS) if event_type in ["complaint","refund_request","support_chat"] else ""

        # opened / clicked / converted
        opened    = random.random() < 0.55 if event_type in ["campaign_received","campaign_opened"] else ""
        clicked   = random.random() < 0.35 if str(opened) == "True" else (random.random() < 0.15 if event_type == "offer_clicked" else "")
        converted = random.random() < 0.25 if str(clicked) == "True" else (True if event_type == "purchase" else "")

        # revenue
        if event_type == "purchase" or converted == True:
            revenue = round(prod[3] * random.uniform(0.8, 1.1), 2)
        else:
            revenue = 0.0

        rows_events.append({
            "event_id":       "EVT-" + str(uuid.uuid4())[:8].upper(),
            "customer_id":    c["customer_id"],
            "customer_name":  c["name"],
            "age":            c["age"],
            "gender":         c["gender"],
            "city":           c["city"],
            "state":          c["state"],
            "event_type":     event_type,
            "product_id":     prod[0],
            "product_name":   prod[1],
            "category":       prod[2],
            "campaign_name":  campaign,
            "message_text":   message_text,
            "ticket_text":    ticket_text,
            "channel":        channel,
            "emotion":        emotion,
            "sentiment":      sentiment,
            "risk_score":     c["risk_score"],
            "trust_score":    c["trust_score"],
            "happiness_score":c["happiness_score"],
            "opened":         opened,
            "clicked":        clicked,
            "converted":      converted,
            "revenue":        revenue,
            "timestamp":      make_timestamp(),
        })

# sort by timestamp
rows_events.sort(key=lambda x: x["timestamp"])

out_path1 = r"datasets\omnipulse_master_events.csv"
fields1 = ["event_id","customer_id","customer_name","age","gender","city","state",
           "event_type","product_id","product_name","category","campaign_name",
           "message_text","ticket_text","channel","emotion","sentiment",
           "risk_score","trust_score","happiness_score","opened","clicked","converted","revenue","timestamp"]

with open(out_path1, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields1)
    w.writeheader()
    w.writerows(rows_events)

print(f"Generated {len(rows_events)} rows -> {out_path1}")

# ── DATASET 2: ai_predictions.csv ───────────────────────────────

rows_preds = []
target_preds = 5000
cust_cycle = customers * (target_preds // len(customers) + 2)
random.shuffle(cust_cycle)

for i in range(target_preds):
    c = cust_cycle[i]

    churn   = c["risk_score"]
    trust   = c["trust_score"]
    happy   = c["happiness_score"]

    # CLV based on profile
    if c["profile_type"] == "healthy":
        clv = round(random.uniform(15000, 250000), 2)
    elif c["profile_type"] == "at_risk":
        clv = round(random.uniform(500, 15000), 2)
    else:
        clv = round(random.uniform(3000, 60000), 2)

    # persona
    if clv > 100000:
        persona = random.choice(["Premium Buyer","High Value Customer","Loyal Customer"])
    elif churn > 70:
        persona = random.choice(["Discount Hunter","Impulse Buyer"])
    else:
        persona = random.choice(PERSONAS)

    # emotion
    if happy > 70:
        emotion = random.choice(["Happy","Excited","Happy"])
    elif happy < 35:
        emotion = random.choice(["Frustrated","Neutral","Angry"])
    else:
        emotion = "Neutral"

    # NBA action logic
    if churn > 80:
        nba = random.choice(["Give Discount","Customer Success Call","Trigger Journey","WhatsApp Reminder"])
        offer = random.choice(["15 Percent Discount","20 Percent Discount","Exclusive Offer"])
    elif trust < 40:
        nba = random.choice(["Customer Success Call","Send Email","WhatsApp Reminder"])
        offer = random.choice(["10 Percent Discount","Bonus Loyalty Points","Free Delivery"])
    elif clv > 80000:
        nba = random.choice(["Offer Loyalty Points","Recommend Product","Send Email"])
        offer = random.choice(["Exclusive Offer","Bonus Loyalty Points","Free Delivery"])
    else:
        nba = random.choice(NBA_ACTIONS)
        offer = random.choice(OFFERS)

    # channel
    if churn > 80:
        channel = random.choice(["WhatsApp","SMS","Push Notification"])
    else:
        channel = random.choice(CHANNELS)

    # retention prediction
    if churn > 70:
        pred_retention = round(random.uniform(0.15, 0.45), 3)
    elif churn < 30:
        pred_retention = round(random.uniform(0.70, 0.98), 3)
    else:
        pred_retention = round(random.uniform(0.40, 0.75), 3)

    # revenue saved
    if churn > 70:
        rev_saved = round(clv * random.uniform(0.1, 0.4), 2)
    else:
        rev_saved = round(clv * random.uniform(0.02, 0.12), 2)

    # digital twin
    if churn > 75:
        dt_outcome = random.choice(["Customer Likely To Churn","Customer Likely To Churn","Retention Improved"])
    elif clv > 80000:
        dt_outcome = random.choice(["Revenue Growth Expected","High Engagement Predicted","Customer Likely To Stay"])
    else:
        dt_outcome = random.choice(DIGITAL_TWIN_OUTCOMES)

    confidence = random.randint(60, 99)

    rows_preds.append({
        "prediction_id":          "PRED-" + str(uuid.uuid4())[:8].upper(),
        "customer_id":            c["customer_id"],
        "churn_score":            churn,
        "trust_score":            trust,
        "happiness_score":        happy,
        "clv":                    clv,
        "persona":                persona,
        "emotion":                emotion,
        "nba_action":             nba,
        "offer":                  offer,
        "discount":               int(offer.split()[0]) if offer[0].isdigit() else 0,
        "recommended_channel":    channel,
        "predicted_retention":    pred_retention,
        "predicted_revenue_saved":rev_saved,
        "digital_twin_outcome":   dt_outcome,
        "confidence":             confidence,
        "timestamp":              make_timestamp(start_days_ago=30),
    })

out_path2 = r"datasets\ai_predictions.csv"
fields2 = ["prediction_id","customer_id","churn_score","trust_score","happiness_score",
           "clv","persona","emotion","nba_action","offer","discount","recommended_channel",
           "predicted_retention","predicted_revenue_saved","digital_twin_outcome","confidence","timestamp"]

with open(out_path2, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields2)
    w.writeheader()
    w.writerows(rows_preds)

print(f"Generated {len(rows_preds)} rows -> {out_path2}")
print("DONE")
