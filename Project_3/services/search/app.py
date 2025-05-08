
import sys
import requests

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/clear', methods=['GET'])
def clearDB():
    return jsonify({"status": 1, "message": "Database cleared"})



@app.route('/search', methods=['GET'])
def search():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"status": 2, "data": "NULL"})

    verify_url = "http://user:5000/verify_user"
    response = requests.get(verify_url, headers={"Authorization": auth_header})
    res_json = response.json()

    if not res_json.get("user"):
        return jsonify({"status": 2, "data": "NULL"})
    username = res_json.get("user")

    name = request.args.get("product_name")
    category = request.args.get("category")

    if name:
        verify_url = f"http://products:5000/search_by_name?product_name={name}"
        response = requests.get(verify_url)
        res_json = response.json()
    elif category:
        verify_url = f"http://products:5000/search_by_category?category={category}"
        response = requests.get(verify_url)
        res_json = response.json()

    if res_json.get("status") != 1:
        return jsonify({"status": 3, "data": "NULL"})

    products = res_json.get("data")

    LastMod = []
    for product in products:
        product_name = product.get("product_name")

        response = requests.get(f"http://logs:5000/last_modifier?product_name={product_name}")
        res_json = response.json()
        last_mod = res_json.get("last_mod")

        product["last_mod"] = last_mod
        LastMod.append(product)

    if name:
        requests.post("http://logs:5000/log_event", json={"event": "search", "user": username, "name": name})
    elif category:
        requests.post("http://logs:5000/log_event", json={"event": "search", "user": username, "category": category})

    return jsonify({"status": 1, "data": LastMod})










