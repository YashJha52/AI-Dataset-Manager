from flask import Blueprint, request, jsonify
from db import get_db_connection
import mysql.connector

user_routes = Blueprint("users", __name__)

@user_routes.route("/register", methods=["POST"])
def register():
    data  = request.json
    name  = data.get("name", "").strip()
    email = data.get("email", "").strip()
    role  = data.get("role", "developer")   # 'lead' or 'developer'

    if role not in ("lead", "developer"):
        role = "developer"

    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (name, email, role) VALUES (%s, %s, %s)",
            (name, email, role)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "role": role
        }), 201

    except mysql.connector.Error as err:
        if err.errno == 1062:
            return jsonify({"error": "A user with this email already exists!"}), 409
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        cursor.close()
        conn.close()


@user_routes.route("/", methods=["GET"])
def get_users():
    """Return all registered users (used to populate assignment dropdowns)."""
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, name, email, role FROM Users ORDER BY name")
        users = cursor.fetchall()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@user_routes.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Return a single user's info including role — used on login to identify role."""
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_id, name, email, role FROM Users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()