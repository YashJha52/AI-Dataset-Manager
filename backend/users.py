from flask import Blueprint, request, jsonify
from db import get_db_connection

user_routes = Blueprint("users", __name__)

@user_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO Users (name, email) VALUES (%s, %s)"
    cursor.execute(query, (data["name"], data["email"]))

    conn.commit()

    return jsonify({"message": "User registered"})