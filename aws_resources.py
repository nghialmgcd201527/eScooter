# aws_resources.py
import boto3

def list_resource_names():
    client = boto3.client('resourcegroupstaggingapi')
    paginator = client.get_paginator('get_resources')
    resources = []
    
    try:
        for page in paginator.paginate(
            TagFilters=[
                {
                    'Key': 'project',
                    'Values': ['ABC']
                }
            ]
        ):
            for resource in page['ResourceTagMappingList']:
                arn = resource['ResourceARN']
                arn_parts = arn.split(':')
                
                resource_info = {
                    'service': arn_parts[2],
                    'region': arn_parts[3],
                    'arn': arn
                }
                
                if len(arn_parts) >= 6:
                    resource_name = arn_parts[-1]
                    if '/' in resource_name:
                        resource_name = resource_name.split('/')[-1]
                    resource_info['name'] = resource_name
                
                if 'Tags' in resource:
                    resource_info['tags'] = resource['Tags']
                
                resources.append(resource_info)
                
        print(f"Found {len(resources)} resources with project=ABC tag:")
        for resource in resources:
            print(f"- {resource['service']}: {resource['name']}")
                
        return resources
    except Exception as e:
        print(f"Error listing resources: {str(e)}")
        raise