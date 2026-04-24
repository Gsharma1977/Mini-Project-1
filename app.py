"""
╔══════════════════════════════════════════════════════════╗
║   FraudIQ - Enhanced AI Fraud Detection System           ║
║   Flask Backend · REST API · SQLite · ML Analytics       ║
║   2nd Year CSE Project                                   ║
╚══════════════════════════════════════════════════════════╝

ENHANCEMENTS OVER BASIC VERSION:
  ✓ Advanced analytics dashboard with charts
  ✓ CSV/PDF export functionality
  ✓ Transaction history analysis
  ✓ Model performance metrics visualization
  ✓ Enhanced error handling & logging
  ✓ Rate limiting for API security
  ✓ Feedback collection system
"""

import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, g, send_file
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import csv
import io

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "database", "transactions.db")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
LOG_DIR    = os.path.join(BASE_DIR, "logs")

# ── Logging Setup ──────────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'fraud_detection.log'),
    maxBytes=10485760,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# ── Encodings (must exactly match values used in train_model.py) ───────────────
TRANSACTION_TYPES = ["online", "in-store", "atm", "wire_transfer", "mobile"]
LOCATIONS         = ["domestic", "international", "high_risk_country"]

# ── Cache the model in memory after first load ─────────────────────────────────
_MODEL_CACHE = None

def load_model():
    """Load the trained model once and cache it for subsequent requests."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Run:  python model/train_model.py"
        )
    with open(MODEL_PATH, "rb") as f:
        _MODEL_CACHE = pickle.load(f)
    app.logger.info("Model loaded and cached successfully")
    print("✅  Model loaded and cached.")
    return _MODEL_CACHE

# ── Rate Limiting (Simple in-memory counter) ────────────────────────────────────
from collections import defaultdict
from time import time

request_counts = defaultdict(list)

def rate_limit(max_requests=100, window=60):
    """Simple rate limiting decorator - max_requests per window (seconds)"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time()
            client_ip = request.remote_addr
            
            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < window
            ]
            
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded. Try again later."}), 429
            
            request_counts[client_ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ── Database helpers ───────────────────────────────────────────────────────────
def get_db():
    """Return a thread-local SQLite connection stored in Flask's 'g' object."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc=None):
    """Automatically close DB connection at the end of each request."""
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    """Create the database tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # Main transactions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            amount      REAL    NOT NULL,
            type        TEXT    NOT NULL,
            location    TEXT    NOT NULL,
            hour        INTEGER NOT NULL,
            prediction  TEXT    NOT NULL,
            probability REAL    NOT NULL,
            created_at  TEXT    NOT NULL,
            ip_address  TEXT
        )
    """)
    
    # Feedback table for model improvement
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id  INTEGER NOT NULL,
            is_correct      INTEGER NOT NULL,
            comments        TEXT,
            created_at      TEXT NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id)
        )
    """)
    
    conn.commit()
    conn.close()
    app.logger.info("Database initialized successfully")
    print("✅  Database ready.")

# ── Feature engineering ────────────────────────────────────────────────────────
def build_feature_vector(amount, tx_type, location, hour):
    """Convert raw transaction inputs into numeric feature vector."""
    log_amount   = np.log1p(float(amount))
    type_encoded = [1 if tx_type  == t else 0 for t in TRANSACTION_TYPES]
    loc_encoded  = [1 if location == l else 0 for l in LOCATIONS]
    features     = [log_amount, int(hour)] + type_encoded + loc_encoded
    return np.array(features).reshape(1, -1)

