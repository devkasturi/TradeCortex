import sqlite3
from sqlite3 import Error
import os

DB_PATH = os.getenv("DB_PATH", "stock_project.db")

def get_db_connection():
    """Get a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database and create tables if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL,
                sentiment_label TEXT,
                sentiment_score REAL,
                volatility REAL,
                risk_level TEXT,
                recommendation TEXT,
                explanation TEXT,
                predicted_price REAL,
                evs_score REAL,
                evs_level TEXT,
                investor_type TEXT,
                ml_accuracy REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Database init error: {e}")
        return False

def save_report(symbol, price, sentiment_label, sentiment_score, volatility,
                risk_level, recommendation, explanation, predicted_price=0,
                evs_score=0, evs_level="N/A", investor_type="moderate", ml_accuracy=0):
    """Save analysis report to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stock_reports (symbol, price, sentiment_label, sentiment_score,
                volatility, risk_level, recommendation, explanation, predicted_price,
                evs_score, evs_level, investor_type, ml_accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol, price, sentiment_label, sentiment_score, volatility,
              risk_level, recommendation, explanation, predicted_price,
              evs_score, evs_level, investor_type, ml_accuracy))
        conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return inserted_id
    except Error as e:
        print(f"DB save error: {e}")
        return None

def get_recent_reports(limit: int = 10) -> list:
    """Fetch recent reports from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM stock_reports ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Convert Row to dict
        reports = []
        for row in rows:
            report = dict(row)
            if report.get("created_at"):
                report["created_at"] = str(report["created_at"])
            reports.append(report)
        return reports
    except Error as e:
        print(f"DB fetch error: {e}")
        return []
