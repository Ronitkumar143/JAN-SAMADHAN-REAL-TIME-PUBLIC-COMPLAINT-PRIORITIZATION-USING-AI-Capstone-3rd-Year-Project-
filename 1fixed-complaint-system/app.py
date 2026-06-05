from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from clustering import cluster_complaints
import joblib
import warnings
import json
import os
import uuid
from datetime import datetime

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = "jansamadhan_secret_2026"
CORS(app)

# Load trained model once when Flask starts
pipeline = joblib.load("backend/models/linear_svc_pipeline.pkl")

# In-memory stores (replace with DB in production)
users = {}       # phone/email -> user info
complaints = []  # all complaints

ADMIN_ID = "admin@829206"
ADMIN_PASS = "123456"


# ── Auth helpers ──────────────────────────────────────────────────
def current_user():
    return session.get("user")

def is_admin():
    return session.get("role") == "admin"


# ── Pages ─────────────────────────────────────────────────────────
@app.route("/")
def home():
    if current_user():
        if is_admin():
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("user_dashboard"))
    return render_template("login.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def user_dashboard():
    if not current_user() or is_admin():
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/submit-complaint")
def submit_complaint_page():
    if not current_user() or is_admin():
        return redirect(url_for("login_page"))
    return render_template("report.html")

@app.route("/admin")
def admin_dashboard():
    if not is_admin():
        return redirect(url_for("login_page"))
    return render_template("admin.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── Auth API ──────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "").strip()

    # Admin check
    if identifier == ADMIN_ID and password == ADMIN_PASS:
        session["user"] = "Administrator"
        session["uid"] = "admin"
        session["role"] = "admin"
        return jsonify({"success": True, "role": "admin"})

    # User check
    user = users.get(identifier)
    if not user:
        return jsonify({"success": False, "error": "Account not found. Please register first."})
    if user["password"] != password:
        return jsonify({"success": False, "error": "Incorrect password."})

    session["user"] = user["name"]
    session["uid"] = identifier
    session["role"] = "user"
    return jsonify({"success": True, "role": "user"})

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    name = data.get("name", "").strip()
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "").strip()

    if not name or not identifier or not password:
        return jsonify({"success": False, "error": "All fields are required."})
    if identifier in users:
        return jsonify({"success": False, "error": "Account already exists. Please login."})

    users[identifier] = {"name": name, "password": password, "identifier": identifier}
    session["user"] = name
    session["uid"] = identifier
    session["role"] = "user"
    return jsonify({"success": True})

@app.route("/api/me")
def api_me():
    if not current_user():
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "name": session.get("user"),
        "uid": session.get("uid"),
        "role": session.get("role")
    })


# ── Complaint API ─────────────────────────────────────────────────
@app.route("/api/submit", methods=["POST"])
def api_submit():
    if not current_user() or is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    text = data.get("complaint", "").strip()
    title = data.get("title", "Untitled").strip()
    location = data.get("location", "").strip()
    manual_cat = data.get("manual_category", "")

    if not text:
        return jsonify({"error": "Complaint text required"}), 400

    ai_category = pipeline.predict([text])[0]

    complaint = {
        "id": str(uuid.uuid4())[:8].upper(),
        "uid": session["uid"],
        "user_name": session["user"],
        "title": title,
        "complaint": text,
        "location": location,
        "manual_category": manual_cat,
        "ai_category": ai_category,
        "status": "Pending",
        "submitted_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "resolved_at": None,
        "admin_note": ""
    }
    complaints.append(complaint)
    return jsonify({"success": True, "complaint": complaint})

@app.route("/api/my-complaints")
def api_my_complaints():
    if not current_user():
        return jsonify({"error": "Unauthorized"}), 401
    uid = session["uid"]
    my = [c for c in complaints if c["uid"] == uid]
    return jsonify(my)

@app.route("/api/all-complaints")
def api_all_complaints():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(complaints)

@app.route("/api/update-status", methods=["POST"])
def api_update_status():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    cid = data.get("id")
    new_status = data.get("status")
    note = data.get("note", "")
    for c in complaints:
        if c["id"] == cid:
            c["status"] = new_status
            c["admin_note"] = note
            if new_status == "Resolved":
                c["resolved_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
            return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/clusters")
def api_clusters():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 401
    texts = [c["complaint"] for c in complaints]
    if len(texts) < 5:
        return jsonify({"error": "Need at least 5 complaints"})
    return jsonify(cluster_complaints(texts))

@app.route("/api/stats")
def api_stats():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 401
    total = len(complaints)
    pending = sum(1 for c in complaints if c["status"] == "Pending")
    resolved = sum(1 for c in complaints if c["status"] == "Resolved")
    in_progress = sum(1 for c in complaints if c["status"] == "In Progress")
    cats = {}
    for c in complaints:
        cats[c["ai_category"]] = cats.get(c["ai_category"], 0) + 1
    return jsonify({
        "total": total, "pending": pending,
        "resolved": resolved, "in_progress": in_progress,
        "categories": cats
    })

if __name__ == "__main__":
    app.run(debug=True)
