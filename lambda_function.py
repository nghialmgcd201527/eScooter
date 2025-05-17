# lambda_function.py
import json
from config import CURRENT_TIMESTAMP, CURRENT_USER, APPLICATION_NAME
from auth import get_leanix_token
from aws_resources import list_resource_names
from leanix_api import get_application_factsheet, create_it_component

def lambda_handler(event, context):
    try:
        # Get AWS resources
        print("Getting AWS resources...")
        resources = list_resource_names()
        
        # Get LeanIX token
        print("Getting LeanIX token...")
        token = get_leanix_token()
        
        # Get Application Fact Sheet ID once
        print(f"Looking up application: {APPLICATION_NAME}")
        app_id = get_application_factsheet(token, APPLICATION_NAME)
        if app_id:
            print(f"Found application ID: {app_id}")
        else:
            print(f"Application not found: {APPLICATION_NAME}")
            raise Exception(f"Application '{APPLICATION_NAME}' not found in LeanIX")
        
        # Create IT Components in LeanIX
        results = []
        print(f"Creating {len(resources)} fact sheets...")
        
        # Process all resources
        for resource in resources:
            try:
                print(f"\nProcessing {resource['service']} resource: {resource['name']}")
                
                # Create IT Component with application relation
                leanix_response = create_it_component(resource, token, app_id)
                
                results.append({
                    'resource': resource,
                    'leanix_status': 'success',
                    'leanix_response': leanix_response,
                    'linked_application': APPLICATION_NAME
                })
            except Exception as e:
                print(f"Error processing {resource['service']} resource {resource['name']}: {str(e)}")
                results.append({
                    'resource': resource,
                    'leanix_status': 'error',
                    'error': str(e),
                    'linked_application': APPLICATION_NAME
                })
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'aws_resources': resources,
                'leanix_results': results,
                'metadata': {
                    'timestamp': CURRENT_TIMESTAMP,
                    'user': CURRENT_USER,
                    'filter': {
                        'tag_key': 'project',
                        'tag_value': 'ABC'
                    },
                    'application': APPLICATION_NAME
                }
            }, indent=2)
        }
        
        return response
        
    except Exception as e:
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'metadata': {
                    'timestamp': CURRENT_TIMESTAMP,
                    'user': CURRENT_USER,
                    'filter': {
                        'tag_key': 'project',
                        'tag_value': 'ABC'
                    },
                    'application': APPLICATION_NAME
                }
            }, indent=2)
        }
        print(f"Error response: {error_response}")
        return error_response