"""
Lambda Function: ProcessImage
Purpose: Automatically resize, watermark, and optimize uploaded images
Trigger: S3 event when image is uploaded to uploads bucket
"""

import json
import os
import boto3
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
UPLOADS_BUCKET = os.environ.get('UPLOADS_BUCKET', 'photogallery-uploads-23brs1079')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET', 'photogallery-processed-23brs1079')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'PhotoGallery-Images')
WATERMARK_TEXT = os.environ.get('WATERMARK_TEXT', 'PhotoGallery')

table = dynamodb.Table(DYNAMODB_TABLE)

# Image size configurations
SIZES = {
    'thumbnail': (150, 150),  # Small square for grid view
    'medium': (800, 800),      # Preview size
    'large': (1920, 1920)      # Full size for viewing
}

def lambda_handler(event, context):
    """
    Process uploaded images: resize, watermark, optimize.
    Triggered by S3 event when file uploaded to uploads bucket.
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
            timestamp = filename_parts[1]
            original_name = filename_parts[2]
            
            # Download image from S3
            print(f"Downloading image from S3...")
            response = s3.get_object(Bucket=bucket, Key=key)
            image_data = response['Body'].read()
            file_size = len(image_data)
            
            # Open image with Pillow
            image = Image.open(BytesIO(image_data))
            
            # Get original dimensions
            width, height = image.size
            print(f"Original size: {width}x{height}, Format: {image.format}")
            
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Process and save different sizes
            processed_urls = {}
            
            # 1. Thumbnail (150x150) - square crop
            thumb = create_thumbnail(image, SIZES['thumbnail'])
            thumb_key = f"processed/{user_id}/thumb-{image_id}.jpg"
            upload_to_s3(thumb, PROCESSED_BUCKET, thumb_key, 'JPEG', 85)
            processed_urls['thumbnail'] = f"https://{PROCESSED_BUCKET}.s3.amazonaws.com/{thumb_key}"
            print(f"Created thumbnail: {thumb_key}")
            
            # 2. Medium (800x800) - maintain aspect ratio
            medium = resize_image(image, SIZES['medium'])
            medium_key = f"processed/{user_id}/med-{image_id}.jpg"
            upload_to_s3(medium, PROCESSED_BUCKET, medium_key, 'JPEG', 85)
            processed_urls['medium'] = f"https://{PROCESSED_BUCKET}.s3.amazonaws.com/{medium_key}"
            print(f"Created medium: {medium_key}")
            
            # 3. Large (1920x1920) with watermark - WebP format
            large = resize_image(image, SIZES['large'])
            large_watermarked = add_watermark(large, WATERMARK_TEXT)
            large_key = f"processed/{user_id}/{image_id}.webp"
            upload_to_s3(large_watermarked, PROCESSED_BUCKET, large_key, 'WEBP', 90)
            processed_urls['large'] = f"https://{PROCESSED_BUCKET}.s3.amazonaws.com/{large_key}"
            print(f"Created large: {large_key}")
            
            # Update DynamoDB with image metadata
            update_dynamodb(
                user_id=user_id,
                image_id=image_id,
                original_name=original_name,
                timestamp=int(timestamp),
                width=width,
                height=height,
                file_size=file_size,
                processed_urls=processed_urls
            )
            
            print(f"Successfully processed image {image_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Images processed successfully'
            })
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise


def create_thumbnail(image, size):
    """
    Create square thumbnail by center cropping.
    
    Args:
        image: PIL Image object
        size: Tuple (width, height)
    
    Returns:
        PIL Image object (thumbnail)
    """
    # Calculate crop box for center square
    width, height = image.size
    min_dim = min(width, height)
    
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    
    # Crop to square
    thumbnail = image.crop((left, top, right, bottom))
    
    # Resize to target size
    thumbnail = thumbnail.resize(size, Image.Resampling.LANCZOS)
    
    return thumbnail


def resize_image(image, max_size):
    """
    Resize image maintaining aspect ratio.
    
    Args:
        image: PIL Image object
        max_size: Tuple (max_width, max_height)
    
    Returns:
        PIL Image object (resized)
    """
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image


def add_watermark(image, text):
    """
    Add watermark text to bottom-right corner.
    
    Args:
        image: PIL Image object
        text: Watermark text
    
    Returns:
        PIL Image object (watermarked)
    """
    # Create a copy to avoid modifying original
    watermarked = image.copy()
    draw = ImageDraw.Draw(watermarked)
    
    # Use default font (PIL's built-in)
    # In production, you could include a custom .ttf font file
    try:
        # Try to load a better font if available
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        # Fallback to default
        font = ImageFont.load_default()
    
    # Get text size using textbbox
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position at bottom-right with padding
    width, height = watermarked.size
    x = width - text_width - 10
    y = height - text_height - 10
    
    # Draw text with shadow for better visibility
    # Shadow (black)
    draw.text((x+2, y+2), text, fill=(0, 0, 0, 128), font=font)
    # Main text (white)
    draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
    
    return watermarked


def upload_to_s3(image, bucket, key, format_type, quality):
    """
    Upload processed image to S3.
    
    Args:
        image: PIL Image object
        bucket: S3 bucket name
        key: S3 object key
        format_type: Image format ('JPEG', 'WEBP')
        quality: Compression quality (1-100)
    """
    buffer = BytesIO()
    image.save(buffer, format=format_type, quality=quality, optimize=True)
    buffer.seek(0)
    
    # Determine content type
    content_type = 'image/jpeg' if format_type == 'JPEG' else 'image/webp'
    
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer,
        ContentType=content_type,
        CacheControl='max-age=31536000'  # Cache for 1 year
    )


def update_dynamodb(user_id, image_id, original_name, timestamp, width, height, file_size, processed_urls):
    """
    Create/update image metadata in DynamoDB.
    
    Args:
        user_id: User ID
        image_id: Image ID (UUID)
        original_name: Original filename
        timestamp: Upload timestamp
        width: Image width
        height: Image height
        file_size: File size in bytes
        processed_urls: Dict with thumbnail, medium, large URLs
    """
    table.put_item(
        Item={
            'userId': user_id,
            'imageId': image_id,
            'imageName': original_name,
            'uploadTimestamp': timestamp,
            'width': width,
            'height': height,
            'fileSize': file_size,
            'processedUrls': processed_urls,
            'processingStatus': 'completed',
            'tags': [],  # Will be populated by AnalyzeImage Lambda
            'createdAt': datetime.utcnow().isoformat()
        }
    )
    print(f"Updated DynamoDB for image {image_id}")


# For local testing (won't work without actual S3 event)
if __name__ == "__main__":
    print("ProcessImage Lambda - requires S3 event trigger")
    print("Deploy to AWS and configure S3 event notification")
