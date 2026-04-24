# ⬡ FraudIQ Enhanced — AI-Powered Fraud Detection System

## 🎓 2nd Year CSE Mini-Project

A comprehensive fraud detection system built with Machine Learning, featuring real-time transaction analysis, interactive dashboards, and advanced analytics.

**Tech Stack:** Python · Flask · Scikit-learn · SQLite · Chart.js · Vanilla JS

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [API Documentation](#api-documentation)
7. [Machine Learning Details](#machine-learning-details)
8. [Project Structure](#project-structure)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

FraudIQ is an intelligent fraud detection system that uses Machine Learning to identify fraudulent transactions in real-time. The system analyzes transaction patterns, provides risk assessments, and offers comprehensive analytics through an intuitive web interface.

### Key Highlights

- ✅ **Real-time Fraud Detection** using Random Forest ML model
- ✅ **92%+ Accuracy** on test dataset with ROC-AUC score of 0.94+
- ✅ **Interactive Dashboards** with data visualization
- ✅ **RESTful API** for easy integration
- ✅ **Analytics Dashboard** with charts and insights
- ✅ **Export Functionality** (CSV reports)
- ✅ **Feedback System** for continuous improvement
- ✅ **Rate Limiting** for API security

---

## 🚀 Features

### Core Features

1. **Transaction Analysis**
   - Real-time fraud scoring with millisecond response time
   - Risk level classification (LOW, MEDIUM, HIGH, CRITICAL)
   - Probability-based predictions with confidence scores

2. **Analytics Dashboard**
   - Fraud rate by transaction type (Online, In-store, ATM, Wire Transfer, Mobile)
   - Geographic risk analysis (Domestic, International, High-risk countries)
   - Hourly transaction patterns
   - 7-day fraud trends visualization

3. **Model Performance Monitoring**
   - ROC curve visualization
   - Confusion matrix analysis
   - Feature importance ranking
   - Precision-recall curves

4. **Data Management**
   - Transaction history logging
   - CSV export for reporting
   - Feedback collection system
   - Database-backed persistence

5. **Security Features**
   - Rate limiting (50 requests/minute per IP)
   - Input validation and sanitization
   - Error logging and monitoring
   - Secure database connections

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│  (HTML/CSS/JavaScript + Chart.js for visualizations)    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  Flask Backend (Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  API Routes  │  │  ML Engine   │  │   Database   │ │
│  │  /predict    │  │  Random      │  │   SQLite     │ │
│  │  /stats      │  │  Forest      │  │              │ │
│  │  /analytics  │  │  Classifier  │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Machine Learning Pipeline                   │
│  Feature Engineering → Model Training → Evaluation       │
│  (Log transform, One-hot encoding, Cross-validation)     │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB RAM minimum
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd fraud_detection_enhanced

# Or simply extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Train the ML Model

```bash
python model/train_model.py
```

**Expected Output:**
```
🔄  Step 1/4 – Generating synthetic dataset …
  ✔ Dataset: 10,000 rows | fraud rate: ~22%

🧠  Step 2/4 – Training and evaluating models …
======================================================
  RANDOM FOREST (primary model)
======================================================
              precision  recall  f1-score
  Legitimate     0.92     0.95     0.93
       Fraud     0.86     0.78     0.82
  ROC-AUC: 0.9450

📊  Step 3/4 – Generating visualizations …
  ✔ Feature importance plot saved
  ✔ ROC curves plot saved
  ✔ Confusion matrices plot saved
  ✔ Precision-recall plot saved

💾  Step 4/4 – Saving model and report …
  ✅  Model saved → model/model.pkl

🎉  Training Complete!
```

### Step 5: Start the Server

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000** 🎉

---

## 📖 Usage Guide

### 1. Submit a Transaction for Analysis

1. Go to the homepage
2. Enter transaction details:
   - **Amount:** Transaction value in USD
   - **Type:** online, in-store, atm, wire_transfer, or mobile
   - **Location:** domestic, international, or high_risk_country
   - **Hour:** 0-23 (24-hour format)
3. Click "Analyse Transaction"
4. View the fraud prediction with probability score and risk level

### 2. View Transaction Dashboard

- Navigate to `/dashboard`
- See all transactions in a table format
- Filter by fraud/legitimate
- Export to CSV

### 3. Analyze Trends

- Navigate to `/analytics`
- View interactive charts:
  - Fraud rate by transaction type
  - Geographic risk distribution
  - Hourly transaction patterns
  - Weekly fraud trends

### 4. Export Data

- Click "Export CSV" button on the dashboard
- Choose between all transactions or fraud-only
- Open in Excel or any spreadsheet software

---

## 🔌 API Documentation

### Base URL: `http://127.0.0.1:5000`

### Endpoints

#### 1. POST /predict
Submit a transaction for fraud analysis.

**Request:**
```json
{
  "amount": 4250.00,
  "type": "wire_transfer",
  "location": "high_risk_country",
  "hour": 3
}
```

**Response:**
```json
{
  "transaction_id": 42,
  "prediction": "FRAUD",
  "probability": 91.34,
  "is_fraud": true,
  "risk_level": "CRITICAL"
}
```

#### 2. GET /transactions
Retrieve transaction history.

**Query Parameters:**
- `limit` (optional): Max results (default: 100, max: 1000)
- `fraud_only` (optional): true/false (default: false)

**Response:**
```json
[
  {
    "id": 1,
    "amount": 4250.0,
    "type": "wire_transfer",
    "location": "high_risk_country",
    "hour": 3,
    "prediction": "FRAUD",
    "probability": 0.9134,
    "created_at": "2025-01-15T10:30:00"
  }
]
```

#### 3. GET /stats
Get aggregate statistics.

**Response:**
```json
{
  "total": 1250,
  "fraud_count": 275,
  "legit_count": 975,
  "avg_amount": 1234.56,
  "avg_fraud_prob": 78.45
}
```

#### 4. GET /analytics_data
Get data for charts and visualizations.

**Response:**
```json
{
  "by_type": [...],
  "by_location": [...],
  "by_hour": [...],
  "trends": [...]
}
```

#### 5. GET /export/csv
Export transactions as CSV file.

**Query Parameters:**
- `fraud_only` (optional): true/false

**Response:** CSV file download

#### 6. POST /feedback
Submit feedback on a prediction.

**Request:**
```json
{
  "transaction_id": 42,
  "is_correct": true,
  "comments": "Correctly identified fraud"
}
```

#### 7. GET /health
System health check.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "database_ok": true,
  "timestamp": "2025-01-15T10:30:00",
  "version": "2.0-enhanced"
}
```

---

## 🧠 Machine Learning Details

### Dataset

- **Size:** 10,000 synthetic transactions
- **Fraud Rate:** ~22% (imbalanced dataset)
- **Split:** 80% training, 20% testing (stratified)

### Features (10 total)

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 0 | log_amount | float | log(1 + amount) — reduces skew |
| 1 | hour | int | 0–23 |
| 2-6 | type_* | binary | One-hot encoded transaction type |
| 7-9 | loc_* | binary | One-hot encoded location |

### Models Compared

1. **Random Forest (Primary Model)**
   - 200 decision trees
   - Max depth: 10
   - Class weight: balanced
   - ROC-AUC: 0.945+

2. **Gradient Boosting**
   - 100 estimators
   - Learning rate: 0.1
   - ROC-AUC: 0.940+

3. **Logistic Regression (Baseline)**
   - With StandardScaler
   - Class weight: balanced
   - ROC-AUC: 0.892

### Performance Metrics

- **Accuracy:** 92%+
- **Precision (Fraud):** 86%
- **Recall (Fraud):** 78%
- **F1-Score (Fraud):** 82%
- **ROC-AUC:** 0.945

### Fraud Indicators (from synthetic data)

- Amount > $3,000 → +35% fraud probability
- Amount > $10,000 → +20% additional
- High-risk country → +30%
- International → +10%
- Wire transfer → +20%
- Online → +5%
- Late night (0-5 AM) → +15%

---

## 📂 Project Structure

```
fraud_detection_enhanced/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── model/
│   ├── train_model.py          # ML training script
│   ├── model.pkl               # Trained model (generated)
│   └── model_report.txt        # Training report (generated)
│
├── templates/
│   ├── index.html              # Transaction input form
│   ├── dashboard.html          # Transaction history dashboard
│   └── analytics.html          # Analytics & charts page
│
├── static/
│   ├── style.css               # Stylesheet
│   └── plots/                  # ML visualization plots (generated)
│       ├── roc_curves.png
│       ├── confusion_matrices.png
│       ├── feature_importance.png
│       └── precision_recall.png
│
├── database/
│   ├── db_setup.sql            # SQL schema reference
│   └── transactions.db         # SQLite database (auto-created)
│
├── logs/
│   └── fraud_detection.log     # Application logs (generated)
│
├── tests/                      # Unit tests (optional)
│   └── test_app.py
│
└── docs/                       # Additional documentation
    ├── PROJECT_REPORT.md
    ├── PRESENTATION.md
    └── USER_MANUAL.md
```

---

## 🧪 Testing

### Manual Testing

1. **Test Safe Transaction**
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 45, "type": "in-store", "location": "domestic", "hour": 14}'
```

2. **Test Fraudulent Transaction**
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 15000, "type": "wire_transfer", "location": "high_risk_country", "hour": 3}'
```

### Automated Testing (Optional)

Create `tests/test_app.py`:
```python
import pytest
from app import app

def test_health_endpoint():
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
```

Run tests:
```bash
pytest tests/
```

---

## 🚀 Deployment

### Option 1: Local Network Deployment

```bash
# Run on all network interfaces
python app.py
# Access from other devices: http://<your-ip>:5000
```

### Option 2: Using Gunicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 3: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python model/train_model.py
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t fraudiq .
docker run -p 5000:5000 fraudiq
```

---

## 🔮 Future Enhancements

### Planned Features

1. **Advanced ML**
   - Deep learning models (Neural Networks)
   - Anomaly detection algorithms
   - Online learning/model updates
   - Ensemble methods

2. **Features**
   - User authentication & roles
   - Email alerts for high-risk transactions
   - Real-time monitoring dashboard
   - Transaction velocity checks
   - Geolocation validation

3. **Integration**
   - REST API authentication (API keys)
   - Webhook support
   - Third-party fraud databases
   - Payment gateway integration

4. **UI/UX**
   - Mobile responsive design
   - Dark/light theme toggle
   - Multi-language support
   - Progressive Web App (PWA)

5. **Database**
   - PostgreSQL support
   - Redis caching
   - Time-series data storage
   - Data archiving

---

## 📄 License

MIT License - Free to use for educational purposes

---

## 👥 Contributors

- **Project Type:** 2nd Year CSE Mini-Project
- **Domain:** Machine Learning, Web Development, Data Science
- **Level:** Intermediate

---

## 📞 Support

For issues, questions, or contributions:
1. Check the documentation in `docs/` folder
2. Review the code comments
3. Test with the provided examples
4. Contact your project guide/mentor

---

## ✅ Project Submission Checklist

- [ ] Code is well-documented with comments
- [ ] README.md is complete
- [ ] Model training works successfully
- [ ] All API endpoints tested
- [ ] Screenshots/demo video prepared
- [ ] Project report written
- [ ] Presentation slides created
- [ ] Requirements.txt updated
- [ ] Database schema documented
- [ ] Future enhancements listed

---

**Built with ❤️ for learning and innovation**
