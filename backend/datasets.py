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

# ─── Dataset CRUD ─────────────────────────────────────────────────────────────

@dataset_routes.route("/create", methods=["POST"])
def create_dataset():
    name       = request.form.get("name")
    description = request.form.get("description")
    created_by = request.form.get("created_by")
    file       = request.files.get("file")

    if not file or not name or not created_by:
        return jsonify({"error": "Missing required fields or file"}), 400

    filename  = secure_filename(file.filename)
    save_name = f"v1_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, save_name)
    file.save(file_path)

    conn   = get_db_connection()
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
    file    = request.files.get("file")
    user_id = request.form.get("user_id")

    if not file or not user_id:
        return jsonify({"error": "File and User ID required"}), 400

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT version_id, version_number, storage_path
            FROM Dataset_Versions
            WHERE dataset_id = %s
            ORDER BY version_number DESC LIMIT 1
        """, (dataset_id,))
        latest = cursor.fetchone()
        if not latest:
            return jsonify({"error": "Dataset not found"}), 404

        filename  = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, "temp_" + filename)
        file.save(temp_path)

        new_hash = get_file_hash(temp_path)
        old_hash = get_file_hash(os.path.join(UPLOAD_FOLDER, latest['storage_path']))

        if new_hash == old_hash:
            os.remove(temp_path)
            return jsonify({"message": "Upload rejected: This file is identical to the current version."}), 200

        new_ver      = latest['version_number'] + 1
        final_name   = f"v{new_ver}_{filename}"
        os.rename(temp_path, os.path.join(UPLOAD_FOLDER, final_name))

        cursor.execute(
            "INSERT INTO Dataset_Versions (dataset_id, version_number, storage_path) VALUES (%s, %s, %s)",
            (dataset_id, new_ver, final_name)
        )
        new_version_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Dataset_Changes_Log (version_id, changed_by, change_description) VALUES (%s, %s, %s)",
            (new_version_id, user_id, "System Auto-Detect: File content modified. SHA-256 hash changed.")
        )
        conn.commit()
        return jsonify({"message": f"Changes detected! Version {new_ver} created."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@dataset_routes.route("/", methods=["GET"])
def get_datasets():
    """All datasets — used by leads."""
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.dataset_id, d.dataset_name, d.description, d.created_by,
               MAX(v.version_id) as version_id, MAX(v.version_number) as version_number,
               (SELECT storage_path FROM Dataset_Versions
                WHERE dataset_id = d.dataset_id ORDER BY version_number DESC LIMIT 1) as storage_path
        FROM Datasets d
        LEFT JOIN Dataset_Versions v ON d.dataset_id = v.dataset_id
        GROUP BY d.dataset_id, d.dataset_name, d.description, d.created_by
    """)
    datasets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(datasets)


