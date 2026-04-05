import os
from flask import Flask, render_template
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
from users import user_routes
from datasets import dataset_routes
from experiments import experiment_routes
from db import get_db_connection
from versions import version_routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

app = Flask(__name__, template_folder=FRONTEND_DIR)
CORS(app)

app.register_blueprint(user_routes, url_prefix="/users")
app.register_blueprint(dataset_routes, url_prefix="/datasets")
app.register_blueprint(experiment_routes, url_prefix="/experiments")
app.register_blueprint(version_routes, url_prefix="/versions")

@app.route("/")
def dashboard():
    return render_template("frontend/dashboard.html")

@app.route("/login")
def login():
    return render_template("frontend/login.html")

@app.route("/datasets-ui")
def datasets_ui():
    # Back to serving just the HTML page. JS will fetch the data!
    return render_template("frontend/datasets.html")

@app.route("/experiments-ui")
def experiments_ui():
    return render_template("frontend/experiments.html")

@app.route("/versions-ui")
def versions_ui():
    return send_file(os.path.join(FRONTEND_DIR, "versions.html"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)