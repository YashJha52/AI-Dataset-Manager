import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="ai_dataset_manager"
    )
    return conn