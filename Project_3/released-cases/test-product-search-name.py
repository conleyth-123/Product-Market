import requests
import json
import os

try:
	
	URLCREATEUSER = "http://127.0.0.1:9000/create_user"
	URLLOGIN = "http://127.0.0.1:9000/login"
	URLPRODUCTCREATE = "http://127.0.0.1:9001/create_product"
	URLPRODUCTEDIT = "http://127.0.0.1:9001/edit_product"
	URLSEARCH = "http://127.0.0.1:9002/search"
	URLORDER = "http://127.0.0.1:9003/order"
	URLLOG = "http://127.0.0.1:9004/view_log"

	URLUSERclear = "http://127.0.0.1:9000/clear"
	URLPRODUCTclear = "http://127.0.0.1:9001/clear"
	URLSEARCHclear = "http://127.0.0.1:9002/clear"
	URLORDERclear = "http://127.0.0.1:9003/clear"
	URLLOGclear = "http://127.0.0.1:9004/clear"
	r_clear = requests.get(url = URLUSERclear)
	r_clear = requests.get(url = URLPRODUCTclear)
	r_clear = requests.get(url = URLSEARCHclear)
	r_clear = requests.get(url = URLORDERclear)
	r_clear = requests.get(url = URLLOGclear)


	PARAMS = {'first_name': 'james', 'last_name': 'mariani', 'username': 'jmm', 'email_address': 'j@a.com', 'password': 'Examplepassword1', 'employee': True, 'salt': 'FE8x1gO+7z0B'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		quit()
	

	PARAMS = {'first_name': 'griffin', 'last_name': 'klevering', 'username': 'griff', 'email_address': 'g@g.com', 'password': 'Examplepassword1', 'employee': False, 'salt': 'xaxkRSzNPnP4'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		quit()

	LOGINPARAMS = {'username': 'jmm', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	if login_data['status'] != 1:
			quit()
	
	LOGINPARAMS = {'username': 'griff', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	if login_data['status'] != 1:
			quit()

	CREATEPRODUCTPARAMS = {'name': 'butter', 'price': 3.99, 'category': 'dairy'}
	r_create_product = requests.post(url = URLPRODUCTCREATE, data = CREATEPRODUCTPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_product_data = r_create_product.json()

	if create_product_data['status'] != 1:
		quit()

	SEARCHPARAMS = {'product_name': 'butter'}
	r_search = requests.get(url = URLSEARCH, params = SEARCHPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	search_data = r_search.json()
	expected_dict = {'status': 1, 'data': [{'product_name': 'butter', 'price': 3.99, 'category': 'dairy', 'last_mod': 'jmm'}]}

	if len(expected_dict['data']) != len(search_data['data']):
		quit()
	for x in expected_dict['data']:
		found = False
		for y in search_data['data']:
			if (y['product_name'] == x['product_name']) and (y['price'] == x['price']) and (y['category'] == x['category']) and (y['last_mod'] == x['last_mod']):
				found = True
				break
		if not found:
			quit()

	print('Test Passed')

except:
	print('Test Failed')

