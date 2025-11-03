# Lambda Functions Overview - PhotoGallery Project

**Date:** November 3, 2025  
**Status:** 📋 Planning Phase

---

## 🎯 Overview

We need to create **6 Lambda functions** that will power the backend of our serverless photo gallery. These functions handle everything from file uploads to AI-powered image analysis.

---

## 📦 Lambda Functions Architecture

```
Frontend (Web App)
      ↓
API Gateway (REST API)
      ↓
Lambda Functions (6 functions)
      ↓
AWS Services (S3, DynamoDB, Rekognition)
```

---

## 🔧 Lambda Function #1: GetUploadUrl

### **Purpose**
Generate pre-signed S3 URLs for direct browser uploads

### **Trigger**
API Gateway (POST /upload)

### **What It Does**
1. Receives request from authenticated user
2. Validates file name and type
3. Generates unique image ID (UUID)
4. Creates pre-signed S3 URL (valid for 5 minutes)
5. Returns URL and image ID to frontend
6. Frontend uploads directly to S3 (bypassing server)

### **Technology**
- **Runtime:** Python 3.11 or Node.js 18
- **Memory:** 256 MB
- **Timeout:** 10 seconds

### **Code Flow**
```python
def lambda_handler(event, context):
    # 1. Extract user ID from JWT token
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    # 2. Get filename from request body
    body = json.loads(event['body'])
    filename = body['filename']
    
    # 3. Validate file type
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return error_response(400, 'Invalid file type')
    
    # 4. Generate unique image ID
    image_id = str(uuid.uuid4())
    
    # 5. Create S3 key
    s3_key = f"uploads/{user_id}/{image_id}-{filename}"
    
    # 6. Generate pre-signed URL
    s3_client = boto3.client('s3')
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': UPLOADS_BUCKET,
            'Key': s3_key,
            'ContentType': 'image/*'
        },
        ExpiresIn=300  # 5 minutes
    )
    
    # 7. Return URL and metadata
    return {
        'statusCode': 200,
        'body': json.dumps({
            'uploadUrl': presigned_url,
            'imageId': image_id,
            'key': s3_key
        })
    }
```

### **Input**
```json
{
  "filename": "sunset.jpg",
  "contentType": "image/jpeg"
}
```

### **Output**
```json
{
  "uploadUrl": "https://photogallery-uploads-23brs1079.s3.amazonaws.com/uploads/user123/uuid-sunset.jpg?X-Amz-Algorithm=...",
  "imageId": "550e8400-e29b-41d4-a716-446655440000",
  "key": "uploads/user123/uuid-sunset.jpg"
}
```

### **AWS Services Used**
- S3 (generate pre-signed URL)
- Cognito (validate JWT token via API Gateway)

---

## 🖼️ Lambda Function #2: ProcessImage

### **Purpose**
Automatically process uploaded images (resize, watermark, format conversion)

### **Trigger**
S3 Event (when image uploaded to uploads bucket)

### **What It Does**
1. Triggered when user uploads to S3
2. Downloads original image from S3
3. Creates 3 resized versions:
   - Thumbnail (150x150px)
   - Medium (800x800px)
   - Large (1920x1920px)
4. Applies watermark to large version
5. Converts to WebP format (smaller file size)
6. Uploads processed images to processed bucket
7. Triggers AnalyzeImage function
8. Saves initial metadata to DynamoDB

### **Technology**
- **Runtime:** Python 3.11 (with Pillow library for image processing)
- **Memory:** 1024 MB (image processing is memory-intensive)
- **Timeout:** 60 seconds
- **Layers:** Pillow layer (for image manipulation)

