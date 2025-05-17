# leanix_api/it_component.py
import requests
import json
import logging
import sys
from config import LEANIX_API_BASE_URL, CURRENT_DATE

# Enhanced logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def create_it_component_factsheet(resource, headers):
    """Create the IT Component fact sheet"""
    logger.debug("=== START create_it_component_factsheet ===")
    
    display_name = f"AWS-{resource['service'].upper()}"
    logger.info(f"Creating fact sheet for {display_name}")
    
    payload = {
        "name": display_name,
        "description": display_name,
        "type": "ITComponent",
        "status": "ACTIVE",
        "fields": [
            {
                "name": "lifecycle",
                "data": {
                    "type": "Lifecycle",
                    "phases": [
                        {
                            "phase": "ACTIVE",
                            "startDate": CURRENT_DATE
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        create_url = f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/factSheets"
        logger.debug(f"Request URL: {create_url}")
        logger.debug(f"Request Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(create_url, headers=headers, json=payload)
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Raw Response Body: {response.text}")
        
        # Check response status
        if response.status_code != 200 and response.status_code != 201:
            logger.error(f"Failed to create IT Component. Status: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            raise Exception(f"Failed to create IT Component. Status: {response.status_code}")
        
        # Parse response
        result = response.json()
        logger.debug(f"Parsed Response: {json.dumps(result, indent=2)}")
        
        # Handle different response structures
        fact_sheet_id = None
        
        if isinstance(result, dict):
            # Try different possible locations for the ID
            if 'id' in result:
                fact_sheet_id = result['id']
            elif 'data' in result and isinstance(result['data'], dict) and 'id' in result['data']:
                fact_sheet_id = result['data']['id']
            elif 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                fact_sheet_id = result['data'][0].get('id')
        
        if not fact_sheet_id:
            # If we still don't have an ID, try to get it by searching for the just-created factsheet
            logger.info("No ID in response, attempting to fetch by name...")
            fact_sheet_id = get_factsheet_id_by_name(display_name, headers)
        
        if not fact_sheet_id:
            logger.error("Failed to get Fact Sheet ID")
            logger.error(f"Full response: {json.dumps(result, indent=2)}")
            raise Exception("No ID received for created IT Component")
        
        # Create result object with confirmed ID
        final_result = {
            'id': fact_sheet_id,
            'name': display_name,
            'type': 'ITComponent',
            'status': 'ACTIVE'
        }
        
        logger.info(f"IT Component created successfully with ID: {fact_sheet_id}")
        logger.debug(f"Final result: {json.dumps(final_result, indent=2)}")
        logger.debug("=== END create_it_component_factsheet ===")
        
        return final_result
        
    except Exception as e:
        logger.error(f"Error creating IT Component: {str(e)}", exc_info=True)
        raise

def get_factsheet_id_by_name(name, headers):
    """Get Fact Sheet ID by searching for the name"""
    try:
        search_url = f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/factSheets"
        params = {
            'name': name,
            'type': 'ITComponent',
            'pageSize': 1
        }
        
        logger.debug(f"Searching for fact sheet with name: {name}")
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data') and len(result['data']) > 0:
                fact_sheet_id = result['data'][0].get('id')
                logger.info(f"Found fact sheet ID: {fact_sheet_id}")
                return fact_sheet_id
        
        logger.warning(f"No fact sheet found with name: {name}")
        return None
        
    except Exception as e:
        logger.error(f"Error searching for fact sheet: {str(e)}")
        return None

def create_it_component_with_relation(resource, token, app_id=None):
    logger.debug("=== START create_it_component_with_relation ===")
    logger.info(f"Creating IT Component for {resource['name']}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Create IT Component
        it_component = create_it_component_factsheet(resource, headers)
        
        # Verify we have an ID
        if not it_component or 'id' not in it_component:
            raise Exception("Failed to create IT Component - no ID received")
        
        logger.info(f"IT Component created with ID: {it_component['id']}")
        
        # Create relation if app_id is provided
        if app_id:
            logger.info(f"Creating relation: IT Component {it_component['id']} -> App {app_id}")
            
            from .relations import create_relation
            try:
                relation_result = create_relation(it_component['id'], app_id, headers)
                logger.info("Relation created successfully")
                logger.debug(f"Relation details: {json.dumps(relation_result, indent=2)}")
                it_component['relation'] = relation_result
            except Exception as e:
                logger.error(f"Failed to create relation: {str(e)}", exc_info=True)
                it_component['relation_error'] = str(e)
        
        logger.debug("=== END create_it_component_with_relation ===")
        return it_component
        
    except Exception as e:
        logger.error(f"Error in create_it_component_with_relation: {str(e)}", exc_info=True)
        raise