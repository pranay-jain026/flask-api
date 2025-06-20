from flask import Flask, request, jsonify
import bcrypt

app = Flask(__name__)

# Temporary in-memory storage (dictionary list)
users = []

@app.route('/')
def index():
    return "Welcome to the Flask API"

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

@app.route('/register', methods=['GET','POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    qualification = data.get('qualification')
    marital_status = data.get('marital_status')
    gender = data.get('gender')
    occupation = data.get('occupation')

    # Basic validation
    if not all([username, email, password]):
        return jsonify({"message": "Username, email, and password are required."}), 400

    # Check for existing user
    for user in users:
        if user['email'] == email:
            return jsonify({"message": "Email already registered"}), 409

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Add user to in-memory list
    users.append({
        "username": username,
        "email": email,
        "password": hashed_password,
        "qualification": qualification,
        "marital_status": marital_status,
        "gender": gender,
        "occupation": occupation
    })

    return jsonify({"message": "User registered successfully", "user": username}), 201

if __name__ == '__main__':
    app.run(debug=True)