### **Code Flow**
```python
def lambda_handler(event, context):
    # 1. Get S3 event details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Parse: uploads/user123/uuid-filename.jpg
    parts = key.split('/')
    user_id = parts[1]
    image_id = parts[2].split('-')[0]
    
    # 2. Download image from S3
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_data = response['Body'].read()
    
    # 3. Open image with Pillow
    from PIL import Image
    import io
    image = Image.open(io.BytesIO(image_data))
    
    # 4. Create resized versions
    thumbnail = resize_image(image, 150, 150)
    medium = resize_image(image, 800, 800)
    large = resize_image(image, 1920, 1920)
    
    # 5. Apply watermark
    watermarked = apply_watermark(large, "© PhotoGallery")
    
    # 6. Convert to WebP
    webp_data = convert_to_webp(watermarked)
    
    # 7. Upload processed images
    upload_to_s3(thumbnail, f"processed/{user_id}/thumb-{image_id}.jpg")
    upload_to_s3(medium, f"processed/{user_id}/med-{image_id}.jpg")
    upload_to_s3(webp_data, f"processed/{user_id}/{image_id}.webp")
    
    # 8. Invoke AnalyzeImage Lambda
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='AnalyzeImage',
        InvocationType='Event',  # Asynchronous
        Payload=json.dumps({
            'bucket': bucket,
            'key': key,
            'userId': user_id,
            'imageId': image_id
        })
    )
    
    # 9. Save initial metadata to DynamoDB
    save_metadata_to_dynamodb(user_id, image_id, image)
    
    return {'statusCode': 200}
```

### **Image Processing Functions**

#### **Resize Function**
```python
def resize_image(image, max_width, max_height):
    # Maintain aspect ratio
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image
```

#### **Watermark Function**
```python
def apply_watermark(image, text):
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 36)
    
    # Position at bottom-right
    text_width, text_height = draw.textsize(text, font)
    position = (image.width - text_width - 10, image.height - text_height - 10)
    
    # Draw text with opacity
    draw.text(position, text, font=font, fill=(255, 255, 255, 128))
    return image
```

### **AWS Services Used**
- S3 (download original, upload processed)
- DynamoDB (save metadata)
- Lambda (invoke AnalyzeImage)

---

## 🤖 Lambda Function #3: AnalyzeImage

### **Purpose**
Use AI to analyze images and generate tags

### **Trigger**
Invoked by ProcessImage Lambda function

### **What It Does**
1. Receives image location from ProcessImage
2. Calls Amazon Rekognition APIs:
   - **DetectLabels** - Identify objects, scenes, activities
   - **DetectText** - Extract text (OCR)
   - **DetectFaces** - Count and analyze faces
   - **DetectModerationLabels** - Flag inappropriate content
3. Processes AI results
4. Updates DynamoDB with tags and analysis

### **Technology**
- **Runtime:** Python 3.11
- **Memory:** 512 MB
- **Timeout:** 30 seconds

### **Code Flow**
```python
def lambda_handler(event, context):
    bucket = event['bucket']
    key = event['key']
    user_id = event['userId']
    image_id = event['imageId']
    
    rekognition = boto3.client('rekognition')
    
    # 1. Detect labels (objects, scenes)
    labels_response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=20,
        MinConfidence=75
    )
    
    # 2. Detect text (OCR)
    text_response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    # 3. Detect faces
    faces_response = rekognition.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['ALL']
    )
    
    # 4. Content moderation
    moderation_response = rekognition.detect_moderation_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    # 5. Process results
    tags = [label['Name'] for label in labels_response['Labels']]
    detected_text = [text['DetectedText'] for text in text_response['TextDetections']]
    face_count = len(faces_response['FaceDetails'])
    moderation_flags = [label['Name'] for label in moderation_response['ModerationLabels']]
    
    # 6. Update DynamoDB with AI analysis
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PhotoGallery-Images')
    
    table.update_item(
        Key={'userId': user_id, 'imageId': image_id},
        UpdateExpression="""
            SET aiAnalysis = :analysis,
                #tags = :tags,
                processingStatus = :status
        """,
        ExpressionAttributeNames={'#tags': 'tags'},
        ExpressionAttributeValues={
            ':analysis': {
                'labels': labels_response['Labels'],
                'detectedText': detected_text,
                'faceCount': face_count,
                'moderationFlags': moderation_flags
            },
            ':tags': tags,
            ':status': 'completed'
        }
    )
    
    return {'statusCode': 200, 'tags': tags}
```

