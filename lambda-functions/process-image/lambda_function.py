"""
Lambda Function: ProcessImage (Simplified - No Pillow)
Purpose: Copy uploaded images and create metadata (without resizing)
Trigger: S3 event when image is uploaded to uploads bucket
"""

import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

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
    Process uploaded images: copy to processed bucket and create metadata.
    Simplified version without image resizing.
    """
    
    try:
        # Parse S3 event
        for record in event['Records']:
            # Get bucket and key from event
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            print(f"Processing: s3://{bucket}/{key}")
            
            # Skip if not in uploads folder
            if not key.startswith('uploads/'):
                print(f"Skipping non-upload file: {key}")
                continue
            
            # Parse key: uploads/{userId}/{imageId}-{timestamp}-{filename}
            parts = key.split('/')
            if len(parts) < 3:
                print(f"Invalid key format: {key}")
                continue
            
            user_id = parts[1]
            filename_parts = parts[2].split('-', 2)  # Split only first 2 dashes
            
            if len(filename_parts) < 3:
                print(f"Invalid filename format: {parts[2]}")
                continue
            
            image_id = filename_parts[0]
            timestamp_str = filename_parts[1]
            original_filename = filename_parts[2]
            
            # Get object metadata
            head_response = s3.head_object(Bucket=bucket, Key=key)
            file_size = head_response['ContentLength']
            content_type = head_response.get('ContentType', 'application/octet-stream')
            
            # Copy original to processed bucket (as "large" version)
            processed_key = f"processed/{user_id}/{image_id}.jpg"
            s3.copy_object(
                CopySource={'Bucket': bucket, 'Key': key},
                Bucket=PROCESSED_BUCKET,
                Key=processed_key,
                ContentType=content_type
            )
            print(f"Copied to: s3://{PROCESSED_BUCKET}/{processed_key}")
            
            # Create thumbnail and medium versions (just copies for now)
            thumb_key = f"processed/{user_id}/thumb-{image_id}.jpg"
            s3.copy_object(
                CopySource={'Bucket': bucket, 'Key': key},
                Bucket=PROCESSED_BUCKET,
                Key=thumb_key,
                ContentType=content_type
            )
            
            med_key = f"processed/{user_id}/med-{image_id}.jpg"
            s3.copy_object(
                CopySource={'Bucket': bucket, 'Key': key},
                Bucket=PROCESSED_BUCKET,
                Key=med_key,
                ContentType=content_type
            )
            
            # Create DynamoDB entry
            upload_timestamp = int(datetime.now().timestamp())
            
            item = {
                'imageId': image_id,
                'userId': user_id,
                'imageName': original_filename,
                'uploadTimestamp': upload_timestamp,
                'fileSize': file_size,
                'width': 1920,  # Placeholder
                'height': 1080,  # Placeholder
                'processingStatus': 'completed',
                'originalKey': key,
                'processedKey': processed_key,
                'thumbnailKey': thumb_key,
                'mediumKey': med_key
            }
            
            # Write to DynamoDB
            table.put_item(Item=item)
            print(f"Created DynamoDB entry for imageId: {image_id}")
            
            # Trigger AnalyzeImage Lambda (async)
            lambda_client = boto3.client('lambda')
            analyze_payload = {
                'imageId': image_id,
                'userId': user_id,
                'bucket': PROCESSED_BUCKET,
                'key': processed_key
            }
            
            try:
                lambda_client.invoke(
                    FunctionName='PhotoGallery-AnalyzeImage',
                    InvocationType='Event',  # Async
                    Payload=json.dumps(analyze_payload)
                )
                print(f"Triggered AnalyzeImage for imageId: {image_id}")
            except Exception as e:
                print(f"Failed to trigger AnalyzeImage: {e}")
            
        return {
            'statusCode': 200,
            'body': json.dumps('Processing completed successfully')
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

# For local testing
if __name__ == '__main__':
    # Test event
    test_event = {
        'Records': [
            {
                's3': {
                    'bucket': {'name': 'photogallery-uploads-23brs1079'},
                    'object': {
                        'key': 'uploads/test-user/test-image-20231104-photo.jpg',
                        'size': 1024000
                    }
                }
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
