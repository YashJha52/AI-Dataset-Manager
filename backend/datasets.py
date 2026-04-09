import os
import csv
import hashlib
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from db import get_db_connection

dataset_routes = Blueprint("datasets", __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

@dataset_routes.route("/create", methods=["POST"])
def create_dataset():
    name = request.form.get("name")
    description = request.form.get("description")
    created_by = request.form.get("created_by")
    file = request.files.get("file")

    if not file or not name or not created_by:
        return jsonify({"error": "Missing required fields or file"}), 400

    filename = secure_filename(file.filename)
    save_name = f"v1_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, save_name)
    file.save(file_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Datasets (dataset_name, description, created_by) VALUES (%s, %s, %s)",
            (name, description, created_by)
        )
        dataset_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO Dataset_Versions (dataset_id, version_number, storage_path) VALUES (%s, %s, %s)",
            (dataset_id, 1, save_name)
        )
        conn.commit()
        return jsonify({"message": "Dataset and file uploaded successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@dataset_routes.route("/upload_version/<int:dataset_id>", methods=["POST"])
def upload_version(dataset_id):
    file = request.files.get("file")
    user_id = request.form.get("user_id")

    if not file or not user_id:
        return jsonify({"error": "File and User ID required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT version_id, version_number, storage_path
            FROM Dataset_Versions
            WHERE dataset_id = %s
            ORDER BY version_number DESC LIMIT 1
        """, (dataset_id,))
        latest_version = cursor.fetchone()

        if not latest_version:
            return jsonify({"error": "Dataset not found"}), 404

        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, "temp_" + filename)
        file.save(temp_path)

        new_hash = get_file_hash(temp_path)
        old_path = os.path.join(UPLOAD_FOLDER, latest_version['storage_path'])
        old_hash = get_file_hash(old_path)

        if new_hash == old_hash:
            os.remove(temp_path)
            return jsonify({"message": "Upload rejected: This file is identical to the current version."}), 200

        new_version_number = latest_version['version_number'] + 1
        final_filename = f"v{new_version_number}_{filename}"
        final_path = os.path.join(UPLOAD_FOLDER, final_filename)
        os.rename(temp_path, final_path)

        cursor.execute(
            "INSERT INTO Dataset_Versions (dataset_id, version_number, storage_path) VALUES (%s, %s, %s)",
            (dataset_id, new_version_number, final_filename)
        )
        new_version_id = cursor.lastrowid

        auto_log_msg = f"System Auto-Detect: File content modified. SHA-256 hash changed."
        cursor.execute(
            "INSERT INTO Dataset_Changes_Log (version_id, changed_by, change_description) VALUES (%s, %s, %s)",
            (new_version_id, user_id, auto_log_msg)
        )
        conn.commit()
        return jsonify({"message": f"Changes detected! Version {new_version_number} created."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@dataset_routes.route("/", methods=["GET"])
def get_datasets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT d.dataset_id, d.dataset_name, d.description, d.created_by,
           MAX(v.version_id) as version_id, MAX(v.version_number) as version_number,
           (SELECT storage_path FROM Dataset_Versions WHERE dataset_id = d.dataset_id ORDER BY version_number DESC LIMIT 1) as storage_path
    FROM Datasets d
    LEFT JOIN Dataset_Versions v ON d.dataset_id = v.dataset_id
    GROUP BY d.dataset_id
    """
    cursor.execute(query)
    datasets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(datasets)

@dataset_routes.route("/search", methods=["GET"])
def search_datasets():
    """Full-text search using MySQL MATCH...AGAINST"""
    q = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if not q:
            cursor.execute("""
                SELECT d.dataset_id, d.dataset_name, d.description, d.created_by,
                       MAX(v.version_id) as version_id, MAX(v.version_number) as version_number,
                       (SELECT storage_path FROM Dataset_Versions WHERE dataset_id = d.dataset_id ORDER BY version_number DESC LIMIT 1) as storage_path
                FROM Datasets d
                LEFT JOIN Dataset_Versions v ON d.dataset_id = v.dataset_id
                GROUP BY d.dataset_id
            """)
        else:
            cursor.execute("""
                SELECT d.dataset_id, d.dataset_name, d.description, d.created_by,
                       MAX(v.version_id) as version_id, MAX(v.version_number) as version_number,
                       (SELECT storage_path FROM Dataset_Versions WHERE dataset_id = d.dataset_id ORDER BY version_number DESC LIMIT 1) as storage_path
                FROM Datasets d
                LEFT JOIN Dataset_Versions v ON d.dataset_id = v.dataset_id
                WHERE MATCH(d.dataset_name, d.description) AGAINST (%s IN NATURAL LANGUAGE MODE)
                   OR d.dataset_name LIKE %s
                GROUP BY d.dataset_id
            """, (q, f"%{q}%"))
        results = cursor.fetchall()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@dataset_routes.route("/preview/<int:dataset_id>", methods=["GET"])
def preview_dataset(dataset_id):
    """Return first 10 rows of the latest version of a CSV dataset."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT storage_path FROM Dataset_Versions WHERE dataset_id=%s ORDER BY version_number DESC LIMIT 1",
            (dataset_id,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Dataset not found"}), 404

        file_path = os.path.join(UPLOAD_FOLDER, row['storage_path'])
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found on disk"}), 404

        rows = []
        headers = []
        try:
            with open(file_path, newline='', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                for i, r in enumerate(reader):
                    if i >= 10:
                        break
                    rows.append(dict(r))
        except Exception:
            return jsonify({"error": "Could not parse file as CSV"}), 400

        return jsonify({"headers": headers, "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@dataset_routes.route("/log_change", methods=["POST"])
def log_change():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Dataset_Changes_Log (version_id, changed_by, change_description) VALUES (%s, %s, %s)",
            (data["version_id"], data["user_id"], data["description"])
        )
        conn.commit()
        return jsonify({"message": "Change recorded!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@dataset_routes.route("/history/<int:dataset_id>", methods=["GET"])
def get_history(dataset_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT c.change_description, c.change_date, u.name as user_name, v.version_number
    FROM Dataset_Changes_Log c
    LEFT JOIN Users u ON c.changed_by = u.user_id
    JOIN Dataset_Versions v ON c.version_id = v.version_id
    WHERE v.dataset_id = %s
    ORDER BY c.change_date DESC
    """
    cursor.execute(query, (dataset_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(history)

@dataset_routes.route("/delete/<int:dataset_id>", methods=["DELETE"])
def delete_dataset(dataset_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT storage_path FROM Dataset_Versions WHERE dataset_id = %s", (dataset_id,))
        versions = cursor.fetchall()
        for v in versions:
            if v['storage_path']:
                file_path = os.path.join(UPLOAD_FOLDER, v['storage_path'])
                if os.path.exists(file_path):
                    os.remove(file_path)

        cursor.execute("DELETE FROM Dataset_Changes_Log WHERE version_id IN (SELECT version_id FROM Dataset_Versions WHERE dataset_id = %s)", (dataset_id,))
        cursor.execute("DELETE FROM Experiments WHERE version_id IN (SELECT version_id FROM Dataset_Versions WHERE dataset_id = %s)", (dataset_id,))
        cursor.execute("DELETE FROM Dataset_Versions WHERE dataset_id = %s", (dataset_id,))
        cursor.execute("DELETE FROM Datasets WHERE dataset_id = %s", (dataset_id,))
        conn.commit()
        return jsonify({"message": "Dataset successfully deleted!"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()