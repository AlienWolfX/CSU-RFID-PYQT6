# db_connection.py

import mysql.connector
from mysql.connector import Error

def create_connection():
    """Establish connection to the database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',  # XAMPP runs locally
            user='root',       # Default XAMPP username
            password='',       # Default XAMPP password (leave blank if not set)
            database='vehicle_monitoring'  # Replace with your database name
        )
        if connection.is_connected():
            print("Connected to the database.")
        return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None