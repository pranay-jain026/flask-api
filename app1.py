from flask import Flask, request, jsonify
import bcrypt
import pyodbc
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=208.91.198.196;'
        'DATABASE=positd2y_pranay;'
        'UID=sa_pranay_gpe;'
        'PWD=Vbsd62?26@Positron'
    )
    return conn

# Auto-create users table if not exists
def create_users_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'users'
            )
            BEGIN
                CREATE TABLE users (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    username VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(255),
                    qualification VARCHAR(100),
                    marital_status VARCHAR(50),
                    gender VARCHAR(20),
                    occupation VARCHAR(100)
                )
            END
        """)
        conn.commit()
        conn.close()
        print("✅ Users table checked/created.")
    except Exception as e:
        print("❌ Error creating table:", e)

@app.route('/')
def index():
    return "Welcome to the Flask API with SQL Server"

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, qualification, marital_status, gender, occupation FROM users")
        users = cursor.fetchall()
        conn.close()

        user_list = []
        for u in users:
            user_list.append({
                "username": u[0],
                "email": u[1],
                "qualification": u[2],
                "marital_status": u[3],
                "gender": u[4],
                "occupation": u[5]
            })

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        qualification = data.get('qualification')
        marital_status = data.get('marital_status')
        gender = data.get('gender')
        occupation = data.get('occupation')

        if not all([username, email, password]):
            return jsonify({"message": "Username, email, and password are required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email already registered"}), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute("""
            INSERT INTO users (username, email, password, qualification, marital_status, gender, occupation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, hashed_password, qualification, marital_status, gender, occupation))

        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully", "user": username}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    create_users_table()  # Auto-create table on startup
    app.run(debug=True, port=5001)
