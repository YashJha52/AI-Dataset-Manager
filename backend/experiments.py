from flask import Blueprint, request, jsonify
from db import get_db_connection

experiment_routes = Blueprint("experiments", __name__)

@experiment_routes.route("/run", methods=["POST"])
def run_experiment():

    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Experiments (model_id, version_id, accuracy, loss)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (
        data["model_id"],
        data["version_id"],
        data["accuracy"],
        data["loss"]
    ))

    conn.commit()

    return jsonify({"message": "Experiment stored"})


@experiment_routes.route("/", methods=["GET"])
def get_experiments():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Experiments")

    experiments = cursor.fetchall()

    return jsonify(experiments)