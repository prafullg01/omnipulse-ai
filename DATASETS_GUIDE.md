# 📊 Dataset Loading Guide - OmniPulse AI

## 📍 Where to Place Your 3 Datasets

### **Location:**
```
c:\Users\Prafull\Desktop\OMNIPULSE AI\backend\datasets\
```

The `datasets` folder has been created for you. Simply drag and drop your 3 dataset files here.

---

## 📋 Required Dataset Files

### 1️⃣ **customers.csv** (or customers.xlsx)

**Purpose:** Customer demographic and profile information

**Required Columns:**
| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| `first_name` | Text | Customer's first name | Priya |
| `last_name` | Text | Customer's last name | Sharma |
| `email` | Text | Email address (unique) | priya@gmail.com |
| `phone` | Text | Phone number (optional) | 9876543210 |
| `city` | Text | City of residence | Mumbai |
| `age` | Number | Customer age | 28 |
| `gender` | Text | Gender (male/female/other) | female |

**Sample Data:**
```csv
first_name,last_name,email,phone,city,age,gender
Priya,Sharma,priya.sharma@gmail.com,9876543210,Mumbai,28,female
Rahul,Kumar,rahul.kumar@gmail.com,9876543211,Delhi,34,male
Anjali,Patel,anjali.patel@gmail.com,9876543212,Bangalore,25,female
```

---

### 2️⃣ **orders.csv** (or orders.xlsx)

**Purpose:** Transaction and purchase history

**Required Columns:**
| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| `customer_email` | Text | Links to customer | priya.sharma@gmail.com |
| `product_name` | Text | Name of product purchased | iPhone 15 Pro |
| `amount` | Number | Total order amount | 134900 |
| `quantity` | Number | Number of items | 1 |
| `order_date` | Date | Purchase date | 2026-05-15 |
| `status` | Text | Order status | delivered |
| `category` | Text | Product category (optional) | Electronics |
| `payment_method` | Text | Payment type (optional) | card |

**Sample Data:**
```csv
customer_email,product_name,amount,quantity,order_date,status,category,payment_method
priya.sharma@gmail.com,iPhone 15 Pro,134900,1,2026-05-15,delivered,Electronics,card
rahul.kumar@gmail.com,Nike Air Max,12995,2,2026-05-20,shipped,Fashion,upi
anjali.patel@gmail.com,MacBook Air M3,114900,1,2026-05-18,delivered,Electronics,card
```

---

### 3️⃣ **events.csv** (or events.xlsx)

**Purpose:** Customer behavior and interaction tracking

**Required Columns:**
| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| `customer_email` | Text | Links to customer | priya.sharma@gmail.com |
| `event_type` | Text | Type of event | product_view |
| `event_value` | Text | Event details (optional) | iPhone 15 Pro |
| `timestamp` | DateTime | When event occurred | 2026-05-10 14:30:00 |

**Valid Event Types:**
- `product_view` - Customer viewed a product
- `cart_add` - Added item to cart
- `cart_remove` - Removed item from cart
- `wishlist_add` - Added to wishlist
- `search` - Searched for products
- `purchase` - Completed purchase
- `review_submit` - Submitted review
- `ticket_created` - Created support ticket

**Sample Data:**
```csv
customer_email,event_type,event_value,timestamp
priya.sharma@gmail.com,product_view,iPhone 15 Pro,2026-05-10 14:30:00
priya.sharma@gmail.com,cart_add,iPhone 15 Pro,2026-05-10 14:35:00
priya.sharma@gmail.com,purchase,iPhone 15 Pro,2026-05-15 10:20:00
rahul.kumar@gmail.com,search,running shoes,2026-05-18 10:15:00
```

---

## 🚀 How to Load Your Datasets

### **Step 1: Place Files**
Drag your 3 files into:
```
backend\datasets\
```

### **Step 2: Open Terminal**
```bash
cd backend
```

### **Step 3: Activate Virtual Environment**
```bash
venv\Scripts\activate
```

### **Step 4: Run Loader Script**
```bash
python load_datasets.py
```

### **Expected Output:**
```
============================================================
OmniPulse AI - Dataset Loader
============================================================

Looking for dataset files in: C:\...\backend\datasets

✓ Loaded customers.csv: 50 rows, 7 columns
  Columns: first_name, last_name, email, phone, city, age, gender

✓ Loaded orders.csv: 200 rows, 8 columns
  Columns: customer_email, product_name, amount, quantity, order_date, status, category, payment_method

✓ Loaded events.csv: 1500 rows, 4 columns
  Columns: customer_email, event_type, event_value, timestamp

📊 Loading customers...
✓ Loaded 50 customers

📊 Loading orders...
✓ Loaded 200 orders

📊 Loading events...
✓ Loaded 1500 events

============================================================
✅ Dataset loading complete!
============================================================
```

