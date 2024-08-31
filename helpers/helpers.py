#! .venv/bin/python

import requests

def get_client_location(ip_address=None):
    url = f"https://ipapi.co/{ip_address}/json/" if ip_address else "https://ipapi.co/json/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None