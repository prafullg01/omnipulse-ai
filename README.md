# 🚀 OmniPulse AI - Customer Intelligence Operating System

<div align="center">

**Real-Time Adaptive Customer Intelligence Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

</div>

---

## ✅ **FIXED - Authentication Now Working!**

The login/register pages have been **completely fixed**:
- ✨ Password hashing corrected
- ✨ Database properly seeded
- ✨ All authentication endpoints working
- ✨ JWT token generation & validation fixed

**You can now login and use all features!**

---

## 🎯 Quick Start

### **Backend Server**
```bash
cd backend
venv\Scripts\activate
python reset_db_force.py  # Reset database if needed
uvicorn app.main:app --reload
```
→ Backend runs on `http://localhost:8000`

### **Frontend Server**
```bash
cd frontend
npm install  # First time only
npm run dev
```
→ Frontend runs on `http://localhost:5173`

---

## 🔐 Login Credentials

### **Admin Dashboard**
```
Email: admin@omnipulse.ai
Password: admin123
```

### **Customer Portal**
```
Email: dhruv.bhat35@gmail.com
Password: password123
```

---

## 📊 Dataset Integration

### **Where to Place Your 3 Datasets:**

📁 **Location:** `backend/datasets/`

**Required Files:**
1. `customers.csv` - Customer demographics
2. `orders.csv` - Transaction history
3. `events.csv` - Behavior tracking

**To Load:**
```bash
cd backend
venv\Scripts\activate
python load_datasets.py
```

**📖 Full Guide:** See `DATASETS_GUIDE.md` for complete instructions

---

## 🎨 Key Features

### **🔐 Authentication System**
- ✅ Secure JWT-based authentication
- ✅ Role-based access control (Admin/Customer)
- ✅ Bcrypt password hashing
- ✅ Session management with Zustand

### **📊 Admin Dashboard**
- **Executive Summary** - Real-time KPIs and business metrics
- **Customer 360 View** - Complete customer intelligence profiles
- **Analytics Center** - Advanced data visualization and insights
- **Campaign Builder** - Create and manage marketing campaigns

### **🤖 AI-Powered Features**
- **Next Best Action (NBA)** - AI-recommended customer actions
- **Churn Prediction** - Identify at-risk customers
- **Emotion Analysis** - Sentiment tracking and mood detection
- **Digital Twin** - Simulate customer scenarios and outcomes
- **Journey Replay** - Visualize customer journey paths
- **Marketer Copilot** - AI-powered marketing assistant

### **⚖️ Trust & Governance**
- **Fairness Center** - Bias detection and mitigation
- **Trust Center** - Transparency and compliance monitoring
- **Observability** - System health and performance tracking

### **💰 Business Intelligence**
- **ROI Calculator** - Campaign and feature ROI analysis
- **Observatory** - Real-time metrics dashboard
- **Predictive Analytics** - CLV, churn, and retention forecasting

### **🛍️ Customer Portal**
- Product browsing and shopping cart
- Order tracking and history
- Support ticket system
- Personalized recommendations

---

## 🏗️ Architecture

### **Backend (FastAPI)**
```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # SQLAlchemy ORM models
│   │   └── models.py        # 14 database tables
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # Authentication (FIXED!)
│   │   ├── customers.py
│   │   ├── products.py
│   │   ├── campaigns.py
│   │   ├── analytics.py
│   │   ├── ai_router.py
│   │   └── support.py
│   ├── database/
│   │   ├── connection.py    # Database connection
│   │   └── seed.py          # Demo data seeder
│   ├── utils/
│   │   └── auth.py          # JWT & password hashing
│   └── websocket/
│       └── manager.py       # Real-time updates
├── datasets/                # Real datasets (9 comprehensive datasets)
│   ├── README.md
│   ├── omnipulse_master_events.csv    # 5,000+ customer events
│   ├── ai_predictions.csv             # AI-generated predictions
│   ├── archive.zip → Ecommerce.csv    # 25,000 behavior records
│   ├── archive (1).zip → flipkart_com-ecommerce_sample.csv  # 20,000 products
│   ├── archive (2).zip → Dataset-SA.csv  # Sentiment analysis
│   ├── archive (3).zip → Orders & Details  # Real Indian orders
│   └── archive (4).zip → Mall_Customers.csv  # Customer segmentation
├── comprehensive_loader.py  # Main dataset loader (uses all 9 datasets)
├── reset_db_force.py        # Database reset script
└── requirements.txt
```