---

## 🎯 File Format Flexibility

### **Supported Formats:**
- ✅ CSV files (`.csv`)
- ✅ Excel files (`.xlsx`, `.xls`)

### **Column Name Flexibility:**
The loader accepts alternative column names:

**For Customers:**
- `name` → automatically splits into first_name and last_name
- `phone_number` → works as `phone`

**For Orders:**
- `email` → works as `customer_email`
- `product` → works as `product_name`
- `total_amount` or `price` → works as `amount`
- `date` → works as `order_date`

**For Events:**
- `email` → works as `customer_email`
- `event` → works as `event_type`
- `value` → works as `event_value`
- `time` or `datetime` → works as `timestamp`

---

## 📝 Data Requirements

### **Important Notes:**

1. **Customer emails must be unique** in customers.csv
2. **Orders and events link by email** - customer must exist first
3. **Date formats:**
   - Orders: `YYYY-MM-DD` (e.g., 2026-05-15)
   - Events: `YYYY-MM-DD HH:MM:SS` (e.g., 2026-05-10 14:30:00)

4. **Missing data handling:**
   - Optional fields can be empty
   - System uses smart defaults for missing data
   - Invalid rows are skipped with warnings

---

## 🔄 Real Datasets Included

The system comes with 9 comprehensive real datasets already loaded:

### Core Datasets
- `omnipulse_master_events.csv` - 5,000+ customer behavior events
- `ai_predictions.csv` - AI-generated predictions and scores

### Extracted from ZIP Archives
- `Ecommerce.csv` - 25,000 ecommerce behavior records
- `flipkart_com-ecommerce_sample.csv` - 20,000+ product catalog
- `Dataset-SA.csv` - Sentiment analysis with reviews
- `List of Orders.csv` + `Order Details.csv` - Real Indian orders
- `Sales target.csv` - Sales targets and metrics
- `Mall_Customers.csv` - Customer segmentation data

**Total:** 5,000+ customers, 500+ orders, 5,000+ events, 3,000+ products

Use `comprehensive_loader.py` to load all datasets automatically!

---

## 🆘 Troubleshooting

### **Error: "File not found"**
✅ Check file is in `backend/datasets/` folder
✅ Check file name matches exactly: `customers.csv`, `orders.csv`, `events.csv`

### **Error: "Column not found"**
✅ Open CSV in Excel/text editor
✅ Verify first row contains column headers
✅ Check column names match expected format

### **Error: "Customer not found" for orders/events**
✅ Ensure `customers.csv` loads first
✅ Verify email addresses match exactly between files
✅ Check for typos in email addresses

### **Warning: "Row skipped"**
- This is normal for invalid data
- Check console output for specific row numbers
- Fix data in those rows and reload

---

## 💡 Pro Tips

1. **Test with sample data first** - Load the provided samples to test the process
2. **Clean your data** - Remove duplicates, fix formatting before loading
3. **Backup your data** - Keep original files safe before loading
4. **Check email format** - Ensure all emails are valid format
5. **Use Excel** - Easier to clean and format data than text editor

---

## 🎉 After Loading

Once your datasets are loaded:

1. **Login to admin dashboard**
   - Email: `admin@omnipulse.ai`
   - Password: `admin123`

2. **View your data in:**
   - 📊 Dashboard - Overall metrics
   - 👥 Customer 360 - Individual profiles
   - 📈 Analytics - Trends and insights
   - 🤖 AI Centers - Predictions and recommendations

3. **Your custom data will power:**
   - Churn prediction models
   - Next Best Action recommendations
   - Customer segmentation
   - Personalized campaigns
   - ROI analysis

---

## ✨ What Happens During Loading

1. **Customers are created** with default password: `password123`
2. **Products are auto-created** from order data
3. **Customer profiles generated** with AI scoring:
   - Trust Score
   - Happiness Score
   - Churn Probability
   - Lifetime Value (CLV)
   - Engagement Score
   - Persona Assignment

4. **Relationships linked**:
   - Orders → Customers
   - Events → Customers
   - Order Items → Products

---

## 📞 Need Help?

1. Check `backend/datasets/README.md` for detailed specs
2. Look at sample files for format examples
3. Run with `python load_datasets.py` to see detailed errors
4. Ensure backend server is NOT running during load

**Your data will be ready to power the OmniPulse AI platform!** 🚀
