import os
from flask import Flask, render_template
from flask_cors import CORS

from users import user_routes
from datasets import dataset_routes
from experiments import experiment_routes
from db import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

app = Flask(__name__, template_folder=FRONTEND_DIR)
CORS(app)

app.register_blueprint(user_routes, url_prefix="/users")
app.register_blueprint(dataset_routes, url_prefix="/datasets")
app.register_blueprint(experiment_routes, url_prefix="/experiments")

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/datasets-ui")
def datasets_ui():
    # Back to serving just the HTML page. JS will fetch the data!
    return render_template("datasets.html")

@app.route("/experiments-ui")
def experiments_ui():
    return render_template("experiments.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)