### **Example Output**
```json
{
  "tags": ["Sunset", "Beach", "Ocean", "Sky", "Nature", "Orange", "Water"],
  "detectedText": ["Beach Resort", "2024"],
  "faceCount": 2,
  "moderationFlags": []
}
```

### **AWS Services Used**
- Rekognition (AI analysis)
- DynamoDB (save results)
- S3 (read image)

---

## 📋 Lambda Function #4: GetImages

### **Purpose**
Retrieve user's photo gallery

### **Trigger**
API Gateway (GET /images)

### **What It Does**
1. Receives authenticated user request
2. Queries DynamoDB for user's images
3. Supports pagination, filtering, sorting
4. Returns list of images with metadata and URLs

### **Technology**
- **Runtime:** Python 3.11 or Node.js 18
- **Memory:** 256 MB
- **Timeout:** 10 seconds

### **Code Flow**
```python
def lambda_handler(event, context):
    # 1. Get user ID from JWT
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    # 2. Parse query parameters
    params = event.get('queryStringParameters', {}) or {}
    limit = int(params.get('limit', 20))
    sort_order = params.get('sort', 'desc')  # newest first
    last_key = params.get('lastKey')  # for pagination
    
    # 3. Query DynamoDB using GSI
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PhotoGallery-Images')
    
    query_params = {
        'IndexName': 'UploadTimeIndex',
        'KeyConditionExpression': Key('userId').eq(user_id),
        'Limit': limit,
        'ScanIndexForward': (sort_order == 'asc')
    }
    
    if last_key:
        query_params['ExclusiveStartKey'] = json.loads(last_key)
    
    response = table.query(**query_params)
    
    # 4. Build image URLs (CloudFront or S3)
    images = []
    for item in response['Items']:
        images.append({
            'imageId': item['imageId'],
            'imageName': item['imageName'],
            'uploadTimestamp': item['uploadTimestamp'],
            'thumbnailUrl': f"https://{CLOUDFRONT_DOMAIN}/processed/{user_id}/thumb-{item['imageId']}.jpg",
            'mediumUrl': f"https://{CLOUDFRONT_DOMAIN}/processed/{user_id}/med-{item['imageId']}.jpg",
            'largeUrl': f"https://{CLOUDFRONT_DOMAIN}/processed/{user_id}/{item['imageId']}.webp",
            'tags': item.get('tags', []),
            'faceCount': item.get('aiAnalysis', {}).get('faceCount', 0)
        })
    
    # 5. Return results with pagination token
    result = {
        'images': images,
        'count': len(images)
    }
    
    if 'LastEvaluatedKey' in response:
        result['nextKey'] = json.dumps(response['LastEvaluatedKey'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### **Input**
```
GET /images?limit=20&sort=desc&lastKey={...}
```

### **Output**
```json
{
  "images": [
    {
      "imageId": "uuid-1",
      "imageName": "sunset.jpg",
      "uploadTimestamp": 1698765432,
      "thumbnailUrl": "https://cdn.../thumb-uuid-1.jpg",
      "mediumUrl": "https://cdn.../med-uuid-1.jpg",
      "largeUrl": "https://cdn.../uuid-1.webp",
      "tags": ["sunset", "beach", "ocean"],
      "faceCount": 0
    }
  ],
  "count": 20,
  "nextKey": "{...}"
}
```

### **AWS Services Used**
- DynamoDB (query images)
- Cognito (authentication)

---

## 🗑️ Lambda Function #5: DeleteImage

### **Purpose**
Delete image and all associated data

### **Trigger**
API Gateway (DELETE /images/{imageId})

### **What It Does**
1. Receives authenticated delete request
2. Verifies user owns the image
3. Deletes from S3 (original + all processed versions)
4. Deletes metadata from DynamoDB
5. Returns success confirmation

### **Technology**
- **Runtime:** Python 3.11 or Node.js 18
- **Memory:** 256 MB
- **Timeout:** 15 seconds

### **Code Flow**
```python
def lambda_handler(event, context):
    # 1. Get user ID and image ID
    user_id = event['requestContext']['authorizer']['claims']['sub']
    image_id = event['pathParameters']['imageId']
    
    # 2. Verify ownership
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PhotoGallery-Images')
    
    response = table.get_item(Key={'userId': user_id, 'imageId': image_id})
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Image not found'})
        }
    
    # 3. Delete from S3 (all versions)
    s3_client = boto3.client('s3')
    
    # Delete original
    s3_client.delete_object(
        Bucket=UPLOADS_BUCKET,
        Key=f"uploads/{user_id}/{image_id}-{response['Item']['imageName']}"
    )
    
    # Delete processed versions
    s3_client.delete_objects(
        Bucket=PROCESSED_BUCKET,
        Delete={
            'Objects': [
                {'Key': f"processed/{user_id}/thumb-{image_id}.jpg"},
                {'Key': f"processed/{user_id}/med-{image_id}.jpg"},
                {'Key': f"processed/{user_id}/{image_id}.webp"}
            ]
        }
    )
    
    # 4. Delete from DynamoDB
    table.delete_item(Key={'userId': user_id, 'imageId': image_id})
    
    # 5. Invalidate CloudFront cache (optional)
    # cloudfront.create_invalidation(...)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Image deleted successfully'})
    }
