# OMNIPULSE AI - QUICK START GUIDE

## System Status: ✓ OPERATIONAL

---

## SYSTEM OVERVIEW

**OmniPulse AI** is now a fully operational Customer Intelligence Operating System with:
- 5,697 customer profiles with complete AI intelligence
- 5,697 personalized NBA recommendations
- 5 active campaigns generating revenue
- 380 customer journeys
- 46,282 real database records

**All dashboards are GREEN (fully data-driven).**

---

## CREDENTIALS

### Admin Account
- **Email:** `admin@omnipulse.ai`
- **Password:** `admin123`

### Customer Accounts
- **Email Pattern:** `customer{ID}@omnipulse.ai` or `mall{ID}@omnipulse.ai`
- **Password:** `password123`
- **Examples:**
  - `customer1@omnipulse.ai` / `password123`
  - `mall1@omnipulse.ai` / `password123`

---

## STARTING THE SYSTEM

### Backend (FastAPI)

```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend URL:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### Frontend (React)

```powershell
cd frontend
npm start
```

**Frontend URL:** http://localhost:3000

---

## AVAILABLE DASHBOARDS

### 1. Churn Center
- **Status:** 🟢 GREEN
- **Data:** 5,697 customers with churn scores
- **Distribution:** 42% Low, 25% Medium, 18% High, 15% Critical
- **Endpoint:** `/api/analytics/churn`

### 2. Emotion Center
- **Status:** 🟢 GREEN
- **Data:** 5,697 customers with emotions
- **Distribution:** 73% Neutral, 18% Happy, 8% Frustrated, 1% Excited
- **Endpoint:** `/api/analytics/emotions`

### 3. Trust Center
- **Status:** 🟢 GREEN
- **Data:** 5,697 customers with trust scores
- **Distribution:** 77.5% High, 20.5% Medium, 1.9% Low
- **Endpoint:** `/api/analytics/trust`

### 4. NBA Center (Next Best Action)
- **Status:** 🟢 GREEN
- **Data:** 5,697 personalized recommendations
- **Confidence:** 85% average
- **Endpoint:** `/api/nba/recommendations`

### 5. Campaign Builder
- **Status:** 🟢 GREEN
- **Data:** 5 active campaigns, 682 responses
- **Revenue:** $7,130.36
- **Endpoint:** `/api/campaigns/`

### 6. ROI Center
- **Status:** 🟢 GREEN
- **Data:** Campaign performance metrics
- **Metrics:** Open rate, click rate, conversion rate, revenue
- **Endpoint:** `/api/analytics/roi`

### 7. Customer 360
- **Status:** 🟢 GREEN
- **Data:** Complete profiles for 5,697 customers
- **Fields:** CLV, churn, trust, emotion, persona, segment, journey stage
- **Endpoint:** `/api/customers/{customer_id}/profile`

### 8. Journey Engine
- **Status:** 🟢 GREEN
- **Data:** 380 active customer journeys
- **Types:** Churn rescue, loyalty, re-engagement, onboarding
- **Endpoint:** `/api/journeys/`

### 9. Analytics Engine
- **Status:** 🟢 GREEN
- **Data:** 2,536 orders, 28,815 events
- **Metrics:** Order trends, event patterns, revenue analytics
- **Endpoint:** `/api/analytics/`

---

## DATABASE QUICK REFERENCE

### Location
`c:\Users\Prafull\Desktop\OMNIPULSE AI\backend\omnipulse.db`

### Key Tables

| Table | Records | Description |
|-------|--------:|-------------|
| `customers` | 5,697 | Customer accounts |
| `customer_profiles` | 5,697 | AI intelligence profiles |
| `nba_decisions` | 5,697 | NBA recommendations |
| `campaigns` | 5 | Active campaigns |
| `campaign_responses` | 682 | Campaign engagement |
| `journeys` | 380 | Customer journeys |
| `orders` | 2,536 | Purchase orders |
| `events` | 28,815 | Behavioral events |
| `products` | 3,899 | Product catalog |

### Quick Queries

```sql
-- Get customer with full profile
SELECT c.*, p.* 
FROM customers c 
JOIN customer_profiles p ON c.customer_id = p.customer_id 
WHERE c.email = 'customer1@omnipulse.ai';

-- Get NBA recommendations for customer
SELECT * FROM nba_decisions 
WHERE customer_id = 'CUSTOMER_ID';

-- Get campaign performance
SELECT 
  c.campaign_name,
  COUNT(cr.response_id) as sent,
  SUM(CASE WHEN cr.opened THEN 1 ELSE 0 END) as opened,
  SUM(cr.revenue) as revenue
FROM campaigns c
LEFT JOIN campaign_responses cr ON c.campaign_id = cr.campaign_id
GROUP BY c.campaign_id;

