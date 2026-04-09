import os
from flask import Flask, render_template, send_file, jsonify, send_from_directory
from flask_cors import CORS
from flask import request
from users import user_routes
from datasets import dataset_routes
from experiments import experiment_routes
from db import get_db_connection
from versions import version_routes
from models import model_routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

# Serve the frontend folder as static files at the root URL.
# This means http://localhost:5000/datasets.html → frontend/datasets.html
# API routes below take PRIORITY over these static files (Flask routes first).
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

app.register_blueprint(user_routes,       url_prefix="/users")
app.register_blueprint(dataset_routes,    url_prefix="/datasets")
app.register_blueprint(experiment_routes, url_prefix="/experiments")
app.register_blueprint(version_routes,    url_prefix="/versions")
app.register_blueprint(model_routes,      url_prefix="/models")

# ─── Page routes ─────────────────────────────────────────────────────────────
# These serve the HTML pages. A dedicated route for "/" is needed because
# a static_url_path='' setup doesn't automatically serve index pages.

@app.route("/")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")

@app.route("/dashboard.html")
def dashboard_html():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")

@app.route("/datasets.html")
def datasets_html():
    return send_from_directory(FRONTEND_DIR, "datasets.html")

@app.route("/experiments.html")
def experiments_html():
    return send_from_directory(FRONTEND_DIR, "experiments.html")

@app.route("/versions.html")
def versions_html():
    return send_from_directory(FRONTEND_DIR, "versions.html")

@app.route("/models.html")
def models_html():
    return send_from_directory(FRONTEND_DIR, "models.html")

@app.route("/login.html")
def login_html():
    return send_from_directory(FRONTEND_DIR, "login.html")

# Legacy Flask-route aliases — redirect to the .html equivalents so any
# old bookmarks or links still work.
@app.route("/login")
def login():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/datasets-ui")
def datasets_ui():
    return send_from_directory(FRONTEND_DIR, "datasets.html")

@app.route("/experiments-ui")
def experiments_ui():
    return send_from_directory(FRONTEND_DIR, "experiments.html")

@app.route("/versions-ui")
def versions_ui():
    return send_from_directory(FRONTEND_DIR, "versions.html")

@app.route("/models-ui")
def models_ui():
    return send_from_directory(FRONTEND_DIR, "models.html")

# ─── Global Stats endpoint ────────────────────────────────────────────────────

@app.route("/stats")
def get_stats():
    """Returns aggregate counts across all tables for the dashboard KPI cards."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM Datasets)           AS total_datasets,
                (SELECT COUNT(*) FROM Dataset_Versions)   AS total_versions,
                (SELECT COUNT(*) FROM Experiments)        AS total_experiments,
                (SELECT COUNT(*) FROM Models)             AS total_models,
                (SELECT COUNT(*) FROM Users)              AS total_users,
                (SELECT ROUND(AVG(accuracy), 3)
                 FROM Experiments WHERE accuracy IS NOT NULL) AS avg_accuracy
        """)
        stats = cursor.fetchone()
        if stats.get("avg_accuracy") is not None:
            stats["avg_accuracy"] = float(stats["avg_accuracy"])
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)