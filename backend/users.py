from flask import Blueprint, request, jsonify
from db import get_db_connection
import mysql.connector

user_routes = Blueprint("users", __name__)

@user_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO Users (name, email) VALUES (%s, %s)"
    
    try:
        cursor.execute(query, (data["name"], data["email"]))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
        
    except mysql.connector.Error as err:
        # Error 1062 is MySQL's specific code for a "Duplicate Entry"
        if err.errno == 1062:
            return jsonify({"error": "A user with this email already exists!"}), 409
        else:
            # Catch any other database errors just in case
            return jsonify({"error": "Database error occurred."}), 500
            
    finally:
        # Always close your connections when done to prevent memory leaks
        cursor.close()
        conn.close()