```

### **Input**
```
DELETE /images/550e8400-e29b-41d4-a716-446655440000
```

### **Output**
```json
{
  "message": "Image deleted successfully"
}
```

### **AWS Services Used**
- S3 (delete objects)
- DynamoDB (delete metadata)
- CloudFront (cache invalidation - optional)

---

## 🔍 Lambda Function #6: SearchImages

### **Purpose**
Search images by tags, filename, or date range

### **Trigger**
API Gateway (GET /images/search)

### **What It Does**
1. Receives search query from user
2. Searches DynamoDB by:
   - Tags (AI-generated or custom)
   - Filename
   - Upload date range
3. Returns matching images
4. Supports pagination

### **Technology**
- **Runtime:** Python 3.11 or Node.js 18
- **Memory:** 256 MB
- **Timeout:** 10 seconds

### **Code Flow**
```python
def lambda_handler(event, context):
    # 1. Get user ID from JWT
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    # 2. Parse search parameters
    params = event.get('queryStringParameters', {}) or {}
    query = params.get('q', '').lower()
    date_from = params.get('from')
    date_to = params.get('to')
    limit = int(params.get('limit', 20))
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PhotoGallery-Images')
    
    # 3. Query by user ID first
    response = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )
    
    # 4. Filter results
    filtered_images = []
    for item in response['Items']:
        # Search in tags
        tags = [tag.lower() for tag in item.get('tags', [])]
        if query and query not in tags and query not in item['imageName'].lower():
            continue
        
        # Date range filter
        upload_time = item['uploadTimestamp']
        if date_from and upload_time < int(date_from):
            continue
        if date_to and upload_time > int(date_to):
            continue
        
        # Add to results
        filtered_images.append({
            'imageId': item['imageId'],
            'imageName': item['imageName'],
            'uploadTimestamp': upload_time,
            'thumbnailUrl': f"https://{CLOUDFRONT_DOMAIN}/processed/{user_id}/thumb-{item['imageId']}.jpg",
            'tags': item.get('tags', [])
        })
        
        if len(filtered_images) >= limit:
            break
    
    # 5. Return results
    return {
        'statusCode': 200,
        'body': json.dumps({
            'images': filtered_images,
            'count': len(filtered_images),
            'query': query
        })
    }
