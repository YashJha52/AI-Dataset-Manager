from flask import Blueprint, request, jsonify
from db import get_db_connection
import mysql.connector

version_routes = Blueprint("versions", __name__)

@version_routes.route("/create", methods=["POST"])
def create_version():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Dataset_Versions (dataset_id, version_number, storage_path)
    VALUES (%s, %s, %s)
    """
    
    try:
        cursor.execute(query, (data["dataset_id"], data["version_number"], data["storage_path"]))
        conn.commit()
        return jsonify({"message": "Version created successfully"}), 201
    except mysql.connector.Error as err:
        # Error 1452 is a Foreign Key constraint failure (Dataset ID doesn't exist)
        if err.errno == 1452:
            return jsonify({"error": "That Dataset ID does not exist. Please create the Dataset first."}), 400
        else:
            return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@version_routes.route("/", methods=["GET"])
def get_versions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Dataset_Versions")
    versions = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return jsonify(versions)