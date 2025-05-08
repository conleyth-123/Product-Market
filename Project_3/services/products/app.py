import json
import sqlite3
import sys
import requests
from flask import Flask, request, jsonify



app = Flask(__name__)
db_name = "products.db"
sql_file = "products.sql"
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
    cursor.execute("DELETE FROM products")
    conn.commit()
    conn.close()

    return jsonify({"status": 1, "message": "Database cleared"})






@app.route('/create_product', methods=['POST'])
def create_product():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": 2})


        verify_url = "http://user:5000/verify_employee"
        response = requests.get(verify_url, headers={"Authorization": auth_header})
        res_json = response.json()

        if not res_json.get("employee"):
            return jsonify({"status": 2})


        data = request.form.to_dict()
        name = data.get("name")
        price = data.get("price")
        category = data.get("category")

        if not name or not price or not category:
            return jsonify({"status": 2})

        conn = get_db()
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM products WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": 2})

        cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", (name, float(price), category))
        conn.commit()
        conn.close()

        verify_jwt = requests.get("http://user:5000/verify_user", headers={"Authorization": auth_header})
        user_json = verify_jwt.json()
        username = user_json.get("user")

        requests.post("http://logs:5000/log_event", json={"event": "product_creation", "user": username, "name": name})

        return jsonify({"status": 1})

    except:
        return jsonify({"status": 2})





@app.route('/edit_product', methods=['POST'])
def edit_products():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": 2})


        verify_url = "http://user:5000/verify_employee"
        response = requests.get(verify_url, headers={"Authorization": auth_header})
        res_json = response.json()

        if res_json.get("employee") != False and res_json.get("employee") != True:
            return jsonify({"status": 3})

        if not res_json.get("employee"):
            return jsonify({"status": 3})

        data = request.form.to_dict()
        name = data.get("name")
        new_price = data.get("price")
        new_category = data.get("category")

        conn = get_db()
        cursor = conn.cursor()

        if new_price:
            cursor.execute("UPDATE products SET price = ? WHERE name = ?",(new_price, name))

        if new_category:
            cursor.execute("UPDATE products SET category = ? WHERE name = ?",(new_category, name))

        conn.commit()
        conn.close()

        verify_jwt = requests.get("http://user:5000/verify_user", headers={"Authorization": auth_header})
        user_json = verify_jwt.json()
        username = user_json.get("user")

        requests.post("http://logs:5000/log_event", json={"event": "product_edit", "user": username, "name": name})


        return jsonify({"status": 1})

    except:
        return jsonify({"status": 2})



@app.route('/search_by_name', methods=['GET'])
def search_by_name():
    name = request.args.get("product_name")
    if not name:
        return jsonify({"status": 2, "data": "NULL"})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, category FROM products WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        product = {"product_name": row[0], "price": row[1], "category": row[2]}
        return jsonify({"status": 1, "data": [product]})
    else:
        return jsonify({"status": 3, "data": "NULL"})


@app.route('/search_by_category', methods=['GET'])
def search_by_category():
    category = request.args.get("category")
    if not category:
        return jsonify({"status": 2, "data": "NULL"})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, category FROM products WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"status": 3, "data": "NULL"})

    products = []
    for row in rows:
        product = {"product_name": row[0], "price": row[1], "category": row[2]}
        products.append(product)

    return jsonify({"status": 1, "data": products})