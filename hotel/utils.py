# utils.py
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

def get_mpesa_access_token():
    response = requests.get(
        settings.ACCESS_TOKEN_URL,
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
    )
    return response.json().get("access_token")
