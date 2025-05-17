# leanix_api/application.py
import requests
from config import LEANIX_API_BASE_URL

def get_application_factsheet(token, app_name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        browse_url = f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/factSheets"
        params = {
            'type': 'Application',
            'name': app_name,
            'pageSize': 1
        }
        
        response = requests.get(browse_url, headers=headers, params=params)
        print(f"Browse API response: {response.text}")
        response.raise_for_status()
        
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            return data['data'][0]['id']
        return None
        
    except Exception as e:
        print(f"Error getting application fact sheet: {str(e)}")
        if hasattr(response, 'text'):
            print(f"Response text: {response.text}")
        raise