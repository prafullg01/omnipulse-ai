# 🚀 OmniPulse AI - Complete Setup Guide

## ✅ Authentication Issue - FIXED!

The login and registration issues have been **resolved**:
- ✨ Password hashing fixed
- ✨ Database properly seeded with demo data
- ✨ Error messages improved for debugging
- ✨ All auth endpoints working correctly

---

## 📋 Quick Start

### 1️⃣ **Backend Setup**

```bash
# Navigate to backend folder
cd backend

# Activate virtual environment
venv\Scripts\activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Reset and seed database (if you encounter auth issues)
python reset_db_force.py

# Start the backend server
uvicorn app.main:app --reload
```

**Backend will run on:** `http://localhost:8000`

---

### 2️⃣ **Frontend Setup**

```bash
# Navigate to frontend folder (open new terminal)
cd frontend

# Install dependencies (if needed)
npm install

# Start the development server
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

---

## 🔐 Login Credentials

### **Admin Account**
- **Email:** `admin@omnipulse.ai`
- **Password:** `admin123`
- **Access:** Full admin dashboard with all features

### **Customer Account** (Any of these)
- **Email:** `dhruv.bhat35@gmail.com`
- **Password:** `password123`

OR Register a new account at `/register`

---

## 📁 Where to Place Your 3 Datasets

### **Location:**
```
backend/datasets/
```

### **Required Files:**

1. **customers.csv** (or .xlsx)
   - Customer demographic data
   - Columns: first_name, last_name, email, phone, city, age, gender

2. **orders.csv** (or .xlsx)
   - Order transaction history
   - Columns: customer_email, product_name, amount, quantity, order_date, status

3. **events.csv** (or .xlsx)
   - Customer behavior events
   - Columns: customer_email, event_type, event_value, timestamp

### **To Load Your Datasets:**

```bash
cd backend
venv\Scripts\activate
python load_datasets.py
```

**Sample datasets** are already provided in `backend/datasets/` folder for reference!

---

## 🎯 All Features Are Now Working

### **✅ Authentication**
- ✨ Registration with email/password
- ✨ Login with JWT tokens
- ✨ Role-based access (admin/customer)
- ✨ Password hashing with bcrypt
- ✨ Secure session management

### **✅ Admin Dashboard** (`/admin`)
- 📊 Executive Summary
- 👥 Customer 360 View
- 📈 Analytics & Insights
- 🤖 AI-Powered Features:
  - Next Best Action (NBA) Center
  - Churn Prediction Center
  - Emotion Analysis Center
  - Digital Twin Simulator
  - Journey Replay
  - Marketer Copilot
- 🎯 Campaign Builder
- 🔍 Observatory (Monitoring)
- ⚖️ Fairness & Trust Center
- 💰 ROI Calculator

### **✅ Customer Portal** (`/shop`)
- 🛍️ Product browsing
- 🛒 Shopping cart
- 💳 Checkout process
- 📦 Order tracking
- 💬 Support tickets

---

## 🔧 Troubleshooting

### **Issue: "Invalid credentials" error**

**Solution:**
```bash
cd backend
venv\Scripts\activate
python reset_db_force.py
```

This will:
- Drop all existing tables
- Recreate database schema
- Seed with fresh demo data
- Fix password hashing issues

### **Issue: Backend not starting**

Check if port 8000 is available:
```bash
netstat -ano | findstr :8000
```

If port is busy, kill the process or change port in command:
```bash
uvicorn app.main:app --reload --port 8001
```

### **Issue: Frontend not connecting to backend**

1. Ensure backend is running on `http://localhost:8000`
2. Check `frontend/vite.config.ts` proxy configuration
3. Restart frontend dev server

### **Issue: Dataset loading errors**

1. Check file names match exactly: `customers.csv`, `orders.csv`, `events.csv`
2. Ensure CSV has proper headers (see `backend/datasets/README.md`)
3. Check for missing required columns
4. Verify email addresses match between files

---

## 🎨 Key Features to Demo

1. **Login as Admin** → `admin@omnipulse.ai` / `admin123`
2. **Executive Summary** → Real-time KPIs and insights
3. **Customer 360** → Detailed customer intelligence profiles
4. **NBA Center** → AI-recommended next best actions
5. **Churn Center** → Predictive churn analysis
6. **Campaign Builder** → Create targeted marketing campaigns
7. **Digital Twin** → Simulate customer scenarios
8. **Marketer Copilot** → AI-powered marketing assistant

---

## 📚 API Documentation

Once backend is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🔄 Database Management Scripts

### **Reset Database** (Drops everything and reseeds)
```bash
python reset_db_force.py
```

### **Seed Only** (If DB exists but empty)
```bash
python -m app.database.seed
```

### **Load Custom Datasets**
```bash
python load_datasets.py
```

---

## 📦 Tech Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite Database
- JWT Authentication
- Bcrypt Password Hashing
- Google Gemini AI Integration

**Frontend:**
- React + TypeScript
- Vite Build Tool
- TailwindCSS
- Framer Motion
- Zustand State Management
- React Router
- Axios HTTP Client

---

## 🆘 Need Help?

1. Check console logs for detailed error messages
2. Verify all dependencies are installed
3. Ensure Python virtual environment is activated
4. Check that both servers are running
5. Try resetting the database

---

## ✨ What's Fixed

- ✅ Password hashing now uses proper bcrypt
- ✅ Login validates credentials correctly
- ✅ Registration creates proper user accounts
- ✅ JWT tokens generated and validated
- ✅ Database seed script creates demo data
- ✅ Customer profiles initialized correctly
- ✅ API endpoints return proper error messages
- ✅ Frontend handles auth state properly

**Your OmniPulse AI platform is now fully operational!** 🎉