### **Frontend (React + TypeScript)**
```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Login.tsx        # FIXED!
│   │   ├── Register.tsx     # FIXED!
│   │   └── admin/           # 15 admin pages
│   │       ├── Dashboard.tsx
│   │       ├── Customer360.tsx
│   │       ├── ChurnCenter.tsx
│   │       ├── NBACenter.tsx
│   │       ├── EmotionCenter.tsx
│   │       ├── DigitalTwin.tsx
│   │       ├── CampaignBuilder.tsx
│   │       └── ... (more)
│   ├── layouts/
│   │   └── AdminLayout.tsx
│   ├── services/
│   │   └── api.ts           # Axios HTTP client
│   └── store/
│       └── authStore.ts     # Zustand state management
└── vite.config.ts           # Vite configuration with proxy
```

---

## 📋 Database Schema (14 Tables)

1. **customers** - User accounts and profiles
2. **customer_profiles** - AI-generated intelligence scores
3. **products** - Product catalog
4. **orders** - Purchase transactions
5. **order_items** - Order line items
6. **events** - Customer behavior tracking
7. **support_tickets** - Customer support
8. **campaigns** - Marketing campaigns
9. **campaign_responses** - Campaign performance
10. **nba_decisions** - Next Best Action recommendations
11. **journeys** - Customer journey tracking
12. **messages** - Customer communications
13. **digital_twin_results** - Simulation results
14. **executive_summaries** - AI-generated insights

---

## 🔧 Technology Stack

### **Backend**
- **Framework:** FastAPI 0.100+
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** JWT (PyJWT) + Bcrypt
- **AI Integration:** Google Gemini AI
- **WebSocket:** FastAPI WebSocket support
- **Validation:** Pydantic models

### **Frontend**
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 5
- **Styling:** TailwindCSS 4
- **Animations:** Framer Motion
- **State Management:** Zustand
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Icons:** Lucide React

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `SETUP_GUIDE.md` | Complete setup and troubleshooting |
| `DATASETS_GUIDE.md` | How to load your 3 datasets |
| `backend/datasets/README.md` | Dataset format specifications |

---

## 🧪 Testing

### **Test Authentication**
```bash
cd backend
venv\Scripts\activate
python test_auth.py
```

This will test:
- ✅ Admin login
- ✅ Customer login
- ✅ User registration
- ✅ Protected endpoint access

### **API Documentation**
Once backend is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🆘 Troubleshooting

### **"Invalid credentials" Error**
```bash
cd backend
venv\Scripts\activate
python reset_db_force.py
```

### **Backend Won't Start**
- Check if port 8000 is available
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`

### **Frontend Won't Connect**
- Ensure backend is running on port 8000
- Check `vite.config.ts` proxy settings
- Clear browser cache and restart dev server

### **Dataset Loading Fails**
- Check file names exactly match: `customers.csv`, `orders.csv`, `events.csv`
- Verify CSV headers match expected format
- See `DATASETS_GUIDE.md` for detailed specs

---

## 🎯 What Makes OmniPulse AI Unique?

### **1. Adaptive Intelligence**
- Real-time customer scoring and segmentation
- Dynamic persona assignment
- Contextual recommendations

### **2. Predictive Analytics**
- Churn prediction with explainable AI
- CLV forecasting
- Next purchase prediction

### **3. Ethical AI**
- Bias detection and fairness monitoring
- Transparency in decision-making
- Privacy-preserving analytics

### **4. Omnichannel Orchestration**
- Unified customer view across touchpoints
- Journey-aware messaging
- Optimal channel selection

### **5. Marketer Empowerment**
- Natural language campaign creation
- A/B test automation
- ROI optimization

---

## 🚀 Deployment

### **Backend Deployment**
- Compatible with: Heroku, Railway, DigitalOcean, AWS
- Database: Upgrade to PostgreSQL for production
- Environment variables in `.env` file

### **Frontend Deployment**
- Compatible with: Vercel, Netlify, Cloudflare Pages
- Update API base URL in production
- Build command: `npm run build`

---

## 📄 License

This project is proprietary software developed for OmniPulse AI.

---

## 🙏 Acknowledgments

- Built with ❤️ using FastAPI, React, and modern web technologies
- Powered by Google Gemini AI
- Designed for Indian e-commerce market

---

## 📧 Support

For issues or questions:
1. Check `SETUP_GUIDE.md` for solutions
2. Review console logs for errors
3. Verify all services are running
4. Reset database if authentication fails

---

<div align="center">

**🎉 Your OmniPulse AI platform is ready to use!**

**Made with 💙 for modern customer intelligence**

</div>
