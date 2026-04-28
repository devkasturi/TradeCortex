"""
auth_routes.py — TradeCortex Authentication Routes
Add this to your project root and register it in app.py

SETUP:
1. pip install flask-session bcrypt
2. Add to MySQL:
   ALTER TABLE users ADD COLUMN ... (or run init_users_table())
3. Register blueprint in app.py:
   from auth_routes import auth_bp
   app.register_blueprint(auth_bp)
   app.secret_key = os.getenv("SECRET_KEY", "tradecortex-secret-change-me")
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
import sqlite3
from sqlite3 import Error
import hashlib
import os
import re

auth_bp = Blueprint("auth", __name__)

# Reuse DB config from db_service.py
DB_PATH = os.getenv("DB_PATH", "stock_project.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Simple SHA-256 hash. For production use bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_users_table():
    """Create users table if it doesn't exist."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                investor_type TEXT DEFAULT 'moderate',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Users table init error: {e}")
        return False


# ── PAGES ──────────────────────────────────────────────

@auth_bp.route("/login")
def login_page():
    """Serve the login/signup page."""
    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))
    return render_template("auth.html")


@auth_bp.route("/dashboard")
def dashboard():
    """Serve the main dashboard (requires login)."""
    # Remove the login check below if you want open access during development:
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    return render_template("index.html")


# ── API ROUTES ─────────────────────────────────────────

@auth_bp.route("/api/auth/signup", methods=["POST"])
def signup():
    """Register a new user."""
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    investor_type = data.get("investor_type", "moderate")

    # Validate
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"success": False, "error": "Invalid email address"}), 400
    if len(password) < 8:
        return jsonify({"success": False, "error": "Password must be at least 8 characters"}), 400

    password_hash = hash_password(password)

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash, first_name, last_name, investor_type) VALUES (?, ?, ?, ?, ?)",
            (email, password_hash, first_name, last_name, investor_type)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Auto login after signup
        session["user_id"] = user_id
        session["email"] = email
        session["name"] = f"{first_name} {last_name}".strip() or email.split("@")[0]
        session["investor_type"] = investor_type

        return jsonify({
            "success": True,
            "user": {"id": user_id, "email": email, "name": session["name"]}
        })

    except Error as e:
        if "Duplicate entry" in str(e):
            return jsonify({"success": False, "error": "An account with this email already exists"}), 409
        return jsonify({"success": False, "error": "Database error: " + str(e)}), 500


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate existing user."""
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    password_hash = hash_password(password)

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, first_name, last_name, investor_type FROM users WHERE email=? AND password_hash=?",
            (email, password_hash)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["name"] = f"{user['first_name']} {user['last_name']}".strip() or email.split("@")[0]
        session["investor_type"] = user["investor_type"]

        return jsonify({
            "success": True,
            "user": {"id": user["id"], "email": user["email"], "name": session["name"]}
        })

    except Error as e:
        return jsonify({"success": False, "error": "Database error: " + str(e)}), 500


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Clear session."""
    session.clear()
    return jsonify({"success": True})


@auth_bp.route("/api/auth/me")
def me():
    """Return current session user info."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    return jsonify({
        "success": True,
        "id": session["user_id"],
        "email": session.get("email"),
        "name": session.get("name"),
        "investor_type": session.get("investor_type", "moderate"),
    })