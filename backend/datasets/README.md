# 📁 Dataset Files Location

## 🎯 Real Datasets Already Loaded

This system uses **9 comprehensive real datasets** with over 25,000 records. All datasets are already in place and can be loaded automatically.

---

## 📋 Current Dataset Files

### Core Generated Datasets

#### 1️⃣ **omnipulse_master_events.csv**
Customer behavior events with full context

**Contains:**
- 5,000+ customer events
- Event types: product_view, search, cart_add, purchase, etc.
- Customer demographics (age, gender, city)
- Product information and categories
- Campaign associations
- Channel attribution
- Timestamps and metadata

---

#### 2️⃣ **ai_predictions.csv**
AI-generated customer predictions and scores

**Contains:**
- Churn scores (0-100)
- Trust scores (0-100)
- Happiness scores (0-100)
- CLV (Customer Lifetime Value)
- Predicted personas
- Emotional states
- Next Best Action recommendations
- Recommended offers and channels

---

### Extracted from ZIP Archives

#### 3️⃣ **Ecommerce.csv** (from archive.zip)
Main ecommerce behavior dataset - 25,000 records

**Contains:**
- Customer IDs and locations
- Session behavior
- Purchase patterns
- Cart abandonment data
- Revenue per session
- Channel attribution

---

#### 4️⃣ **flipkart_com-ecommerce_sample.csv** (from archive (1).zip)
Product catalog - 20,000+ products

**Contains:**
- Product names and descriptions
- Categories and subcategories
- Pricing information
- Discounts
- Brand information
- Product URLs and images

---

#### 5️⃣ **Dataset-SA.csv** (from archive (2).zip)
Sentiment analysis dataset

**Contains:**
- Customer reviews
- Sentiment labels (positive/negative/neutral)
- Review text and summaries
- Product feedback

---

#### 6️⃣ **List of Orders.csv** + **Order Details.csv** (from archive (3).zip)
Real Indian customer orders - 500+ orders

**Contains:**
- Order IDs and dates
- Customer names (real Indian names)
- Cities and states across India
- Product categories
- Order amounts and profits
- Quantities and discounts

---

#### 7️⃣ **Sales target.csv** (from archive (3).zip)
Sales targets and metrics

---

#### 8️⃣ **Mall_Customers.csv** (from archive (4).zip)
Customer segmentation data - 200 profiles

**Contains:**
- Customer demographics
- Annual income
- Spending scores
- Age and gender
- Customer segmentation clusters

---

## 🚀 How to Load All Datasets

### Method 1: Automatic Comprehensive Loader (Recommended)

1. **Open terminal** in the backend folder
2. **Activate virtual environment:**
   ```bash
   venv\Scripts\activate
   ```
3. **Run the comprehensive loader:**
   ```bash
   python comprehensive_loader.py
   ```

This will:
- ✅ Extract all ZIP archives automatically
- ✅ Load all 9 datasets in correct order
- ✅ Create 5,000+ customers
- ✅ Create 500+ orders with order items
- ✅ Create 5,000+ behavioral events
- ✅ Create 3,000+ products
- ✅ Generate customer profiles with AI scores
- ✅ Create sentiment-based support tickets
- ✅ Create campaigns and messages
- ✅ Show detailed progress

---

### Method 2: Alternative Loader

```bash
python load_all_datasets.py
```

---

## 📊 Data Statistics

After loading, your database will contain:

| Entity | Count | Source |
|--------|-------|--------|
| **Customers** | 5,000+ | Multiple datasets |
| **Products** | 3,000+ | Flipkart catalog |
| **Orders** | 500+ | List of Orders |
| **Order Items** | 1,000+ | Order Details |
| **Events** | 5,000+ | Master events |
| **Support Tickets** | 100+ | Sentiment data |
| **Campaigns** | 15+ | Generated |
| **Messages** | 1,000+ | Generated |
| **Customer Profiles** | 5,000+ | AI-scored |

---

## 💡 Dataset Features

### Geographic Coverage
- **Pan-India:** Customers from 25+ states
- **Major Cities:** Mumbai, Delhi, Bangalore, Chennai, Kolkata, Pune, Hyderabad, etc.
- **Real Names:** Authentic Indian customer names

### Time Series Data
- **Order Dates:** Jan 2018 - Dec 2019
- **Event Timestamps:** Chronological sequences
- **Campaign Periods:** Seasonal sales events

### Rich Attributes
- **Demographics:** Age, gender, location
- **Behavior:** Views, searches, carts, purchases
- **Sentiment:** Positive/negative reviews
- **Predictions:** Churn, CLV, persona, emotion
- **Segmentation:** High-value, at-risk, loyal, new

---

## 🆘 Troubleshooting

**Error: "ZIP file not found"**
- Ensure all archive.zip files are in the datasets folder
- Check file names: archive.zip, archive (1).zip, archive (2).zip, etc.

**Error: "CSV not found after extraction"**
- Run `comprehensive_loader.py` - it extracts automatically
- Check extracted_archive folders were created

**Error: "Database locked"**
- Close any database viewers (DB Browser)
- Stop any running backend servers
- Delete omnipulse.db and run loader again

**Loader is slow**
- Normal! Processing 25,000+ records takes time
- Password hashing for 5,000 customers is intentionally slow (security)
- Wait for completion (5-10 minutes)

---

## 🔐 Default Credentials

After loading:

**Admin Account:**
- Email: `admin@omnipulse.ai`
- Password: `admin123`

**All Customer Accounts:**
- Password: `password123`

**Customer Email Formats:**
- `customer{ID}@omnipulse.ai` (e.g., customer1803@omnipulse.ai)
- `mall{ID}@omnipulse.ai` (e.g., mall1@omnipulse.ai)

---

## 📈 Next Steps

After loading datasets:

1. **Start the backend:**
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Login and explore:**
   - Navigate to http://localhost:5173
   - Login with admin credentials
   - View dashboards with real data
   - Test all AI features

---

Need help? Check the comprehensive loader output for detailed progress and error messages!
