from utils.db import create_connection
from mysql.connector import Error
import bcrypt

def create_table():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(60) NOT NULL,
                role VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Users table created or already exists.")
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            cursor.close()
            connection.close()

def register_user():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    role = input("Enter the role (e.g., user, admin): ")

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Hash password with bcrypt
            salt = bcrypt.gensalt(rounds=12)
            hashed_password = bcrypt.hashpw(password.encode(), salt)
            
            insert_user_query = """
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s);
            """
            cursor.execute(insert_user_query, (username, hashed_password, role))
            connection.commit()
            print(f"User '{username}' registered successfully.")
        except Error as e:
            print(f"Error registering user: {e}")
        finally:
            cursor.close()
            connection.close()

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

if __name__ == "__main__":
    create_table()
    register_user()