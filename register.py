import tkinter as tk
from tkinter import ttk, messagebox
from utils.db import create_connection
from mysql.connector import Error
import bcrypt

class RegisterForm:
    def __init__(self, root):
        self.root = root
        self.root.title("User Registration")
        self.root.geometry("300x250")
        
        # Create form fields
        tk.Label(root, text="Username:").pack(pady=5)
        self.username = tk.Entry(root)
        self.username.pack(pady=5)
        
        tk.Label(root, text="Password:").pack(pady=5)
        self.password = tk.Entry(root, show="*")
        self.password.pack(pady=5)
        
        tk.Label(root, text="Role:").pack(pady=5)
        self.role = ttk.Combobox(root, values=["user", "admin"])
        self.role.set("user")
        self.role.pack(pady=5)
        
        # Register button
        tk.Button(root, text="Register", command=self.register_user).pack(pady=20)

    def register_user(self):
        username = self.username.get()
        password = self.password.get()
        role = self.role.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                salt = bcrypt.gensalt(rounds=12)
                hashed_password = bcrypt.hashpw(password.encode(), salt)
                
                insert_user_query = """
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s);
                """
                cursor.execute(insert_user_query, (username, hashed_password, role))
                connection.commit()
                messagebox.showinfo("Success", f"User '{username}' registered successfully.")
                self.username.delete(0, tk.END)
                self.password.delete(0, tk.END)
                self.role.set("user")
            except Error as e:
                messagebox.showerror("Error", f"Error registering user: {e}")
            finally:
                cursor.close()
                connection.close()

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

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

if __name__ == "__main__":
    create_table()
    root = tk.Tk()
    app = RegisterForm(root)
    root.mainloop()