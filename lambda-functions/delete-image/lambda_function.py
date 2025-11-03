"""
Lambda Function: DeleteImage
Purpose: Delete an image and all its versions from S3 and DynamoDB
Trigger: API Gateway DELETE /images/{imageId}
"""

import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
UPLOADS_BUCKET = os.environ.get('UPLOADS_BUCKET', 'photogallery-uploads-23brs1079')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'photogallery-processed-23brs1079')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'PhotoGallery-Images')

table = dynamodb.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    Delete an image from S3 buckets and DynamoDB.
    
    API Gateway Event Structure:
    {
        "pathParameters": {"imageId": "uuid"},
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "user-id"}
            }
        }
    }
    """
    
    try:
        # Extract user ID from Cognito JWT claims
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Extract image ID from path parameters
        image_id = event['pathParameters']['imageId']
        
        print(f"Delete request - UserId: {user_id}, ImageId: {image_id}")
        
        # Step 1: Get image metadata from DynamoDB
        image_metadata = get_image_metadata(user_id, image_id)
        
        if not image_metadata:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Image not found',
                    'message': f'Image {image_id} does not exist or does not belong to user'
                })
            }
        
        # Step 2: Delete from S3 buckets
        delete_from_s3(user_id, image_id, image_metadata)
        
        # Step 3: Delete from DynamoDB
        delete_from_dynamodb(user_id, image_id)
        
        print(f"Successfully deleted image {image_id} for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Image deleted successfully',
                'imageId': image_id,
                'deletedFiles': {
                    'original': True,
                    'processed': True,
                    'metadata': True
                }
            })
        }
        
    except KeyError as e:
        print(f"Missing required field: {str(e)}")
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Bad Request',
                'message': f'Missing required field: {str(e)}'
            })
        }
    
    except ClientError as e:
        print(f"AWS error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'Failed to delete image'
            })
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }


def get_image_metadata(user_id, image_id):
    """
    Retrieve image metadata from DynamoDB to verify ownership.
    
    Returns:
        dict: Image metadata if found, None otherwise
    """
    try:
        response = table.get_item(
            Key={
                'userId': user_id,
                'imageId': image_id
            }
        )
        
        return response.get('Item')
        
    except ClientError as e:
        print(f"Error getting image metadata: {str(e)}")
        return None


def delete_from_s3(user_id, image_id, metadata):
    """
    Delete image files from S3 buckets.
    Deletes original from uploads bucket and all processed versions.
    
    Args:
        user_id (str): User ID
        image_id (str): Image ID
        metadata (dict): Image metadata containing file info
    """
    
    # Get original filename from metadata
    original_filename = metadata.get('imageName', '')
    timestamp = metadata.get('uploadTimestamp', '')
    
    # Construct S3 keys
    # Original file in uploads bucket
    original_key = f"uploads/{user_id}/{image_id}-{timestamp}-{original_filename}"
    
    # Processed files in processed bucket
    processed_keys = [
        f"processed/{user_id}/thumb-{image_id}.jpg",      # Thumbnail 150x150
        f"processed/{user_id}/med-{image_id}.jpg",        # Medium 800x800
        f"processed/{user_id}/{image_id}.webp"            # Large WebP
    ]
    
    # Delete original from uploads bucket
    try:
        print(f"Deleting original: {original_key}")
        s3.delete_object(
            Bucket=UPLOADS_BUCKET,
            Key=original_key
        )
        print(f"Deleted original from {UPLOADS_BUCKET}")
    except ClientError as e:
        print(f"Error deleting original from S3: {str(e)}")
        # Continue even if original file doesn't exist
    
    # Delete processed versions from processed bucket
    for key in processed_keys:
        try:
            print(f"Deleting processed: {key}")
            s3.delete_object(
                Bucket=PROCESSED_BUCKET,
                Key=key
            )
        except ClientError as e:
            print(f"Error deleting {key}: {str(e)}")
            # Continue deleting other files even if one fails
    
    print(f"Deleted all S3 files for image {image_id}")


def delete_from_dynamodb(user_id, image_id):
    """
    Delete image metadata from DynamoDB.
    
    Args:
        user_id (str): User ID
        image_id (str): Image ID
    """
    try:
        table.delete_item(
            Key={
                'userId': user_id,
                'imageId': image_id
            }
        )
        print(f"Deleted metadata from DynamoDB for image {image_id}")
        
    except ClientError as e:
        print(f"Error deleting from DynamoDB: {str(e)}")
        raise


def get_cors_headers():
    """Return CORS headers for API Gateway responses."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'DELETE,OPTIONS'
    }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "pathParameters": {
            "imageId": "test-image-123"
        },
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "test-user-123"
                }
            }
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