# ── Risk level helper ──────────────────────────────────────────────────────────
def _risk_level(prob):
    """Map fraud probability to a human-readable risk tier."""
    if prob < 0.3:  return "LOW"
    if prob < 0.6:  return "MEDIUM"
    if prob < 0.8:  return "HIGH"
    return "CRITICAL"

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main transaction-check form."""
    return render_template("index.html",
                           transaction_types=TRANSACTION_TYPES,
                           locations=LOCATIONS)

@app.route("/dashboard")
def dashboard():
    """Serve the enhanced admin dashboard page."""
    return render_template("dashboard.html")

@app.route("/analytics")
def analytics():
    """Serve the analytics page with charts and insights."""
    return render_template("analytics.html")

# ── /predict ──────────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
@rate_limit(max_requests=50, window=60)
def predict():
    """
    POST /predict - Main fraud detection endpoint
    Request: { amount, type, location, hour }
    Response: { prediction, probability, is_fraud, risk_level }
    """
    try:
        data = request.get_json(force=True)

        # Extract and validate fields
        amount   = data.get("amount")
        tx_type  = data.get("type")
        location = data.get("location")
        hour     = data.get("hour")

        if None in (amount, tx_type, location, hour):
            return jsonify({"error": "Missing required fields: amount, type, location, hour"}), 400

        try:
            amount = float(amount)
            hour   = int(hour)
        except (ValueError, TypeError):
            return jsonify({"error": "amount must be a number and hour must be an integer"}), 400

        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400
        if tx_type not in TRANSACTION_TYPES:
            return jsonify({"error": f"Invalid type. Valid options: {TRANSACTION_TYPES}"}), 400
        if location not in LOCATIONS:
            return jsonify({"error": f"Invalid location. Valid options: {LOCATIONS}"}), 400
        if not (0 <= hour <= 23):
            return jsonify({"error": "Hour must be between 0 and 23"}), 400

        # Run prediction
        model    = load_model()
        X        = build_feature_vector(amount, tx_type, location, hour)
        prob     = float(model.predict_proba(X)[0][1])
        is_fraud = prob >= 0.5
        label    = "FRAUD" if is_fraud else "LEGITIMATE"

        # Persist to database
        db = get_db()
        cursor = db.execute(
            """INSERT INTO transactions
               (amount, type, location, hour, prediction, probability, created_at, ip_address)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (amount, tx_type, location, hour,
             label, round(prob, 6), datetime.utcnow().isoformat(), request.remote_addr)
        )
        db.commit()
        transaction_id = cursor.lastrowid

        app.logger.info(f"Prediction made: ID={transaction_id}, Fraud={is_fraud}, Prob={prob:.4f}")

        return jsonify({
            "transaction_id": transaction_id,
            "prediction":  label,
            "probability": round(prob * 100, 2),
            "is_fraud":    is_fraud,
            "risk_level":  _risk_level(prob)
        })

    except FileNotFoundError as e:
        app.logger.error(f"Model not found: {e}")
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        app.logger.exception("Prediction error")
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

