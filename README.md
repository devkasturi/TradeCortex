# 🧠 TradeCortex AI — Setup Guide

## Project Structure
```
TradeCortex/
├── app.py                  ← Main Flask app (all API routes)
├── db.py                   ← DB connection (backward compat)
├── requirements.txt
├── templates/
│   └── index.html          ← Jaw-dropping UI
└── services/
    ├── __init__.py
    ├── stock_service.py    ← yfinance data fetching
    ├── news_service.py     ← News headlines
    ├── sentiment.py        ← TextBlob sentiment analysis
    ├── ml_predictor.py     ← Linear Regression ML engine
    ├── volatility.py       ← EVS calculation (USP)
    ├── recommendation.py   ← Smart recommendation engine
    ├── explanation.py      ← Explainable AI
    └── db_service.py       ← MySQL CRUD operations
```

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
python -m textblob.download_corpora   # Download TextBlob data
```

### 2. MySQL Setup
```sql
-- Run in MySQL:
CREATE DATABASE IF NOT EXISTS stock_project;
-- The app auto-creates the table on startup
```

### 3. Configure DB credentials
Edit `services/db_service.py` (or set env vars):
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "stock_project",
}
```

Or use environment variables:
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=Tina@2006
export DB_NAME=stock_project
```

### 4. Run the app
```bash
cd TradeCortex
python app.py
```

Open: http://localhost:5000

## 🚀 Features
1. **AI Price Prediction** — Linear Regression on historical data
2. **Real-Time Stock Data** — yfinance integration
3. **Sentiment Analysis** — TextBlob NLP on news headlines
4. **EVS Score** — Emotional Volatility Score (YOUR USP)
5. **Smart Recommendation** — Buy / Hold / Sell engine
6. **Investor Mode** — Conservative / Moderate / Aggressive
7. **Explainable AI** — Human-readable decision reasoning
8. **Report Storage** — MySQL database persistence
9. **Jaw-Dropping UI** — Dark mode professional dashboard
10. **Data Visualization** — Chart.js price + prediction charts

## 📡 API Endpoints
- `GET /` — Main dashboard UI
- `GET /api/analyze?symbol=AAPL&investor_type=moderate` — Full analysis
- `GET /api/history` — Recent reports from DB
