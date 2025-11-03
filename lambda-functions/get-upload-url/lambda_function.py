"""
Lambda Function: GetUploadUrl
Purpose: Generate pre-signed S3 URLs for direct browser uploads
Trigger: API Gateway (POST /upload)
Runtime: Python 3.11
"""

import json
import boto3
import uuid
import os
from datetime import datetime

# Environment variables
UPLOADS_BUCKET = os.environ.get('UPLOADS_BUCKET', 'photogallery-uploads-23brs1079')

# Initialize S3 client (region is automatically detected in Lambda)
s3_client = boto3.client('s3')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Expected input (from API Gateway):
    {
        "body": {
            "filename": "sunset.jpg",
            "contentType": "image/jpeg",
            "fileSize": 2458624
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
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extract user ID from Cognito JWT token (via API Gateway authorizer)
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Validate input
        filename = body.get('filename')
        content_type = body.get('contentType', 'image/jpeg')
        file_size = body.get('fileSize', 0)
        
        if not filename:
            return error_response(400, 'Filename is required')
        
        # Validate file extension
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            return error_response(400, f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}')
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            return error_response(400, f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB')
        
        # Generate unique image ID
        image_id = str(uuid.uuid4())
        
        # Create S3 key (path)
        # Format: uploads/{userId}/{imageId}-{filename}
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        s3_key = f"uploads/{user_id}/{image_id}-{timestamp}-{filename}"
        
        # Generate pre-signed URL for PUT operation
        # Valid for 5 minutes (300 seconds)
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': UPLOADS_BUCKET,
                'Key': s3_key,
                'ContentType': content_type,
            },
            ExpiresIn=300,  # 5 minutes
            HttpMethod='PUT'
        )
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # CORS
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'imageId': image_id,
                'key': s3_key,
                'bucket': UPLOADS_BUCKET,
                'expiresIn': 300,
                'message': 'Upload URL generated successfully'
            })
        }
        
    except KeyError as e:
        return error_response(401, f'Unauthorized: Missing {str(e)}')
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def error_response(status_code, message):
    """
    Generate standardized error response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'error': message
        })
    }


# For local testing
if __name__ == '__main__':
    # Test event (simulates API Gateway request with Cognito authorizer)
    test_event = {
        'body': json.dumps({
            'filename': 'test-image.jpg',
            'contentType': 'image/jpeg',
            'fileSize': 2048576
        }),
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
