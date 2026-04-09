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
    try:
        cursor.execute(query, (
            data["model_id"],
            data["version_id"],
            data["accuracy"],
            data["loss"]
        ))
        conn.commit()
        return jsonify({"message": "Experiment stored"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@experiment_routes.route("/", methods=["GET"])
def get_experiments():
    """
    Returns enriched experiment list joined with model name and dataset version info,
    using the vw_best_experiments view for richer data.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.experiment_id, e.model_id, e.version_id,
                   m.model_name, m.algorithm,
                   v.version_number,
                   d.dataset_name,
                   ROUND(e.accuracy, 4) AS accuracy,
                   ROUND(e.loss, 4) AS loss,
                   e.run_date
            FROM Experiments e
            LEFT JOIN Models m           ON e.model_id   = m.model_id
            LEFT JOIN Dataset_Versions v ON e.version_id = v.version_id
            LEFT JOIN Datasets d         ON v.dataset_id = d.dataset_id
            ORDER BY e.run_date DESC
        """)
        experiments = cursor.fetchall()
        # run_date is a datetime object — convert to string for JSON
        for exp in experiments:
            if exp.get("run_date"):
                exp["run_date"] = exp["run_date"].strftime("%Y-%m-%d %H:%M")
        return jsonify(experiments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@experiment_routes.route("/analytics", methods=["GET"])
def get_analytics():
    """
    Returns data structured for Chart.js:
    - accuracy_by_model: avg accuracy per model algorithm
    - accuracy_over_time: experiment accuracy ordered by date (last 20)
    - model_comparison: all model names + their avg accuracy + avg loss
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Accuracy over time (last 20 experiments)
        cursor.execute("""
            SELECT e.run_date, ROUND(e.accuracy, 4) AS accuracy,
                   ROUND(e.loss, 4) AS loss, m.model_name
            FROM Experiments e
            LEFT JOIN Models m ON e.model_id = m.model_id
            ORDER BY e.run_date ASC
            LIMIT 20
        """)
        over_time = cursor.fetchall()
        for row in over_time:
            if row.get("run_date"):
                row["run_date"] = row["run_date"].strftime("%Y-%m-%d %H:%M")

        # Model comparison — avg accuracy and loss per model
        cursor.execute("""
            SELECT m.model_name, m.algorithm,
                   ROUND(AVG(e.accuracy), 4) AS avg_accuracy,
                   ROUND(AVG(e.loss), 4)     AS avg_loss,
                   COUNT(e.experiment_id)    AS run_count
            FROM Experiments e
            JOIN Models m ON e.model_id = m.model_id
            GROUP BY m.model_id, m.model_name, m.algorithm
            ORDER BY avg_accuracy DESC
        """)
        model_comparison = cursor.fetchall()

        return jsonify({
            "over_time": over_time,
            "model_comparison": model_comparison
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()