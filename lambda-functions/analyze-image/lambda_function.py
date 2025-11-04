"""
Lambda Function: AnalyzeImage
Purpose: Use Amazon Rekognition to analyze images and extract AI-generated tags
Trigger: DynamoDB Stream or invoked by ProcessImage Lambda
"""

import json
import os
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError

# Initialize AWS clients
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'photogallery-processed-23brs1079')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'PhotoGallery-Images')
MAX_LABELS = int(os.environ.get('MAX_LABELS', '10'))
MIN_CONFIDENCE = float(os.environ.get('MIN_CONFIDENCE', '80'))

table = dynamodb.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    Analyze image using Amazon Rekognition and update DynamoDB with tags.
    
    Can be triggered by:
    1. Direct invocation with imageId and userId
    2. DynamoDB Stream event
    3. API Gateway request
    """
    
    try:
        # Parse event based on source
        if 'Records' in event and event['Records'][0].get('eventSource') == 'aws:dynamodb':
            # DynamoDB Stream trigger
            return handle_dynamodb_stream(event)
        else:
            # Direct invocation or API Gateway
            return handle_direct_invocation(event, context)
            
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }


def handle_direct_invocation(event, context):
    """
    Handle direct Lambda invocation.
    
    Expected event:
    {
        "imageId": "uuid",
        "userId": "user-id",
        "bucket": "bucket-name" (optional)
    }
    """
    
    # Extract parameters
    image_id = event.get('imageId')
    user_id = event.get('userId')
    bucket = event.get('bucket', PROCESSED_BUCKET)
    
    if not image_id or not user_id:
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Bad Request',
                'message': 'imageId and userId are required'
            })
        }
    
    print(f"Analyzing image: {image_id} for user: {user_id}")
    
    # Analyze the large processed image (use .jpg for simplified version)
    s3_key = event.get('key') or f"processed/{user_id}/{image_id}.jpg"
    
    # Run all Rekognition analyses
    results = analyze_image(bucket, s3_key)
    
    # Update DynamoDB with results
    update_image_metadata(user_id, image_id, results)
    
    return {
        'statusCode': 200,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'message': 'Image analyzed successfully',
            'imageId': image_id,
            'analysis': results
        }, cls=DecimalEncoder)
    }


def handle_dynamodb_stream(event):
    """
    Handle DynamoDB Stream events.
    Triggered when new image metadata is added.
    """
    
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            # New image added
            new_image = record['dynamodb']['NewImage']
            
            user_id = new_image['userId']['S']
            image_id = new_image['imageId']['S']
            
            print(f"Stream trigger - Analyzing: {image_id}")
            
            # Analyze image (use .jpg for simplified version)
            s3_key = f"processed/{user_id}/{image_id}.jpg"
            results = analyze_image(PROCESSED_BUCKET, s3_key)
            
            # Update DynamoDB
            update_image_metadata(user_id, image_id, results)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Stream processed successfully'})
    }


def analyze_image(bucket, key):
    """
    Analyze image using Amazon Rekognition.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
    
    Returns:
        dict: Analysis results
    """
    
    results = {
        'labels': [],
        'text': [],
        'faces': [],
        'moderation': [],
        'faceCount': 0,
        'hasText': False,
        'isSafe': True
    }
    
    try:
        # 1. Detect Labels (objects, scenes, activities)
        print("Detecting labels...")
        labels_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=MAX_LABELS,
            MinConfidence=MIN_CONFIDENCE
        )
        
        results['labels'] = [
            {
                'name': label['Name'],
                'confidence': Decimal(str(round(label['Confidence'], 2)))
            }
            for label in labels_response['Labels']
        ]
        print(f"Found {len(results['labels'])} labels")
        
    except ClientError as e:
        print(f"Error detecting labels: {str(e)}")
    
    try:
        # 2. Detect Text (OCR)
        print("Detecting text...")
        text_response = rekognition.detect_text(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        # Filter for high-confidence text detections
        results['text'] = [
            {
                'text': text['DetectedText'],
                'confidence': Decimal(str(round(text['Confidence'], 2))),
                'type': text['Type']
            }
            for text in text_response['TextDetections']
            if text['Confidence'] >= MIN_CONFIDENCE and text['Type'] == 'LINE'
        ]
        
        results['hasText'] = len(results['text']) > 0
        print(f"Found {len(results['text'])} text lines")
        
    except ClientError as e:
        print(f"Error detecting text: {str(e)}")
    
    try:
        # 3. Detect Faces
        print("Detecting faces...")
        faces_response = rekognition.detect_faces(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            Attributes=['ALL']
        )
        
        results['faces'] = [
            {
                'confidence': Decimal(str(round(face['Confidence'], 2))),
                'ageRange': {
                    'low': face['AgeRange']['Low'],
                    'high': face['AgeRange']['High']
                },
                'gender': face['Gender']['Value'],
                'emotions': [
                    {
                        'type': emotion['Type'],
                        'confidence': Decimal(str(round(emotion['Confidence'], 2)))
                    }
                    for emotion in sorted(face['Emotions'], key=lambda x: x['Confidence'], reverse=True)[:3]
                ],
                'smile': face['Smile']['Value'],
                'eyeglasses': face['Eyeglasses']['Value'],
                'sunglasses': face['Sunglasses']['Value'],
                'beard': face['Beard']['Value']
            }
            for face in faces_response['FaceDetails']
        ]
        
        results['faceCount'] = len(results['faces'])
        print(f"Found {results['faceCount']} faces")
        
    except ClientError as e:
        print(f"Error detecting faces: {str(e)}")
    
    try:
        # 4. Content Moderation
        print("Checking content moderation...")
        moderation_response = rekognition.detect_moderation_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MinConfidence=MIN_CONFIDENCE
        )
        
        results['moderation'] = [
            {
                'name': label['Name'],
                'confidence': Decimal(str(round(label['Confidence'], 2))),
                'parentName': label.get('ParentName', '')
            }
            for label in moderation_response['ModerationLabels']
        ]
        
        results['isSafe'] = len(results['moderation']) == 0
        
        if not results['isSafe']:
            print(f"⚠️ Content moderation flags: {len(results['moderation'])}")
        else:
            print("✓ Content is safe")
        
    except ClientError as e:
        print(f"Error in content moderation: {str(e)}")
    
    return results


def update_image_metadata(user_id, image_id, analysis_results):
    """
    Update DynamoDB with AI analysis results.
    
    Args:
        user_id: User ID
        image_id: Image ID
        analysis_results: Dict with Rekognition results
    """
    
    # Extract simple tag list from labels
    tags = [label['name'].lower() for label in analysis_results['labels']]
    
    try:
        table.update_item(
            Key={
                'userId': user_id,
                'imageId': image_id
            },
            UpdateExpression='SET tags = :tags, aiAnalysis = :ai, analysisStatus = :status',
            ExpressionAttributeValues={
                ':tags': tags,
                ':ai': {
                    'labels': analysis_results['labels'],
                    'faceCount': analysis_results['faceCount'],
                    'hasText': analysis_results['hasText'],
                    'isSafe': analysis_results['isSafe'],
                    'textDetections': analysis_results['text'][:5],  # Limit text storage
                    'faces': analysis_results['faces'],
                    'moderationFlags': analysis_results['moderation']
                },
                ':status': 'completed'
            }
        )
        
        print(f"✓ Updated DynamoDB for image {image_id} with {len(tags)} tags")
        
    except ClientError as e:
        print(f"Error updating DynamoDB: {str(e)}")
        raise


def get_cors_headers():
    """Return CORS headers for API Gateway responses."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB Decimal types to JSON."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "imageId": "test-image-123",
        "userId": "test-user-123"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2, cls=DecimalEncoder))
