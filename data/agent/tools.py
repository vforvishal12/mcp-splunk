import requests

def get_logs():
    return requests.get("http://localhost:9000/search_logs").json()["logs"]

def get_health():
    return requests.get("http://localhost:9000/service_health").json()