# ── /transactions ──────────────────────────────────────────────────────────────
@app.route("/transactions", methods=["GET"])
def get_transactions():
    """
    GET /transactions?limit=100&fraud_only=false
    Returns recent transactions as JSON array.
    """
    try:
        limit      = max(1, min(int(request.args.get("limit", 100)), 1000))
        fraud_only = request.args.get("fraud_only", "false").lower() == "true"

        db = get_db()
        if fraud_only:
            rows = db.execute(
                "SELECT * FROM transactions WHERE prediction='FRAUD' ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM transactions ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()

        return jsonify([dict(r) for r in rows])

    except Exception as e:
        app.logger.exception("Fetch transactions error")
        return jsonify({"error": str(e)}), 500

# ── /stats ─────────────────────────────────────────────────────────────────────
@app.route("/stats", methods=["GET"])
def get_stats():
    """GET /stats - Returns aggregate statistics."""
    try:
        db  = get_db()
        row = db.execute("""
            SELECT
                COUNT(*)                                        AS total,
                SUM(prediction = 'FRAUD')                      AS fraud_count,
                SUM(prediction = 'LEGITIMATE')                 AS legit_count,
                ROUND(AVG(amount), 2)                          AS avg_amount,
                ROUND(AVG(CASE WHEN prediction='FRAUD'
                               THEN probability END) * 100, 2) AS avg_fraud_prob
            FROM transactions
        """).fetchone()
        return jsonify(dict(row))
    except Exception as e:
        app.logger.exception("Stats error")
        return jsonify({"error": str(e)}), 500

# ── /analytics_data ────────────────────────────────────────────────────────────
@app.route("/analytics_data", methods=["GET"])
def analytics_data():
    """GET /analytics_data - Returns data for charts and visualizations."""
    try:
        db = get_db()
        
        # Fraud by transaction type
        type_data = db.execute("""
            SELECT type, 
                   COUNT(*) as total,
                   SUM(prediction = 'FRAUD') as fraud_count
            FROM transactions
            GROUP BY type
        """).fetchall()
        
        # Fraud by location
        location_data = db.execute("""
            SELECT location,
                   COUNT(*) as total,
                   SUM(prediction = 'FRAUD') as fraud_count
            FROM transactions
            GROUP BY location
        """).fetchall()
        
        # Fraud by hour distribution
        hour_data = db.execute("""
            SELECT hour,
                   COUNT(*) as total,
                   SUM(prediction = 'FRAUD') as fraud_count
            FROM transactions
            GROUP BY hour
            ORDER BY hour
        """).fetchall()
        
        # Recent trends (last 7 days)
        trend_data = db.execute("""
            SELECT DATE(created_at) as date,
                   COUNT(*) as total,
                   SUM(prediction = 'FRAUD') as fraud_count
            FROM transactions
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """).fetchall()
        
        return jsonify({
            "by_type": [dict(r) for r in type_data],
            "by_location": [dict(r) for r in location_data],
            "by_hour": [dict(r) for r in hour_data],
            "trends": [dict(r) for r in trend_data]
        })
        
    except Exception as e:
        app.logger.exception("Analytics data error")
        return jsonify({"error": str(e)}), 500

# ── /export/csv ────────────────────────────────────────────────────────────────
@app.route("/export/csv", methods=["GET"])
def export_csv():
    """Export transactions to CSV file."""
    try:
        fraud_only = request.args.get("fraud_only", "false").lower() == "true"
        
        db = get_db()
        if fraud_only:
            rows = db.execute(
                "SELECT * FROM transactions WHERE prediction='FRAUD' ORDER BY id DESC"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM transactions ORDER BY id DESC"
            ).fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Amount', 'Type', 'Location', 'Hour', 'Prediction', 'Probability', 'Created At'])
        
        # Write data
        for row in rows:
            writer.writerow([
                row['id'], row['amount'], row['type'], row['location'],
                row['hour'], row['prediction'], row['probability'], row['created_at']
            ])
        
        # Prepare response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'transactions_{"fraud_only" if fraud_only else "all"}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        app.logger.exception("CSV export error")
        return jsonify({"error": str(e)}), 500

# ── /feedback ──────────────────────────────────────────────────────────────────
@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    POST /feedback - Submit feedback on a prediction
    Request: { transaction_id, is_correct, comments }
    """
    try:
        data = request.get_json(force=True)
        transaction_id = data.get("transaction_id")
        is_correct = data.get("is_correct")
        comments = data.get("comments", "")
        
        if transaction_id is None or is_correct is None:
            return jsonify({"error": "Missing required fields: transaction_id, is_correct"}), 400
        
        db = get_db()
        db.execute(
            """INSERT INTO feedback (transaction_id, is_correct, comments, created_at)
               VALUES (?, ?, ?, ?)""",
            (transaction_id, int(is_correct), comments, datetime.utcnow().isoformat())
        )
        db.commit()
        
        app.logger.info(f"Feedback received for transaction {transaction_id}")
        return jsonify({"message": "Feedback submitted successfully"}), 201
        
    except Exception as e:
        app.logger.exception("Feedback submission error")
        return jsonify({"error": str(e)}), 500

# ── /health ─────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    """Enhanced health-check endpoint."""
    try:
        model_ok = os.path.exists(MODEL_PATH)
        db_ok = os.path.exists(DB_PATH)
        
        # Check database connectivity
        if db_ok:
            db = get_db()
            db.execute("SELECT 1").fetchone()
        
        return jsonify({
            "status": "ok" if (model_ok and db_ok) else "degraded",
            "model_loaded": model_ok,
            "database_ok": db_ok,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0-enhanced"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    load_model()
    app.logger.info("FraudIQ Enhanced started successfully")
    print("🚀  FraudIQ Enhanced running → http://127.0.0.1:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
