# leanix_api/relations.py
import requests
import json
import logging
import sys
from datetime import datetime
from config import (
    LEANIX_API_BASE_URL, 
    APPLICATION_NAME, 
    CURRENT_DATE, 
    CURRENT_DATETIME
)

# Enhanced logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with a higher log level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

def create_relation(it_component_id, app_id, headers):
    """Create a relation between IT Component and Application"""
    logger.debug(f"=== START create_relation ===")
    logger.info(f"Creating relation: IT Component {it_component_id} -> Application {app_id}")
    
    try:
        relation_payload = {
            "fromId": it_component_id,
            "toId": app_id,
            "type": "relITComponentToApplication",
            "displayNameToFS": APPLICATION_NAME,
            "typeFromFS": "ITComponent",
            "typeToFS": "Application",
            "status": "ACTIVE",
            "activeFrom": datetime.utcnow().strftime("%Y-%m-%d"),
            "fields": [],
            "permittedReadACL": [],
            "constrainingRelations": [],
            "idsOfConstrainingRelations": []
        }
        
        logger.debug(f"Relation payload: {json.dumps(relation_payload, indent=2)}")
        
        # First try - standard relation endpoint
        relation_url = f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/relations"
        logger.info(f"Attempting to create relation using URL: {relation_url}")
        
        response = requests.post(relation_url, headers=headers, json=relation_payload)
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")
        
        if response.status_code != 200:
            # Second try - factSheet relations endpoint
            relation_url = f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/factSheets/{it_component_id}/relations"
            logger.info(f"Second attempt using URL: {relation_url}")
            
            response = requests.post(relation_url, headers=headers, json=relation_payload)
            logger.debug(f"Second Response Status: {response.status_code}")
            logger.debug(f"Second Response Body: {response.text}")
        
        response.raise_for_status()
        
        # Verify relation was created
        is_verified = verify_relation(it_component_id, app_id, headers)
        if is_verified:
            logger.info("Relation created and verified successfully")
        else:
            logger.warning("Relation created but verification failed")
            
        logger.debug("=== END create_relation ===")
        return response.json()
        
    except Exception as e:
        logger.error(f"Error creating relation: {str(e)}", exc_info=True)
        raise

def verify_relation(it_component_id, app_id, headers):
    """Verify that the relation exists"""
    logger.debug(f"=== START verify_relation ===")
    logger.info(f"Verifying relation between {it_component_id} and {app_id}")
    
    try:
        # Try both directions
        urls = [
            f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/factSheets/{it_component_id}/relations",
            f"{LEANIX_API_BASE_URL}/services/pathfinder/v1/factSheets/{app_id}/relations"
        ]
        
        for url in urls:
            logger.debug(f"Checking relations using URL: {url}")
            response = requests.get(url, headers=headers)
            logger.debug(f"Verification Response Status: {response.status_code}")
            logger.debug(f"Verification Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                relations = data.get('data', [])
                
                for relation in relations:
                    if (relation.get('fromId') == it_component_id and relation.get('toId') == app_id) or \
                       (relation.get('fromId') == app_id and relation.get('toId') == it_component_id):
                        logger.info(f"Found relation: {json.dumps(relation, indent=2)}")
                        logger.debug("=== END verify_relation ===")
                        return True
        
        logger.warning("No relation found")
        logger.debug("=== END verify_relation ===")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying relation: {str(e)}", exc_info=True)
        return False