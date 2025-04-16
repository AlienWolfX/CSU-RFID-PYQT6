import os
import psycopg2
from dotenv import load_dotenv

def insert_admin_user():
    """Insert an admin user into the users table"""
    
    
    load_dotenv()
    
    try:
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD")
        )
        
        
        cur = conn.cursor()
        
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role_id INTEGER NOT NULL DEFAULT 2
            )
        """)
        
        
        cur.execute("""
            INSERT INTO users (username, password, role_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING user_id
        """, ('admin', 'admin123', 1))
        
        
        result = cur.fetchone()
        
        
        conn.commit()
        
        if result:
            print("Admin user created successfully!")
            print(f"User ID: {result[0]}")
        else:
            print("Admin user already exists or insertion failed")
            
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    insert_admin_user()