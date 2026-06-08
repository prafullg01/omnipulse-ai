# OmniPulse AI - Quick Start Guide

## 🚀 Your System is Ready!

The database is loaded with **46,282 real records** from 9 comprehensive datasets.

---

## 🔐 Login Credentials

### Admin Access
```
Email: admin@omnipulse.ai
Password: admin123
```

### Test Customer Accounts
```
Email: customer1803@omnipulse.ai
Password: password123

Email: mall1@omnipulse.ai
Password: password123
```

*Note: All customer accounts use password: `password123`*

---

## 🏃 Start the Application

### Terminal 1: Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend will run at: **http://localhost:8000**

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## 📊 What's in the Database?

| Data Type | Count | Description |
|-----------|-------|-------------|
| **Customers** | 5,698 | Real Indian customers from multiple sources |
| **Products** | 3,899 | Flipkart product catalog |
| **Orders** | 2,536 | Real order transactions |
| **Events** | 28,815 | Customer behavior events |
| **Profiles** | 5,697 | AI-scored customer profiles |

---

## 🎯 First Steps After Login

1. **Dashboard Overview**
   - View customer metrics
   - See revenue trends
   - Check active campaigns

2. **Customer 360° View**
   - Search for a customer
   - View their complete profile
   - See purchase history
   - Check behavior events

3. **AI Recommendations**
   - View Next Best Actions
   - See churn predictions
   - Check sentiment analysis

4. **Journey Orchestration**
   - View customer journeys
   - See journey stages
   - Track completion rates

---

## 🔍 Verify Installation

Run this to check your database:
```bash
cd backend
venv\Scripts\activate
python check_db.py
```

Expected output:
- Database size: ~15 MB
- Customers: 5,000+
- Products: 3,000+
- Orders: 2,000+
- Events: 28,000+

---

## 📚 Documentation

- **MIGRATION_COMPLETE.md** - Migration summary and statistics
- **SAMPLE_DATASETS_AUDIT_REPORT.md** - Complete audit trail
- **DATASETS_GUIDE.md** - Dataset usage guide
- **backend/datasets/README.md** - Dataset details

---

## ❓ Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <process_id> /F
```

### Frontend won't start
```bash
# Reinstall dependencies
npm install

# Clear cache
npm cache clean --force
```

### Database issues
```bash
# Check database
python check_db.py

# Reload database (if needed)
python comprehensive_loader.py
```

---

## 🎉 You're All Set!

Your OmniPulse AI platform is ready with:
- ✅ 46,000+ real records
- ✅ Production-quality data
- ✅ AI-powered insights
- ✅ Complete customer profiles

**Happy exploring!** 🚀
