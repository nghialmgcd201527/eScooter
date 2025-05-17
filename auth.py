# auth.py
import requests
import base64
from config import LEANIX_API_BASE_URL, LEANIX_API_TOKEN

def get_leanix_token():
    auth_url = f"{LEANIX_API_BASE_URL}/services/mtm/v1/oauth2/token"
    
    auth_string = f"apitoken:{LEANIX_API_TOKEN}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Error getting token: {str(e)}")
        if hasattr(response, 'text'):
            print(f"Response text: {response.text}")
        raise