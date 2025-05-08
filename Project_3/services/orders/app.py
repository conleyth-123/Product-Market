
import json
import sys

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/clear', methods=['GET'])
def clearDB():
    return jsonify({"status": 1, "message": "Database cleared"})


@app.route('/order', methods=['POST'])
def order():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"status": 2, "cost": "NULL"})

    verify_url = "http://user:5000/verify_user"
    response = requests.get(verify_url, headers={"Authorization": auth_header})
    res_json = response.json()

    if not res_json.get("user"):
        return jsonify({"status": 2, "cost": "NULL"})

    username = res_json.get("user")

    data = request.form.to_dict()
    orders = data.get("order")
    orders = json.loads(orders)

    cost = 0
    for order in orders:
        verify_url = f"http://products:5000/search_by_name?product_name={order.get("product")}"
        response = requests.get(verify_url)
        res_json = response.json()
        if not res_json.get("data"):
            return jsonify({"status": 3, "cost": "NULL"})

        quantity = order.get("quantity")

        price = res_json.get("data")[0].get("price")

        cost += price * quantity


    cost = "{:.2f}".format(cost)

    requests.post("http://logs:5000/log_event", json={"event": "order", "user": username, "name": "NULL"})


    return jsonify({"status": 1, "cost": cost})