```

### **Input**
```
GET /images/search?q=sunset&from=1698000000&to=1699000000
```

### **Output**
```json
{
  "images": [
    {
      "imageId": "uuid-1",
      "imageName": "sunset.jpg",
      "uploadTimestamp": 1698765432,
      "thumbnailUrl": "https://cdn.../thumb-uuid-1.jpg",
      "tags": ["sunset", "beach", "ocean"]
    }
  ],
  "count": 1,
  "query": "sunset"
}
```

### **AWS Services Used**
- DynamoDB (query and filter)
- Cognito (authentication)

---

## 📊 Lambda Functions Summary Table

| Function | Runtime | Memory | Timeout | Trigger | Purpose |
|----------|---------|--------|---------|---------|---------|
| **GetUploadUrl** | Python/Node | 256 MB | 10s | API Gateway | Generate S3 pre-signed URLs |
| **ProcessImage** | Python | 1024 MB | 60s | S3 Event | Resize, watermark, convert images |
| **AnalyzeImage** | Python | 512 MB | 30s | Lambda invoke | AI tagging with Rekognition |
| **GetImages** | Python/Node | 256 MB | 10s | API Gateway | Retrieve user's gallery |
| **DeleteImage** | Python/Node | 256 MB | 15s | API Gateway | Delete images |
| **SearchImages** | Python/Node | 256 MB | 10s | API Gateway | Search by tags/date |

---

## 🔄 Complete Workflow

```
1. User uploads image via frontend
   ↓
2. Frontend calls GetUploadUrl Lambda
   ↓
3. Lambda returns pre-signed S3 URL
   ↓
4. Frontend uploads directly to S3
   ↓
5. S3 triggers ProcessImage Lambda
   ↓
6. ProcessImage resizes and watermarks
   ↓
7. ProcessImage invokes AnalyzeImage Lambda
   ↓
8. AnalyzeImage uses Rekognition for tagging
   ↓
9. Metadata saved to DynamoDB
   ↓
10. User sees image in gallery (GetImages)
   ↓
11. User can search images (SearchImages)
   ↓
12. User can delete images (DeleteImage)
```

---

## 💰 Cost Estimate

### **Lambda (Free Tier)**
- 1M requests/month: FREE
- 400,000 GB-seconds compute: FREE

### **Expected Usage (Development)**
- ~1000 requests/day
- Well within Free Tier ✅

---

## 🛠️ Development Approach

### **Phase 1: Core Functions (Week 1)**
1. GetUploadUrl
2. GetImages
3. DeleteImage

### **Phase 2: Processing (Week 2)**
4. ProcessImage (with Pillow layer)
5. AnalyzeImage (Rekognition integration)

### **Phase 3: Advanced (Week 3)**
6. SearchImages
7. Testing and optimization

---

## 📦 Required Lambda Layers

### **For ProcessImage Function:**
- **Pillow (PIL)** - Image processing library
- Can use pre-built layer or create custom layer
- ARN: `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-Pillow:1`

### **For All Functions:**
- **boto3** - AWS SDK (included by default)
- **Custom layers** (if needed for other dependencies)

---

## 🔧 Environment Variables

All Lambda functions will need:

```python
UPLOADS_BUCKET = "photogallery-uploads-23brs1079"
PROCESSED_BUCKET = "photogallery-processed-23brs1079"
DYNAMODB_TABLE = "PhotoGallery-Images"
CLOUDFRONT_DOMAIN = "xxxxx.cloudfront.net"  # Will add later
REGION = "us-east-1"
```

---

## ✅ Next Steps

1. **Create function code** for each Lambda
2. **Package dependencies** (if needed)
3. **Deploy to AWS Lambda**
4. **Test each function** individually
5. **Connect to API Gateway**
6. **End-to-end testing**

---

## 🎯 When You're Ready to Build

We'll start with:
1. **GetUploadUrl** (simplest, no external dependencies)
2. Test it with API Gateway
3. Then build ProcessImage with image processing
4. Add Rekognition for AI features
5. Complete with GetImages, DeleteImage, SearchImages

---

**Estimated Development Time:**
- Each function: 30-60 minutes
- Testing: 30 minutes per function
- Total: 6-8 hours

**Ready to code when you are!** 💻

---

**Document Status:** ✅ Complete Overview  
**Last Updated:** November 3, 2025  
**Next:** Lambda Function Development
