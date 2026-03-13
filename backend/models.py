from flask import Blueprint, request, jsonify
from db import get_db_connection

model_routes = Blueprint("models", __name__)

@model_routes.route("/create", methods=["POST"])
def create_model():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Models (model_name, algorithm)
    VALUES (%s, %s)
    """
    cursor.execute(query, (data["model_name"], data["algorithm"]))
    conn.commit()

    return jsonify({"message": "Model created"})


@model_routes.route("/", methods=["GET"])
def get_models():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Models")
    models = cursor.fetchall()

    return jsonify(models)