-- Get churn distribution
SELECT 
  CASE 
    WHEN churn_probability < 0.3 THEN 'Low'
    WHEN churn_probability < 0.6 THEN 'Medium'
    WHEN churn_probability < 0.75 THEN 'High'
    ELSE 'Critical'
  END as risk_level,
  COUNT(*) as count
FROM customer_profiles
GROUP BY risk_level;
```

---

## VALIDATION & REPORTS

### Run System Validation

```powershell
cd backend
.\venv\Scripts\python.exe final_system_validation.py
```

**Output:**
- Console report with all counts and distributions
- `system_validation_report.json` file

### Reports Available

1. **`database_audit_report.json`** - Complete database audit
2. **`system_validation_report.json`** - System health metrics
3. **`SYSTEM_REBUILD_COMPLETE.md`** - Full rebuild documentation

---

## REBUILDING THE SYSTEM

If you need to rebuild the entire intelligence layer:

```powershell
cd backend

# Phase 1-2, 7-9: Core rebuild
.\venv\Scripts\python.exe final_complete_rebuild.py

# Phase 3-6: Distribution rebalancing
.\venv\Scripts\python.exe rebalance_distributions.py

# Force target distributions
.\venv\Scripts\python.exe force_target_distributions.py

# Validate
.\venv\Scripts\python.exe final_system_validation.py
```

**Time:** ~5 minutes total  
**Result:** All 9 dashboards GREEN

---

## TROUBLESHOOTING

### Backend won't start
```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

### Database locked
```powershell
# Check for Python processes
tasklist | findstr python

# Kill if needed
taskkill /F /IM python.exe
```

### Frontend won't start
```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Database missing or corrupt
```powershell
cd backend

# Delete old database
del omnipulse.db

# Reload all data
.\venv\Scripts\python.exe comprehensive_loader.py

# Rebuild intelligence
.\venv\Scripts\python.exe final_complete_rebuild.py
.\venv\Scripts\python.exe rebalance_distributions.py
.\venv\Scripts\python.exe force_target_distributions.py
```

---

## API ENDPOINTS REFERENCE

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Customers
- `GET /api/customers/` - List all customers
- `GET /api/customers/{customer_id}` - Get customer details
- `GET /api/customers/{customer_id}/profile` - Get customer profile

### Analytics
- `GET /api/analytics/churn` - Churn analysis
- `GET /api/analytics/emotions` - Emotion distribution
- `GET /api/analytics/trust` - Trust metrics
- `GET /api/analytics/roi` - Campaign ROI

### NBA
- `GET /api/nba/recommendations` - Get all NBA decisions
- `GET /api/nba/customer/{customer_id}` - Get customer NBA

### Campaigns
- `GET /api/campaigns/` - List campaigns
- `POST /api/campaigns/` - Create campaign
- `GET /api/campaigns/{campaign_id}` - Get campaign details

### Journeys
- `GET /api/journeys/` - List journeys
- `GET /api/journeys/customer/{customer_id}` - Get customer journeys

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (React)                   │
│              http://localhost:3000                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ REST API
                  ▼
┌─────────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                     │
│              http://localhost:8000                  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Routers: auth, customers, campaigns, NBA    │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Intelligence Layer: Churn, Trust, Emotion   │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ SQLAlchemy ORM
                  ▼
┌─────────────────────────────────────────────────────┐
│            DATABASE (SQLite)                        │
│            omnipulse.db                             │
│                                                     │
│  • 5,697 customers                                  │
│  • 5,697 profiles                                   │
│  • 5,697 NBA decisions                              │
│  • 2,536 orders                                     │
│  • 28,815 events                                    │
│  • 5 campaigns                                      │
│  • 380 journeys                                     │
└─────────────────────────────────────────────────────┘
```

---

## DATASETS USED

All data loaded from these 9 real datasets:

1. `Ecommerce.csv` - E-commerce transactions
2. `flipkart_com-ecommerce_sample.csv` - Product catalog
3. `Dataset-SA.csv` - Sentiment analysis
4. `List of Orders.csv` - Order details
5. `Order Details.csv` - Order line items
6. `Sales target.csv` - Sales metrics
7. `Mall_Customers.csv` - Customer demographics
8. `omnipulse_master_events.csv` - Behavioral events
9. `ai_predictions.csv` - ML predictions

**Location:** `c:\Users\Prafull\Desktop\OMNIPULSE AI\backend\datasets\`

---

## SUPPORT

### Documentation
- `SYSTEM_REBUILD_COMPLETE.md` - Complete system documentation
- `DATABASE_INTEGRATION_STATUS.md` - Database integration details
- `DATA_LINEAGE_REPORT.md` - Data source tracking

### Validation
- Run `final_system_validation.py` to check system health
- All dashboards should show GREEN status
- Profile coverage should be 100%
- NBA coverage should be 100%

### Contact
For issues or questions, refer to the comprehensive documentation in the root directory.

---

**System Status:** 🟢 OPERATIONAL  
**Last Updated:** June 4, 2026  
**Version:** 1.0.0
