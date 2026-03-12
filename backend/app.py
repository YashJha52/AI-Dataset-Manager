import os
from flask import Flask, send_file
from flask_cors import CORS

from users import user_routes
from datasets import dataset_routes
from experiments import experiment_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(user_routes, url_prefix="/users")
app.register_blueprint(dataset_routes, url_prefix="/datasets")
app.register_blueprint(experiment_routes, url_prefix="/experiments")

# 1. Get the directory where app.py lives (backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level and into the frontend folder
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

# Dashboard page
@app.route("/")
def dashboard():
    return send_file(os.path.join(FRONTEND_DIR, "dashboard.html"))

# Login page
@app.route("/login")
def login():
    return send_file(os.path.join(FRONTEND_DIR, "login.html"))

# Dataset UI
@app.route("/datasets-ui")
def datasets_ui():
    return send_file(os.path.join(FRONTEND_DIR, "datasets.html"))

# Experiment UI
@app.route("/experiments-ui")
def experiments_ui():
    return send_file(os.path.join(FRONTEND_DIR, "experiments.html"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)