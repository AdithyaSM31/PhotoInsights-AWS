"""
Lambda Function: GetImages
Purpose: Retrieve user's photo gallery with metadata
Trigger: API Gateway (GET /images)
Runtime: Python 3.11
"""

import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'PhotoGallery-Images')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'photogallery-processed-23brs1079')
CLOUDFRONT_DOMAIN = os.environ.get('CLOUDFRONT_DOMAIN', '')  # Will add later

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

# S3 client for generating URLs
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Expected input (from API Gateway):
    {
        "queryStringParameters": {
            "limit": "20",
            "sortOrder": "desc",
            "lastKey": "{encoded_key}"
        },
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "user-id-from-cognito"
                }
            }
        }
    }
    """
    
    try:
        # Get user ID from Cognito JWT token
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Parse query parameters
        params = event.get('queryStringParameters') or {}
        limit = int(params.get('limit', '20'))
        sort_order = params.get('sortOrder', 'desc').lower()
        last_key = params.get('lastKey')
        
        # Limit validation
        if limit > 100:
            limit = 100  # Maximum 100 items per request
        if limit < 1:
            limit = 20
        
        # Query DynamoDB using GSI (UploadTimeIndex) for sorting by upload time
        query_params = {
            'IndexName': 'UploadTimeIndex',
            'KeyConditionExpression': Key('userId').eq(user_id),
            'Limit': limit,
            'ScanIndexForward': (sort_order == 'asc')  # False = descending (newest first)
        }
        
        # Handle pagination
        if last_key:
            try:
                query_params['ExclusiveStartKey'] = json.loads(last_key)
            except:
                pass  # Invalid lastKey, ignore
        
        # Execute query
        response = table.query(**query_params)
        
        # Build image list with URLs
        images = []
        for item in response.get('Items', []):
            image_data = build_image_response(item, user_id)
            images.append(image_data)
        
        # Prepare response
        result = {
            'images': images,
            'count': len(images),
            'userId': user_id
        }
        
        # Add pagination token if there are more results
        if 'LastEvaluatedKey' in response:
            result['nextKey'] = json.dumps(response['LastEvaluatedKey'], cls=DecimalEncoder)
            result['hasMore'] = True
        else:
            result['hasMore'] = False
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(result, cls=DecimalEncoder)
        }
        
    except KeyError as e:
        return error_response(401, f'Unauthorized: Missing {str(e)}')
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(500, f'Internal server error: {str(e)}')


def build_image_response(item, user_id):
    """
    Build image response object with URLs
    """
    image_id = item['imageId']
    
    # Use CloudFront if configured, otherwise generate S3 URLs
    if CLOUDFRONT_DOMAIN:
        base_url = f"https://{CLOUDFRONT_DOMAIN}"
    else:
        base_url = f"https://{PROCESSED_BUCKET}.s3.amazonaws.com"
    
    # Build image object
    image_data = {
        'imageId': image_id,
        'imageName': item.get('imageName', 'unknown'),
        'uploadTimestamp': int(item.get('uploadTimestamp', 0)),
        'fileSize': int(item.get('fileSize', 0)),
        'width': int(item.get('width', 0)),
        'height': int(item.get('height', 0)),
        'urls': {
            'thumbnail': f"{base_url}/processed/{user_id}/thumb-{image_id}.jpg",
            'medium': f"{base_url}/processed/{user_id}/med-{image_id}.jpg",
            'large': f"{base_url}/processed/{user_id}/{image_id}.webp",
            'original': f"{base_url}/uploads/{user_id}/{image_id}-{item.get('imageName', 'image.jpg')}"
        }
    }
    
    # Add optional fields if they exist
    if 'tags' in item:
        image_data['tags'] = item['tags']
    
    if 'aiAnalysis' in item:
        ai_analysis = item['aiAnalysis']
        image_data['aiAnalysis'] = {
            'faceCount': int(ai_analysis.get('faceCount', 0)),
            'hasText': bool(ai_analysis.get('detectedText', [])),
            'moderationFlags': ai_analysis.get('moderationFlags', [])
        }
    
    if 'processingStatus' in item:
        image_data['processingStatus'] = item['processingStatus']
    
    return image_data


def get_cors_headers():
    """
    Return CORS headers for API response
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }


def error_response(status_code, message):
    """
    Generate standardized error response
    """
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'error': message
        })
    }


class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to convert DynamoDB Decimal types to JSON
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


# For local testing
if __name__ == '__main__':
    # Test event
    test_event = {
        'queryStringParameters': {
            'limit': '10',
            'sortOrder': 'desc'
        },
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-123'
                }
            }
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
