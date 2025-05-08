import sqlite3
import json
import base64
import hashlib
import hmac
import sys
import requests

from flask import Flask, request, jsonify

app = Flask(__name__)
db_name = "user.db"
sql_file = "user.sql"
db_flag = False


def get_key():
    with open("key.txt", "r") as key_file:
        return key_file.read().strip()

key = get_key()


def create_db():
    conn = sqlite3.connect(db_name)

    with open(sql_file, 'r') as sql_startup:
        init_db = sql_startup.read()
    cursor = conn.cursor()
    cursor.executescript(init_db)
    conn.commit()
    conn.close()
    global db_flag
    db_flag = True
    return conn


def get_db():
    if not db_flag:
        create_db()
    conn = sqlite3.connect(db_name)
    return conn


@app.route('/clear', methods=['GET'])
def clearDB():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user")
    conn.commit()
    conn.close()


    return jsonify({"status": 1, "message": "Database cleared"})


def valid_password(password, username, first_name, last_name):
    if len(password) <= 8:
        return False

    has_lower = any(c.islower() for c in password)
    if not has_lower:
        return False

    has_upper = any(c.isupper() for c in password)
    if not has_upper:
        return False

    has_digit = any(c.isdigit() for c in password)
    if not has_digit:
        return False

    if username.lower() in password.lower():
        return False

    if first_name.lower() in password.lower():
        return False

    if last_name.lower() in password.lower():
        return False

    return True





@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        data = request.form.to_dict()

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email_address = data.get('email_address')
        employee = data.get('employee')
        password = data.get('password')
        salt = data.get('salt')

        if not valid_password(password, username, first_name, last_name):
            return jsonify({"status": 4, "pass_hash": "NULL"}), 200

        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM user WHERE username = ?", (username,))
        username_count = cursor.fetchone()[0]
        if username_count > 0:
            return jsonify({"status": 2, "pass_hash": "NULL"}), 200

        cursor.execute("SELECT COUNT(*) FROM user WHERE email_address = ?", (email_address,))
        email_count = cursor.fetchone()[0]
        if email_count > 0:
            return jsonify({"status": 3, "pass_hash": "NULL"}), 200


        cursor.execute("INSERT INTO user (first_name, last_name, username, email_address, employee, password, salt) VALUES (?, ?, ?, ?, ?, ?, ?)",(first_name, last_name, username, email_address, employee, hashed_password, salt))
        conn.commit()
        conn.close()

        requests.post("http://logs:5000/log_event", json={"event": "user_creation", "user": username, "name": "NULL"})

        return jsonify({"status": 1, "pass_hash": hashed_password}), 200

    except:
        return jsonify({"status": 0, "pass_hash": "NUll"}), 200






@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form.to_dict()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"status": 2, "jwt": "NULL"}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"status": 2, "jwt": "NULL"}), 400

        stored_pass = user[5]
        salt = user[6]
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()

        if hashed_password == stored_pass:
            header  = {"alg": "HS256", "typ": "JWT"}
            payload = {"username": username}

            base64_header = base64.b64encode(json.dumps(header).encode('utf-8')).decode('utf-8')
            base64_payload = base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')

            message = f"{base64_header}.{base64_payload}".encode()
            signature = hmac.new(key.encode(), message, hashlib.sha256).hexdigest()

            jwt_token =f"{base64_header}.{base64_payload}.{signature}"

            requests.post("http://logs:5000/log_event", json={"event": "login", "user": username, "name": "NULL"})

            return jsonify({"status": 1, "jwt": jwt_token}), 200

        else:

            return jsonify({"status": 2, "jwt": "NULL"}), 400

    except:
        return jsonify({"status": 2, "jwt": "NULL"}), 400




def base64url_decode(data):
    data += "=" * (-len(data) % 4)
    return base64.b64decode(data)

def decode_jwt(jwt):
    try:
        headerB64, payloadB64, signature = jwt.split('.')

        headerJS = base64url_decode(headerB64).decode('utf-8')
        payloadJS = base64url_decode(payloadB64).decode('utf-8')

        header = json.loads(headerJS)
        payload = json.loads(payloadJS)

        message = f"{headerB64}.{payloadB64}".encode()
        expected_signature = hmac.new(key.encode(), message, hashlib.sha256).hexdigest()

        if expected_signature != signature:
            return None


        return payload

    except:
        return None



@app.route('/verify_employee', methods=['GET'])
def verify_employee():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"employee": False})

    try:
        decoded_jwt = decode_jwt(auth_header)
        if decoded_jwt is None:
            return jsonify({"employee": False})


        username = decoded_jwt.get("username")
        if not username:
            return jsonify({"employee": False})

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT employee FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result[0] == "True":
            return jsonify({"employee": True})
        else:
            return jsonify({"employee": False})

    except:
        return jsonify({"employee": False})



@app.route('/verify_user', methods=['GET'])
def verify_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"user": None})

    try:
        decoded_jwt = decode_jwt(auth_header)
        if decoded_jwt is None:
            return jsonify({"user": None})

        username = decoded_jwt.get("username")
        if not username:
            return jsonify({"user": None})


        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return jsonify({"user": username})
        else:
            return jsonify({"user": None})

    except:
        return jsonify({"user": None})







