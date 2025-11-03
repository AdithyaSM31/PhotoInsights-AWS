"""
Lambda Function: SearchImages
Purpose: Search images by tags, filename, date range
Trigger: API Gateway GET /images/search
"""

import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'PhotoGallery-Images')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'photogallery-processed-23brs1079')
CLOUDFRONT_DOMAIN = os.environ.get('CLOUDFRONT_DOMAIN', '')

table = dynamodb.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    Search images based on multiple criteria.
    
    Query Parameters:
    - tags: Comma-separated tags (e.g., "sunset,beach")
    - filename: Search in filename
    - dateFrom: Start date (YYYY-MM-DD or Unix timestamp)
    - dateTo: End date (YYYY-MM-DD or Unix timestamp)
    - hasFaces: true/false
    - hasText: true/false
    - limit: Results per page (1-100, default: 20)
    - sortOrder: asc/desc (default: desc - newest first)
    - lastKey: Pagination token
    """
    
    try:
        # Extract user ID from Cognito JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Get query parameters
        params = event.get('queryStringParameters') or {}
        
        # Parse search criteria
        search_tags = params.get('tags', '').lower().split(',') if params.get('tags') else []
        search_filename = params.get('filename', '').lower()
        date_from = parse_timestamp(params.get('dateFrom'))
        date_to = parse_timestamp(params.get('dateTo'))
        has_faces = params.get('hasFaces', '').lower() == 'true' if params.get('hasFaces') else None
        has_text = params.get('hasText', '').lower() == 'true' if params.get('hasText') else None
        
        # Pagination parameters
        limit = min(int(params.get('limit', 20)), 100)
        sort_order = params.get('sortOrder', 'desc').lower() == 'desc'
        last_key = params.get('lastKey')
        
        print(f"Search - User: {user_id}, Tags: {search_tags}, Filename: {search_filename}")
        
        # Build query
        query_params = build_query(
            user_id=user_id,
            tags=search_tags,
            filename=search_filename,
            date_from=date_from,
            date_to=date_to,
            has_faces=has_faces,
            has_text=has_text,
            limit=limit,
            sort_order=sort_order,
            last_key=last_key
        )
        
        # Execute search
        response = table.query(**query_params)
        
        # Process results
        images = []
        for item in response.get('Items', []):
            images.append(format_image_item(item))
        
        # Prepare response
        result = {
            'images': images,
            'count': len(images),
            'userId': user_id,
            'hasMore': 'LastEvaluatedKey' in response
        }
        
        # Add pagination token if more results available
        if 'LastEvaluatedKey' in response:
            import base64
            result['nextKey'] = base64.b64encode(
                json.dumps(response['LastEvaluatedKey']).encode()
            ).decode()
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(result, cls=DecimalEncoder)
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
    
    except Exception as e:
        print(f"Search error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }


def build_query(user_id, tags, filename, date_from, date_to, has_faces, has_text, limit, sort_order, last_key):
    """
    Build DynamoDB query with filters.
    
    Strategy:
    1. Use GSI (UploadTimeIndex) for date-based queries
    2. Apply filters for tags, filename, faces, text
    3. Filter in application layer (DynamoDB has 1MB limit)
    """
    
    # Base query using GSI for time-based sorting
    query_params = {
        'IndexName': 'UploadTimeIndex',
        'KeyConditionExpression': Key('userId').eq(user_id),
        'Limit': limit * 3,  # Fetch extra to account for filtering
        'ScanIndexForward': not sort_order  # False = descending
    }
    
    # Add date range to key condition if provided
    if date_from and date_to:
        query_params['KeyConditionExpression'] &= Key('uploadTimestamp').between(date_from, date_to)
    elif date_from:
        query_params['KeyConditionExpression'] &= Key('uploadTimestamp').gte(date_from)
    elif date_to:
        query_params['KeyConditionExpression'] &= Key('uploadTimestamp').lte(date_to)
    
    # Build filter expression for other criteria
    filter_expressions = []
    
    # Filter by tags (must contain at least one tag)
    if tags and tags[0]:  # Check if tags list is not empty
        tag_filters = [Attr('tags').contains(tag) for tag in tags if tag]
        if tag_filters:
            # Combine with OR logic
            combined_filter = tag_filters[0]
            for tag_filter in tag_filters[1:]:
                combined_filter |= tag_filter
            filter_expressions.append(combined_filter)
    
    # Filter by filename
    if filename:
        filter_expressions.append(Attr('imageName').contains(filename))
    
    # Filter by face presence
    if has_faces is not None:
        if has_faces:
            filter_expressions.append(Attr('aiAnalysis.faceCount').gt(0))
        else:
            filter_expressions.append(Attr('aiAnalysis.faceCount').eq(0))
    
    # Filter by text presence
    if has_text is not None:
        filter_expressions.append(Attr('aiAnalysis.hasText').eq(has_text))
    
    # Combine all filters with AND logic
    if filter_expressions:
        combined_filter = filter_expressions[0]
        for filter_expr in filter_expressions[1:]:
            combined_filter &= filter_expr
        query_params['FilterExpression'] = combined_filter
    
    # Add pagination token
    if last_key:
        import base64
        query_params['ExclusiveStartKey'] = json.loads(
            base64.b64decode(last_key).decode()
        )
    
    return query_params


def format_image_item(item):
    """
    Format DynamoDB item for response.
    
    Args:
        item: DynamoDB item
    
    Returns:
        dict: Formatted image data
    """
    
    # Build CDN URLs
    base_url = f"https://{CLOUDFRONT_DOMAIN}" if CLOUDFRONT_DOMAIN else f"https://{PROCESSED_BUCKET}.s3.amazonaws.com"
    
    user_id = item['userId']
    image_id = item['imageId']
    
    formatted = {
        'imageId': image_id,
        'imageName': item.get('imageName', 'untitled'),
        'uploadTimestamp': item.get('uploadTimestamp'),
        'fileSize': item.get('fileSize'),
        'width': item.get('width'),
        'height': item.get('height'),
        'urls': {
            'thumbnail': f"{base_url}/processed/{user_id}/thumb-{image_id}.jpg",
            'medium': f"{base_url}/processed/{user_id}/med-{image_id}.jpg",
            'large': f"{base_url}/processed/{user_id}/{image_id}.webp",
            'original': f"https://{PROCESSED_BUCKET.replace('processed', 'uploads')}.s3.amazonaws.com/uploads/{user_id}/{image_id}-{item.get('uploadTimestamp', '')}-{item.get('imageName', '')}"
        },
        'tags': item.get('tags', []),
        'processingStatus': item.get('processingStatus', 'unknown')
    }
    
    # Add AI analysis summary if available
    if 'aiAnalysis' in item:
        ai = item['aiAnalysis']
        formatted['aiAnalysis'] = {
            'faceCount': ai.get('faceCount', 0),
            'hasText': ai.get('hasText', False),
            'isSafe': ai.get('isSafe', True),
            'topLabels': [label['name'] for label in ai.get('labels', [])[:3]]
        }
    
    return formatted


def parse_timestamp(date_str):
    """
    Convert date string to Unix timestamp.
    
    Args:
        date_str: Date string (YYYY-MM-DD or Unix timestamp)
    
    Returns:
        int: Unix timestamp or None
    """
    
    if not date_str:
        return None
    
    try:
        # Try as Unix timestamp first
        return int(date_str)
    except ValueError:
        pass
    
    try:
        # Try as YYYY-MM-DD format
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return int(dt.timestamp())
    except ValueError:
        pass
    
    return None


def get_cors_headers():
    """Return CORS headers for API Gateway responses."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB Decimal types to JSON."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 else int(obj)
        return super(DecimalEncoder, self).default(obj)


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "test-user-123"
                }
            }
        },
        "queryStringParameters": {
            "tags": "sunset,beach",
            "limit": "10"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
