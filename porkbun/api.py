import requests
from porkbun.config import API_KEY, SECRET_API_KEY

BASE_URL = "https://porkbun.com/api/json/v3"

def make_request(endpoint, data):
    data.update({
        "apikey": API_KEY,
        "secretapikey": SECRET_API_KEY
    })
    response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
    return response.json()