@dataset_routes.route("/my/<int:user_id>", methods=["GET"])
def get_my_datasets(user_id):
    """Datasets assigned to a specific developer."""
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT d.dataset_id, d.dataset_name, d.description, d.created_by,
                   MAX(v.version_id) as version_id, MAX(v.version_number) as version_number,
                   (SELECT storage_path FROM Dataset_Versions
                    WHERE dataset_id = d.dataset_id ORDER BY version_number DESC LIMIT 1) as storage_path,
                   a.assignment_id, a.assigned_at,
                   lead.name AS assigned_by_name
            FROM Dataset_Assignments a
            JOIN Datasets d         ON a.dataset_id  = d.dataset_id
            JOIN Users lead         ON a.assigned_by = lead.user_id
            LEFT JOIN Dataset_Versions v ON d.dataset_id = v.dataset_id
            WHERE a.assigned_to = %s
            GROUP BY d.dataset_id, d.dataset_name, d.description, d.created_by,
                     a.assignment_id, a.assigned_at, lead.name
        """, (user_id,))
        datasets = cursor.fetchall()
        # Convert datetime to string
        for ds in datasets:
            if ds.get("assigned_at"):
                ds["assigned_at"] = ds["assigned_at"].strftime("%Y-%m-%d %H:%M")
        return jsonify(datasets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@dataset_routes.route("/search", methods=["GET"])
def search_datasets():
    q    = request.args.get("q", "").strip()
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
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@dataset_routes.route("/preview/<int:dataset_id>", methods=["GET"])
def preview_dataset(dataset_id):
    conn   = get_db_connection()
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
        rows, headers = [], []
        try:
            with open(file_path, newline='', encoding='utf-8', errors='replace') as f:
                reader  = csv.DictReader(f)
                headers = reader.fieldnames or []
                for i, r in enumerate(reader):
                    if i >= 10: break
                    rows.append(dict(r))
        except Exception:
            return jsonify({"error": "Could not parse file as CSV"}), 400
        return jsonify({"headers": headers, "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ─── Assignment endpoints ──────────────────────────────────────────────────────

@dataset_routes.route("/assign", methods=["POST"])
def assign_dataset():
    """Team lead assigns a dataset to a developer."""
    data        = request.json
    dataset_id  = data.get("dataset_id")
    assigned_to = data.get("assigned_to")   # developer user_id
    assigned_by = data.get("assigned_by")   # lead user_id

    if not dataset_id or not assigned_to or not assigned_by:
        return jsonify({"error": "dataset_id, assigned_to, and assigned_by are required"}), 400

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify the lead actually has the 'lead' role
        cursor.execute("SELECT role FROM Users WHERE user_id = %s", (assigned_by,))
        lead = cursor.fetchone()
        if not lead or lead["role"] != "lead":
            return jsonify({"error": "Only team leads can assign datasets"}), 403

        # Verify the target is a developer
        cursor.execute("SELECT role, name FROM Users WHERE user_id = %s", (assigned_to,))
        dev = cursor.fetchone()
        if not dev or dev["role"] != "developer":
            return jsonify({"error": "Datasets can only be assigned to developers"}), 400

        cursor.execute(
            "INSERT INTO Dataset_Assignments (dataset_id, assigned_to, assigned_by) VALUES (%s, %s, %s)",
            (dataset_id, assigned_to, assigned_by)
        )
        conn.commit()
        return jsonify({"message": f"Dataset assigned to {dev['name']} successfully!"}), 201
    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "This dataset is already assigned to that developer."}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@dataset_routes.route("/unassign/<int:assignment_id>", methods=["DELETE"])
def unassign_dataset(assignment_id):
    """Team lead removes an assignment."""
    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Dataset_Assignments WHERE assignment_id = %s", (assignment_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Assignment not found"}), 404
        return jsonify({"message": "Assignment removed."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@dataset_routes.route("/assignments/<int:dataset_id>", methods=["GET"])
def get_assignments(dataset_id):
    """Get all developers assigned to a specific dataset."""
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.assignment_id, a.assigned_at,
                   u.user_id, u.name, u.email
            FROM Dataset_Assignments a
            JOIN Users u ON a.assigned_to = u.user_id
            WHERE a.dataset_id = %s
            ORDER BY a.assigned_at DESC
        """, (dataset_id,))
        assignments = cursor.fetchall()
        for a in assignments:
            if a.get("assigned_at"):
                a["assigned_at"] = a["assigned_at"].strftime("%Y-%m-%d %H:%M")
        return jsonify(assignments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@dataset_routes.route("/log_change", methods=["POST"])
def log_change():
    data   = request.json
    conn   = get_db_connection()
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
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.change_description, c.change_date,
               IFNULL(u.name, 'System (Auto)') as user_name,
               v.version_number
        FROM Dataset_Changes_Log c
        LEFT JOIN Users u ON c.changed_by = u.user_id
        JOIN  Dataset_Versions v ON c.version_id = v.version_id
        WHERE v.dataset_id = %s
        ORDER BY c.change_date DESC
    """, (dataset_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(history)


@dataset_routes.route("/delete/<int:dataset_id>", methods=["DELETE"])
def delete_dataset(dataset_id):
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT storage_path FROM Dataset_Versions WHERE dataset_id = %s", (dataset_id,))
        for v in cursor.fetchall():
            if v['storage_path']:
                fp = os.path.join(UPLOAD_FOLDER, v['storage_path'])
                if os.path.exists(fp): os.remove(fp)
        cursor.execute("DELETE FROM Dataset_Assignments WHERE dataset_id = %s", (dataset_id,))
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