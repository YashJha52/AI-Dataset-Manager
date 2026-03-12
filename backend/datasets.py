from flask import Blueprint, request, jsonify
from db import get_db_connection

dataset_routes = Blueprint("datasets", __name__)

@dataset_routes.route("/create", methods=["POST"])
def create_dataset():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Datasets (dataset_name, description, created_by)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (
        data["name"],
        data["description"],
        data["created_by"]
    ))

    conn.commit()

    return jsonify({"message": "Dataset created"})


@dataset_routes.route("/", methods=["GET"])
def get_datasets():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Datasets")

    datasets = cursor.fetchall()

    return jsonify(datasets)