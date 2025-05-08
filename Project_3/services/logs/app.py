import sqlite3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
db_name = "logs.db"
sql_file = "logs.sql"
db_flag = False

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
    cursor.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

    return jsonify({"status": 1, "message": "Database cleared"})


@app.route('/log_event', methods=['POST'])
def log_event():
    data = request.json
    event = data.get("event")
    username = data.get("user")
    name = data.get("name", "NULL")

    if not event or not username:
        return jsonify({"status": 2})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (event, username, name) VALUES (?, ?, ?)", (event, username, name))
    conn.commit()
    conn.close()

    return jsonify({"status": 1})




@app.route('/view_log', methods=['GET'])
def view_log():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"status": 2, "data": "NULL"})

    try:
        verify_url = "http://user:5000/verify_user"
        response = requests.get(verify_url, headers={"Authorization": auth_header})
        res_json = response.json()

        if not res_json.get("user"):
            return jsonify({"status": 2, "data": "NULL"})
    except:
        return jsonify({"status": 2, "data": "NULL"})


    user_request = res_json.get("user")

    verify_url = "http://user:5000/verify_employee"
    response = requests.get(verify_url, headers={"Authorization": auth_header})
    res_json = response.json()
    is_employee = res_json.get("employee", False)

    username = request.args.get("username")
    product = request.args.get("product")

    conn = get_db()
    cursor = conn.cursor()

    if username:
        if username != user_request and not is_employee:
            return jsonify({"status": 3, "data": "NULL"})

        cursor.execute("SELECT event, username, name FROM logs WHERE username = ?", (username,))
    elif product:
        if not is_employee:
            return jsonify({"status": 3, "data": "NULL"})

        cursor.execute("SELECT event, username, name FROM logs WHERE name = ?", (product,))
    else:
        return jsonify({"status": 2, "data": "NULL"})

    logs = cursor.fetchall()
    conn.close()


    data = {}
    i = 1
    for event, user, name in logs:
        data[str(i)] = {"event": event, "name": name, "user": user}
        i += 1

    return jsonify({"status": 1, "data": data})


@app.route('/last_modifier', methods=['GET'])
def last_modifier():
    product_name = request.args.get("product_name")
    if not product_name:
        return jsonify({"status": 2, "last_mod": "NULL"})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM logs WHERE name = ? AND event IN ('product_creation', 'product_edit') ORDER BY ROWID DESC LIMIT 1",(product_name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"status": 1, "last_mod": row[0]})
    return jsonify({"status": 3, "last_mod": "NULL"})

