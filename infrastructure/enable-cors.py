"""
Enable CORS on API Gateway endpoints
"""
import boto3
import json

client = boto3.client('apigateway', region_name='us-east-1')
API_ID = 'fjr24hbqvb'

# Resources to configure
resources = [
    {'path': '/upload', 'id': 'm17kxe', 'methods': ['POST', 'OPTIONS']},
    {'path': '/images', 'id': 'ye8t2t', 'methods': ['GET', 'OPTIONS']},
    {'path': '/images/search', 'id': 'p9s8z1', 'methods': ['GET', 'OPTIONS']},
    {'path': '/images/{imageId}', 'id': 'hhcp8n', 'methods': ['DELETE', 'OPTIONS']}
]

def enable_cors(resource_id, resource_path):
    """Enable CORS for a resource"""
    print(f"\n=== Configuring CORS for {resource_path} ===")
    
    # Step 1: Create OPTIONS method
    try:
        client.put_method(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        print("✓ OPTIONS method created")
    except client.exceptions.ConflictException:
        print("✓ OPTIONS method already exists")
    
    # Step 2: Add MOCK integration
    try:
        client.put_integration(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        print("✓ MOCK integration added")
    except Exception as e:
        print(f"! Integration: {e}")
    
    # Step 3: Create method response
    try:
        client.put_method_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
        print("✓ Method response created")
    except client.exceptions.ConflictException:
        print("✓ Method response already exists")
    
    # Step 4: Create integration response with CORS headers
    try:
        client.put_integration_response(
            restApiId=API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,DELETE,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        print("✓ Integration response with CORS headers added")
    except Exception as e:
        print(f"! Integration response: {e}")

# Configure CORS for all resources
for resource in resources:
    enable_cors(resource['id'], resource['path'])

# Deploy the API
print("\n=== Deploying API ===")
try:
    deployment = client.create_deployment(
        restApiId=API_ID,
        stageName='prod',
        description='CORS configuration'
    )
    print(f"✓ API deployed (deployment ID: {deployment['id']})")
    print(f"\n✅ API URL: https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod")
except Exception as e:
    print(f"✗ Deployment failed: {e}")
