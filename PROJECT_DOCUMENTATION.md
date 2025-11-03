# Serverless Photo Gallery - AWS DA3 Project

## Project Team

**Team Members:**
1. **Adithya Sankar Menon** - 23BRS1079
2. **Karthick Swaminathan** - 23BRS1063
3. **Sambari Bhuvan** - 23BRS1189

**Submission Date:** October 28, 2025

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Objectives](#objectives)
3. [Architecture Overview](#architecture-overview)
4. [AWS Services Used](#aws-services-used)
5. [Core Features](#core-features)
6. [Image Processing Pipeline](#image-processing-pipeline)
7. [Database Schema](#database-schema)
8. [Security Implementation](#security-implementation)
9. [System Architecture](#system-architecture)
10. [Implementation Plan](#implementation-plan)
11. [Cost Estimation](#cost-estimation)
12. [Expected Outcomes](#expected-outcomes)
13. [Technical Workflow](#technical-workflow)
14. [Scalability and Performance](#scalability-and-performance)

---

## Project Overview

The **Serverless Photo Gallery** is a cloud-native web application that leverages AWS serverless architecture to provide users with an automated, scalable, and cost-efficient photo management system. The application eliminates the need for managing physical servers while providing enterprise-grade features including automatic image processing, secure authentication, and intelligent content delivery.

### Key Highlights

- **Fully Serverless:** No server management required
- **Event-Driven Architecture:** Automated workflows triggered by events
- **Scalable:** Automatically scales with user demand
- **Cost-Efficient:** Pay only for resources consumed
- **Intelligent Processing:** AI-powered image recognition and tagging
- **Secure:** Enterprise-grade authentication and authorization

---

## Objectives

### Primary Objectives

1. **Automate Image Workflow:** Create an end-to-end automated pipeline for image upload, processing, and storage
2. **Demonstrate Serverless Architecture:** Showcase AWS serverless capabilities without managing infrastructure
3. **Implement Secure Access:** Ensure user authentication and authorization for all operations
4. **Enable Intelligent Processing:** Utilize AI for automatic image tagging and recognition
5. **Optimize Content Delivery:** Implement CDN for fast global image delivery

### Learning Objectives

- Understand and implement AWS serverless services
- Design event-driven architectures
- Implement secure authentication flows
- Work with NoSQL databases
- Integrate AI/ML services for practical applications

---

## Architecture Overview

The application follows a **microservices-based serverless architecture** where each component is loosely coupled and communicates through events and APIs. The architecture is designed to be:

- **Highly Available:** Multi-AZ deployment across AWS regions
- **Fault Tolerant:** Automatic failover and retry mechanisms
- **Scalable:** Auto-scaling based on demand
- **Secure:** Multiple layers of security controls

```
User → CloudFront → S3 (Static Website) → API Gateway → Lambda Functions
                                                              ↓
                                                       DynamoDB (Metadata)
                                                              ↓
User Upload → S3 Bucket → Event Trigger → Lambda → Rekognition
                                            ↓
                                    Processed Images → S3
```

---

## AWS Services Used

### 1. **Amazon S3 (Simple Storage Service)**

**Purpose:** Storage and hosting

**Usage in Project:**
- **Source Bucket:** Store original uploaded images
- **Processed Bucket:** Store processed/resized images
- **Static Website Hosting:** Host frontend application
- **Event Notifications:** Trigger Lambda functions on upload

**Configuration:**
- Versioning enabled for backup
- Lifecycle policies for cost optimization
- CORS configuration for web access
- Server-side encryption for security

---

### 2. **AWS Lambda**

**Purpose:** Serverless compute engine

**Functions Implemented:**

#### a) **Image Processing Function**
- **Trigger:** S3 PUT event (new image upload)
- **Processing Tasks:**
  - Image resizing (thumbnail, medium, large)
  - Format conversion (JPEG, PNG, WebP)
  - Watermark application (text/logo overlay)
  - Metadata extraction (EXIF data)
- **Runtime:** Python 3.11 / Node.js 18.x
- **Memory:** 1024 MB
- **Timeout:** 60 seconds

#### b) **Rekognition Integration Function**
- **Trigger:** Invoked by Image Processing Function
- **Processing Tasks:**
  - Detect objects, scenes, and activities
  - Identify people and faces
  - Extract text from images (OCR)
  - Detect inappropriate content
  - Generate searchable tags
- **Runtime:** Python 3.11
- **Memory:** 512 MB
- **Timeout:** 30 seconds

#### c) **API Handler Functions**
- **GetImages:** Retrieve user's image gallery
- **GetImageMetadata:** Fetch specific image details
- **DeleteImage:** Remove image and metadata
- **SearchImages:** Search by tags or metadata

---

### 3. **Amazon API Gateway**

**Purpose:** RESTful API endpoints

**API Endpoints:**

| Method | Endpoint | Function | Authentication |
|--------|----------|----------|----------------|
| GET | `/images` | List all user images | Required |
| GET | `/images/{id}` | Get specific image | Required |
| POST | `/images/upload` | Get pre-signed upload URL | Required |
| DELETE | `/images/{id}` | Delete image | Required |
| GET | `/images/search` | Search images by tags | Required |
| GET | `/user/profile` | Get user profile | Required |

**Features:**
- CORS enabled for web access
- Request/Response validation
- API throttling and rate limiting
- CloudWatch integration for monitoring
- Custom domain name support

---

### 4. **Amazon DynamoDB**

**Purpose:** NoSQL metadata database

**Table Design:**

#### **Images Table**

```json
{
  "TableName": "PhotoGallery-Images",
  "KeySchema": [
    {
      "AttributeName": "userId",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "imageId",
      "KeyType": "RANGE"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "userId",
      "AttributeType": "S"
    },
    {
      "AttributeName": "imageId",
      "AttributeType": "S"
    },
    {
      "AttributeName": "uploadTimestamp",
      "AttributeType": "N"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "UploadTimeIndex",
      "KeySchema": [
        {
          "AttributeName": "userId",
          "KeyType": "HASH"
        },
        {
          "AttributeName": "uploadTimestamp",
          "KeyType": "RANGE"
        }
      ]
    }
  ]
}
```

#### **Metadata Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `userId` | String | Cognito user ID (Partition Key) |
| `imageId` | String | Unique image identifier (Sort Key) |
| `imageName` | String | Original filename |
| `uploadTimestamp` | Number | Unix timestamp of upload |
| `fileSize` | Number | Original file size in bytes |
| `fileFormat` | String | Original format (jpg, png, etc.) |
| `originalUrl` | String | S3 URL of original image |
| `thumbnailUrl` | String | S3 URL of thumbnail |
| `processedUrl` | String | S3 URL of processed image |
| `width` | Number | Image width in pixels |
| `height` | Number | Image height in pixels |
| `detectedTags` | List | AI-generated tags from Rekognition |
| `detectedLabels` | Map | Labels with confidence scores |
| `detectedText` | List | OCR extracted text |
| `faceCount` | Number | Number of faces detected |
| `watermarked` | Boolean | Watermark applied status |
| `contentModeration` | Map | Inappropriate content flags |
| `exifData` | Map | Camera and photo metadata |
| `isPublic` | Boolean | Public/private flag |
| `lastModified` | Number | Last update timestamp |

**Why DynamoDB for Metadata?**

1. **Data Consistency:** Prevents inconsistencies by maintaining a single source of truth
2. **Fast Queries:** Sub-millisecond latency for metadata retrieval
3. **Flexible Schema:** Easy to add new metadata fields
4. **Scalability:** Automatically scales with demand
5. **Search Capability:** Enable searching by tags, dates, or other attributes
6. **Image Verification:** Check if image exists before processing
7. **Duplicate Detection:** Use hash values to identify duplicate uploads
8. **Audit Trail:** Track all image operations and history

---

### 5. **Amazon Cognito**

**Purpose:** User authentication and authorization

**Features Implemented:**

#### **User Pool Configuration**
- Email/password authentication
- Multi-factor authentication (MFA) optional
- Password policy enforcement
- Email verification
- Forgot password flow
- User attributes (name, email, profile picture)

#### **Security Features**
- JWT token-based authentication
- Token refresh mechanism
- Session management
- User groups for access control
- Identity federation (optional: Google, Facebook)

#### **Authorization Flow**
```
1. User signs up → Email verification
2. User logs in → Receive JWT tokens (ID, Access, Refresh)
3. Frontend stores tokens → LocalStorage (ID token) + HttpOnly Cookie (Refresh)
4. API requests → Include ID token in Authorization header
5. API Gateway → Validate token with Cognito
6. Lambda functions → Access user ID from token claims
```

---

### 6. **Amazon CloudFront**

**Purpose:** Content Delivery Network (CDN)

**Distributions:**

#### **Static Website Distribution**
- **Origin:** S3 static website bucket
- **Caching:** HTML (5 min), CSS/JS (1 hour), Images (24 hours)
- **SSL/TLS:** Custom certificate or CloudFront default
- **Compression:** Gzip/Brotli enabled

#### **Images Distribution**
- **Origin:** S3 processed images bucket
- **Caching:** Long TTL (7 days)
- **Invalidation:** Automatic on image deletion
- **Custom Headers:** CORS, Cache-Control
- **Price Class:** Use edge locations closest to users

**Benefits:**
- Reduced latency for global users
- Reduced load on S3
- DDoS protection
- HTTPS enforcement
- Cost savings on data transfer

---

### 7. **Amazon Rekognition**

**Purpose:** AI-powered image analysis

**Features Used:**

#### **Label Detection**
- Detect objects (car, tree, building, etc.)
- Identify scenes (beach, sunset, indoor, etc.)
- Recognize activities (running, swimming, etc.)
- Confidence scores for each label

#### **Face Detection and Analysis**
- Detect faces in images
- Facial attributes (age range, gender, emotions)
- Face comparison for grouping
- Celebrity recognition (optional)

#### **Text Detection (OCR)**
- Extract text from images
- Support for multiple languages
- Text location and bounding boxes

#### **Content Moderation**
- Detect inappropriate content
- Flag suggestive or explicit images
- Identify violence or weapons

**Integration:**
```python
# Example Rekognition Integration
def analyze_image(bucket, key):
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=20,
        MinConfidence=70
    )
    
    tags = [label['Name'] for label in response['Labels']]
    return tags
```

---

## Core Features

### 1. **User Authentication**
- Secure sign-up and login
- Email verification
- Password reset functionality
- Session management
- Multi-device support

### 2. **Image Upload**
- Drag-and-drop interface
- Multiple file upload
- Progress indicators
- Pre-signed URL for direct S3 upload
- Client-side validation (file type, size)

### 3. **Automatic Image Processing**

#### **Resizing**
- **Thumbnail:** 150x150px (for gallery grid)
- **Medium:** 800x800px (for preview)
- **Large:** 1920x1920px (for full view)
- Maintains aspect ratio
- Progressive JPEG for faster loading

#### **Watermarking**
- Text watermark with custom message
- Logo overlay from S3 bucket
- Configurable position (corner, center)
- Opacity and size control
- User-specific watermark settings

#### **Format Conversion**
- Convert to WebP for smaller file size
- Maintain JPEG/PNG for compatibility
- Automatic format selection based on browser support
- Quality optimization

### 4. **AI Tagging and Recognition**
- Automatic object detection
- Scene recognition
- Text extraction (OCR)
- Face detection and counting
- Content moderation
- Searchable tag generation

### 5. **Photo Gallery View**
- Grid/list layout toggle
- Infinite scroll pagination
- Filter by date, tags, or name
- Sort options (newest, oldest, name)
- Full-screen image viewer
- Image sharing (generate public link)

### 6. **Search Functionality**
- Search by filename
- Search by AI-generated tags
- Search by upload date range
- Search by detected text
- Combined search filters

### 7. **Image Management**
- View image details and metadata
- Download original/processed images
- Delete images (soft delete with retention)
- Edit image tags manually
- Set images as public/private

---

## Image Processing Pipeline

### Workflow Diagram

```
┌──────────────┐
│   User       │
│   Uploads    │
│   Image      │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  API Gateway     │
│  /upload         │──→ Returns pre-signed S3 URL
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Client uploads  │
│  directly to S3  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  S3 PUT Event    │
│  Notification    │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────┐
│  Lambda: ImageProcessor  │
│                          │
│  1. Download image       │
│  2. Resize (3 sizes)     │
│  3. Apply watermark      │
│  4. Convert format       │
│  5. Upload processed     │
│  6. Invoke Rekognition   │
└──────┬──────────────┬────┘
       │              │
       ▼              ▼
┌──────────────┐  ┌────────────────┐
│  Rekognition │  │  Upload to S3  │
│  Analysis    │  │  /processed/   │
└──────┬───────┘  └────────────────┘
       │
       ▼
┌──────────────────┐
│  Lambda writes   │
│  metadata to     │
│  DynamoDB        │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  CloudFront      │
│  Cache cleared   │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  User sees       │
│  processed image │
│  in gallery      │
└──────────────────┘
```

### Processing Steps in Detail

#### **Step 1: Pre-signed URL Generation**
```python
# Lambda function: GetUploadUrl
def generate_upload_url(user_id, filename):
    s3_client = boto3.client('s3')
    key = f"uploads/{user_id}/{uuid4()}-{filename}"
    
    url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': UPLOAD_BUCKET, 'Key': key},
        ExpiresIn=300  # 5 minutes
    )
    
    return {
        'uploadUrl': url,
        'imageId': key.split('/')[2].split('-')[0]
    }
```

#### **Step 2: Image Processing**
```python
# Lambda function: ProcessImage
def process_image(event):
    # Extract S3 event details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download image
    image = download_from_s3(bucket, key)
    
    # Create resized versions
    thumbnail = resize_image(image, 150, 150)
    medium = resize_image(image, 800, 800)
    large = resize_image(image, 1920, 1920)
    
    # Apply watermark
    watermarked = apply_watermark(large, "© PhotoGallery")
    
    # Convert format
    webp_version = convert_to_webp(watermarked)
    
    # Upload processed images
    upload_to_s3(thumbnail, f"processed/{user_id}/thumb-{image_id}.jpg")
    upload_to_s3(medium, f"processed/{user_id}/med-{image_id}.jpg")
    upload_to_s3(webp_version, f"processed/{user_id}/{image_id}.webp")
    
    # Invoke Rekognition
    tags = analyze_with_rekognition(bucket, key)
    
    # Save metadata to DynamoDB
    save_metadata(user_id, image_id, tags)
```

#### **Step 3: Rekognition Analysis**
```python
# Lambda function: AnalyzeImage
def analyze_with_rekognition(bucket, key):
    rekognition = boto3.client('rekognition')
    
    # Detect labels
    labels_response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=20,
        MinConfidence=75
    )
    
    # Detect text
    text_response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    # Detect faces
    faces_response = rekognition.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['ALL']
    )
    
    # Content moderation
    moderation_response = rekognition.detect_moderation_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    return {
        'labels': [l['Name'] for l in labels_response['Labels']],
        'text': [t['DetectedText'] for t in text_response['TextDetections']],
        'faceCount': len(faces_response['FaceDetails']),
        'moderation': moderation_response['ModerationLabels']
    }
```

---

## Database Schema

### DynamoDB Tables

#### **Images Table**

```javascript
{
  userId: "cognito-user-id-123",  // Partition Key
  imageId: "uuid-v4",               // Sort Key
  imageName: "sunset.jpg",
  uploadTimestamp: 1698451200,
  fileSize: 2458624,
  fileFormat: "jpeg",
  dimensions: {
    width: 3840,
    height: 2160
  },
  urls: {
    original: "https://cloudfront.net/original/user123/img.jpg",
    thumbnail: "https://cloudfront.net/processed/user123/thumb-img.jpg",
    medium: "https://cloudfront.net/processed/user123/med-img.jpg",
    large: "https://cloudfront.net/processed/user123/img.webp"
  },
  processing: {
    status: "completed",
    watermarked: true,
    convertedFormats: ["webp", "jpeg"]
  },
  aiAnalysis: {
    tags: ["sunset", "beach", "ocean", "sky", "orange"],
    labels: [
      { name: "Sunset", confidence: 98.5 },
      { name: "Beach", confidence: 95.3 },
      { name: "Ocean", confidence: 92.1 }
    ],
    detectedText: ["Beach Resort", "2024"],
    faceCount: 2,
    moderationFlags: []
  },
  exifData: {
    camera: "Canon EOS R5",
    lens: "RF 24-70mm f/2.8",
    iso: 100,
    aperture: "f/8",
    shutterSpeed: "1/250",
    focalLength: "35mm",
    dateTaken: "2024-10-15T18:30:00Z"
  },
  metadata: {
    isPublic: false,
    shareUrl: null,
    viewCount: 15,
    lastModified: 1698451300,
    customTags: ["vacation", "favorites"]
  }
}
```

#### **Users Table** (Optional)

```javascript
{
  userId: "cognito-user-id-123",  // Partition Key
  email: "user@example.com",
  name: "John Doe",
  preferences: {
    defaultWatermark: "© John Doe Photography",
    autoTagging: true,
    publicGallery: false
  },
  statistics: {
    totalImages: 145,
    totalStorage: 524288000,  // bytes
    joinDate: 1685664000
  }
}
```

### GSI (Global Secondary Index)

**Index: UploadTimeIndex**
- Partition Key: `userId`
- Sort Key: `uploadTimestamp`
- Purpose: Query images by upload date range

**Index: TagsIndex**
- Partition Key: `userId`
- Sort Key: `tags` (as a string attribute)
- Purpose: Search images by tags

---

## Security Implementation

### 1. **Authentication Layer (Cognito)**
- JWT token validation on every API request
- Token expiration and refresh mechanism
- Secure password policies (min 8 chars, special chars)
- Rate limiting on login attempts
- Account lockout after failed attempts

### 2. **Authorization Layer**
- User can only access their own images
- Lambda authorizer validates user context
- DynamoDB queries filtered by userId
- S3 bucket policies restrict access

### 3. **Network Security**
- HTTPS enforced on all endpoints
- CloudFront custom SSL certificates
- API Gateway resource policies
- VPC endpoints for internal communication (optional)

### 4. **Data Security**
- S3 server-side encryption (SSE-S3 or SSE-KMS)
- DynamoDB encryption at rest
- Secrets Manager for API keys and credentials
- IAM roles with least privilege principle

### 5. **Input Validation**
- File type validation (whitelist: jpg, jpeg, png, gif)
- File size limits (max 10 MB per upload)
- Image dimension validation
- SQL injection prevention (N/A for NoSQL)
- XSS prevention in metadata

### 6. **Monitoring and Auditing**
- CloudWatch Logs for all Lambda functions
- API Gateway access logs
- CloudTrail for AWS API calls
- DynamoDB point-in-time recovery
- S3 versioning and lifecycle policies

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User / Client                           │
│                    (Web Browser / Mobile)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon CloudFront (CDN)                      │
│            Global Content Delivery + DDoS Protection            │
└────────────┬───────────────────────────────────┬────────────────┘
             │                                   │
             │ Static Assets                     │ API Requests
             ▼                                   ▼
┌─────────────────────┐              ┌──────────────────────────┐
│   Amazon S3         │              │   Amazon API Gateway     │
│   Static Website    │              │   RESTful API            │
│   (HTML/CSS/JS)     │              │   + Cognito Authorizer   │
└─────────────────────┘              └──────────┬───────────────┘
                                                │
                                                │ Invoke
                                                ▼
                                     ┌──────────────────────────┐
                                     │   AWS Lambda Functions   │
                                     │   (Node.js / Python)     │
                                     │                          │
                                     │   - GetImages            │
                                     │   - GetUploadUrl         │
                                     │   - ProcessImage         │
                                     │   - AnalyzeImage         │
                                     │   - DeleteImage          │
                                     │   - SearchImages         │
                                     └────┬──────────┬──────┬───┘
                                          │          │      │
             ┌────────────────────────────┘          │      └──────────────┐
             │                                       │                     │
             ▼                                       ▼                     ▼
┌─────────────────────┐              ┌──────────────────────┐  ┌─────────────────┐
│   Amazon S3         │              │   Amazon DynamoDB    │  │ Amazon Cognito  │
│   Image Storage     │              │   Metadata Database  │  │ Authentication  │
│                     │              │                      │  │                 │
│   - /uploads/       │              │   Tables:            │  │ - User Pool     │
│   - /processed/     │              │   - Images           │  │ - User Groups   │
│   - /thumbnails/    │              │   - Users (optional) │  │ - JWT Tokens    │
└─────────┬───────────┘              └──────────────────────┘  └─────────────────┘
          │                                                    
          │ S3 Event                                          
          ▼                                                    
┌─────────────────────┐                                       
│   AWS Lambda        │                                       
│   ProcessImage      │────────────────┐                     
│   Function          │                │                     
└─────────────────────┘                │ Analyze             
                                       ▼                     
                            ┌──────────────────────┐         
                            │ Amazon Rekognition   │         
                            │ AI Image Analysis    │         
                            │                      │         
                            │ - Label Detection    │         
                            │ - Face Detection     │         
                            │ - Text Detection     │         
                            │ - Content Moderation │         
                            └──────────────────────┘         
```

### Component Interaction Flow

**Image Upload Flow:**
```
1. User authenticates → Cognito returns JWT token
2. User clicks upload → Frontend requests pre-signed URL from API
3. API Gateway → Lambda generates S3 pre-signed URL
4. Frontend uploads directly to S3 using pre-signed URL
5. S3 triggers ProcessImage Lambda function
6. Lambda downloads, processes, and re-uploads image
7. Lambda invokes Rekognition for AI analysis
8. Lambda saves metadata to DynamoDB
9. User receives success notification
```

**Image Retrieval Flow:**
```
1. User opens gallery → Frontend calls /images API
2. API Gateway validates JWT token
3. Lambda queries DynamoDB for user's images
4. DynamoDB returns metadata with CloudFront URLs
5. Frontend displays thumbnails from CloudFront
6. User clicks image → Frontend loads full image from CloudFront
7. CloudFront serves cached image (or from S3 origin)
```

---

## Implementation Plan

### Phase 1: Infrastructure Setup (Week 1)

#### **Day 1-2: AWS Account & IAM Setup**
- [ ] Create AWS account (use Free Tier)
- [ ] Set up billing alerts
- [ ] Create IAM users for team members
- [ ] Configure MFA for root account
- [ ] Create IAM roles for Lambda functions

#### **Day 3-4: S3 Bucket Configuration**
- [ ] Create S3 buckets:
  - `photogallery-uploads-[random]`
  - `photogallery-processed-[random]`
  - `photogallery-website-[random]`
- [ ] Configure bucket policies
- [ ] Enable versioning and encryption
- [ ] Set up lifecycle policies
- [ ] Configure CORS

#### **Day 5-7: Cognito User Pool**
- [ ] Create Cognito User Pool
- [ ] Configure password policies
- [ ] Set up email verification
- [ ] Create user pool client
- [ ] Test sign-up and login flows

---

### Phase 2: Backend Development (Week 2)

#### **Day 1-3: Lambda Functions**
- [ ] Create Lambda execution role
- [ ] Develop GetUploadUrl function
- [ ] Develop ProcessImage function
  - Image resizing logic
  - Watermarking implementation
  - Format conversion
- [ ] Develop AnalyzeImage function
  - Rekognition integration
- [ ] Develop GetImages function
- [ ] Develop DeleteImage function
- [ ] Develop SearchImages function

#### **Day 4-5: API Gateway**
- [ ] Create REST API
- [ ] Define resources and methods
- [ ] Configure Cognito authorizer
- [ ] Set up CORS
- [ ] Configure request/response models
- [ ] Test API endpoints with Postman

#### **Day 6-7: DynamoDB**
- [ ] Create Images table
- [ ] Configure GSI for queries
- [ ] Set up auto-scaling
- [ ] Test CRUD operations
- [ ] Implement error handling

---

### Phase 3: Image Processing Pipeline (Week 3)

#### **Day 1-2: S3 Event Triggers**
- [ ] Configure S3 event notifications
- [ ] Link S3 events to Lambda
- [ ] Test automatic trigger on upload

#### **Day 3-4: Image Processing**
- [ ] Implement PIL/Pillow for Python (or Sharp for Node.js)
- [ ] Create resize functions (3 sizes)
- [ ] Implement watermark overlay
- [ ] Add format conversion (WebP)
- [ ] Test with various image types

#### **Day 5-6: Rekognition Integration**
- [ ] Set up Rekognition client
- [ ] Implement label detection
- [ ] Implement text detection (OCR)
- [ ] Implement face detection
- [ ] Implement content moderation
- [ ] Test with sample images

#### **Day 7: Metadata Storage**
- [ ] Save processed image URLs to DynamoDB
- [ ] Store AI-generated tags
- [ ] Store EXIF data
- [ ] Test metadata retrieval

---

### Phase 4: Frontend Development (Week 4)

#### **Day 1-2: Frontend Framework Setup**
- [ ] Choose framework (React, Vue, or Vanilla JS)
- [ ] Set up project structure
- [ ] Configure build tools (Webpack/Vite)
- [ ] Create component structure

#### **Day 3-4: Authentication UI**
- [ ] Create login page
- [ ] Create sign-up page
- [ ] Implement Cognito SDK integration
- [ ] Handle JWT token storage
- [ ] Create protected routes

#### **Day 5-6: Gallery UI**
- [ ] Create image grid layout
- [ ] Implement upload component
- [ ] Create image viewer/modal
- [ ] Add filter and search UI
- [ ] Implement pagination/infinite scroll

#### **Day 7: Integration**
- [ ] Connect frontend to API Gateway
- [ ] Test image upload flow
- [ ] Test image retrieval and display
- [ ] Test search and filter
- [ ] Handle error states and loading

---

### Phase 5: CloudFront & Optimization (Week 5)

#### **Day 1-2: CloudFront Setup**
- [ ] Create distribution for static website
- [ ] Create distribution for images
- [ ] Configure cache behaviors
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificate

#### **Day 3-4: Performance Optimization**
- [ ] Implement lazy loading for images
- [ ] Add progressive image loading
- [ ] Optimize bundle size
- [ ] Implement client-side caching
- [ ] Test load times

#### **Day 5-7: Testing & Bug Fixes**
- [ ] Test all user flows
- [ ] Test error scenarios
- [ ] Fix bugs and issues
- [ ] Optimize Lambda cold starts
- [ ] Security audit

---

### Phase 6: Documentation & Deployment (Week 6)

#### **Day 1-3: Documentation**
- [ ] Complete architecture documentation
- [ ] Write API documentation
- [ ] Create user guide
- [ ] Document deployment process
- [ ] Create presentation slides

#### **Day 4-5: Final Testing**
- [ ] End-to-end testing
- [ ] Load testing
- [ ] Security testing
- [ ] User acceptance testing
- [ ] Performance benchmarking

#### **Day 6-7: Deployment & Demo**
- [ ] Deploy to production
- [ ] Create demo account
- [ ] Prepare demo presentation
- [ ] Create video demonstration
- [ ] Final submission preparation

---

## Cost Estimation

### AWS Free Tier (First 12 Months)

| Service | Free Tier | Expected Usage | Cost |
|---------|-----------|----------------|------|
| **Lambda** | 1M requests/month | 50K requests | $0.00 |
| **API Gateway** | 1M requests/month | 50K requests | $0.00 |
| **S3** | 5GB storage | 2GB | $0.00 |
| **DynamoDB** | 25GB storage | 1GB | $0.00 |
| **Cognito** | 50K MAU | 10 users | $0.00 |
| **CloudFront** | 1TB data transfer | 10GB | $0.00 |
| **Rekognition** | 5K images/month | 1K images | $0.00 |

**Estimated Monthly Cost: $0 - $5** (within Free Tier)

### Beyond Free Tier (Estimated)

| Service | Unit Cost | Expected Usage | Monthly Cost |
|---------|-----------|----------------|--------------|
| **Lambda** | $0.20 per 1M requests | 100K requests | $0.02 |
| **S3** | $0.023 per GB | 10GB | $0.23 |
| **DynamoDB** | $0.25 per GB | 2GB | $0.50 |
| **CloudFront** | $0.085 per GB | 50GB transfer | $4.25 |
| **Rekognition** | $1 per 1K images | 5K images | $5.00 |

**Estimated Monthly Cost: $10 - $15** (for moderate usage)

### Cost Optimization Strategies

1. **S3 Lifecycle Policies:** Move old images to Glacier
2. **CloudFront Caching:** Reduce S3 data transfer
3. **Lambda Memory Optimization:** Right-size memory allocation
4. **DynamoDB On-Demand:** Pay per request instead of provisioned
5. **Image Compression:** Reduce storage and transfer costs

---

## Expected Outcomes

### Functional Outcomes

✅ **User Authentication System**
- Users can register, login, and manage sessions
- Secure JWT-based authentication
- Password reset functionality

✅ **Image Upload System**
- Users can upload multiple images
- Direct upload to S3 using pre-signed URLs
- Progress indicators and error handling

✅ **Automatic Image Processing**
- Uploaded images automatically resized (3 versions)
- Watermarks applied to images
- Format conversion to WebP for optimization

✅ **AI-Powered Tagging**
- Automatic object and scene detection
- Text extraction from images (OCR)
- Face detection and counting
- Content moderation flags

✅ **Photo Gallery Interface**
- Grid view of all uploaded images
- Full-screen image viewer
- Search by tags, filename, or date
- Filter and sort capabilities

✅ **Metadata Management**
- All image metadata stored in DynamoDB
- Fast retrieval and querying
- EXIF data preservation
- Custom tagging support

✅ **Global Content Delivery**
- Fast image loading via CloudFront
- Reduced latency for users worldwide
- Automatic caching and invalidation

### Technical Outcomes

✅ **Serverless Architecture**
- Zero server management required
- Automatic scaling based on demand
- Pay-per-use cost model

✅ **Event-Driven Design**
- S3 events trigger processing automatically
- Asynchronous processing pipeline
- Decoupled microservices

✅ **High Availability**
- Multi-AZ deployment across AWS
- Automatic failover mechanisms
- 99.99% uptime SLA

✅ **Security Best Practices**
- Encryption at rest and in transit
- IAM role-based access control
- Input validation and sanitization

### Learning Outcomes

✅ **AWS Services Mastery**
- Hands-on experience with 7+ AWS services
- Understanding of serverless architectures
- Cloud cost optimization strategies

✅ **Full-Stack Development**
- Frontend development (React/Vue/Vanilla JS)
- Backend API design (REST)
- Database design (NoSQL)

✅ **AI/ML Integration**
- Practical use of Amazon Rekognition
- Understanding of computer vision applications
- Implementing AI features in web apps

✅ **DevOps Practices**
- Infrastructure as Code (optional: CloudFormation)
- CI/CD pipeline (optional: AWS CodePipeline)
- Monitoring and logging (CloudWatch)

---

## Technical Workflow

### 1. User Registration Flow

```
User Fills Form → Submit → API Gateway → Lambda → Cognito
                                                      ↓
User ← Email ← SES ← Cognito ← Verification Code
                                                      ↓
User Clicks Link → Verify → Cognito → Account Active
```

### 2. Image Upload Workflow

```
User Selects Image → Request Upload URL → API Gateway
                                              ↓
                                         Lambda validates
                                              ↓
                                    Generates pre-signed URL
                                              ↓
User ← Returns URL ← API Gateway ← Lambda
  ↓
Uploads to S3 directly (no server intermediary)
  ↓
S3 Event Notification
  ↓
Lambda ProcessImage triggered
  ↓
Download → Process → Upload → Update DB
```

### 3. Image Viewing Workflow

```
User Opens Gallery → API Request → API Gateway → Lambda
                                                    ↓
                                              Query DynamoDB
                                                    ↓
                                              Return metadata
                                                    ↓
Frontend ← JSON Response ← API Gateway ← Lambda
  ↓
Renders images using CloudFront URLs
  ↓
User clicks image → Full image loaded from CloudFront
```

### 4. Search Workflow

```
User Enters Search → API Request with query → API Gateway
                                                  ↓
                                             Lambda
                                                  ↓
                                       Query DynamoDB by tags
                                                  ↓
                                       Filter results
                                                  ↓
Frontend ← Matching images ← API Gateway ← Lambda
```

---

## Scalability and Performance

### Scalability Features

#### **Automatic Scaling**
- **Lambda:** Scales to 1000+ concurrent executions
- **API Gateway:** Handles 10,000+ requests per second
- **DynamoDB:** Auto-scales based on traffic
- **CloudFront:** Global edge network handles millions of users

#### **Performance Optimizations**

**Frontend:**
- Lazy loading of images
- Progressive image rendering
- Bundle splitting and code optimization
- Service worker for offline support (PWA)

**Backend:**
- Lambda warm start optimization
- DynamoDB query optimization with GSI
- S3 Transfer Acceleration for faster uploads
- CloudFront edge caching

**Database:**
- Efficient partition key design
- Global Secondary Indexes for common queries
- DynamoDB Accelerator (DAX) for caching (optional)

### Load Testing Results (Expected)

| Metric | Target | Strategy |
|--------|--------|----------|
| **API Response Time** | < 200ms | Lambda optimization |
| **Image Load Time** | < 500ms | CloudFront caching |
| **Concurrent Users** | 1000+ | Auto-scaling |
| **Upload Throughput** | 100 images/min | Pre-signed URLs |
| **Search Query Time** | < 100ms | DynamoDB GSI |

---

## Security Considerations

### Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| **Unauthorized Access** | Cognito authentication, JWT validation |
| **DDoS Attack** | CloudFront, API Gateway throttling |
| **SQL Injection** | DynamoDB (NoSQL), input validation |
| **XSS** | Content Security Policy, sanitization |
| **CSRF** | SameSite cookies, CORS configuration |
| **Data Breach** | S3/DynamoDB encryption, IAM policies |
| **Malicious Uploads** | File type validation, Rekognition moderation |

---

## Future Enhancements

### Phase 2 Features (Post-Submission)

1. **Social Features**
   - Public galleries
   - Image sharing
   - Comments and likes

2. **Advanced Processing**
   - Image filters (Instagram-style)
   - Auto-enhance (brightness, contrast)
   - Background removal

3. **Organization**
   - Albums/Collections
   - Favorites
   - Tags management UI

4. **Analytics**
   - View counts
   - Popular images
   - Storage usage dashboard

5. **Mobile App**
   - React Native or Flutter
   - Push notifications
   - Offline support

6. **Collaboration**
   - Shared albums
   - Multi-user access
   - Role-based permissions

---

## Conclusion

This **Serverless Photo Gallery** project demonstrates a comprehensive understanding of modern cloud architecture, serverless computing, and AI integration. The project showcases:

- **Technical Depth:** Integration of 7+ AWS services in a cohesive architecture
- **Practical Application:** Real-world use case with production-ready features
- **Innovation:** AI-powered tagging using Amazon Rekognition
- **Best Practices:** Security, scalability, and cost optimization
- **Learning Value:** Hands-on experience with cutting-edge cloud technologies

The project is well-suited for DA3 submission as it demonstrates both theoretical knowledge and practical implementation skills in cloud computing, making it an excellent showcase of AWS capabilities and serverless architecture patterns.

---

## References and Resources

### AWS Documentation
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Amazon DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [Amazon Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Amazon Rekognition Developer Guide](https://docs.aws.amazon.com/rekognition/)
- [Amazon API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Amazon CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)

### Tutorials and Guides
- AWS Serverless Application Model (SAM)
- AWS Amplify for frontend integration
- Boto3 Python SDK documentation
- AWS SDK for JavaScript

### Tools and Libraries
- **Image Processing:** Pillow (Python), Sharp (Node.js)
- **Frontend:** React.js, Vue.js, or Vanilla JavaScript
- **Authentication:** AWS Amplify SDK, amazon-cognito-identity-js
- **API Client:** Axios, Fetch API
- **Testing:** Jest, Pytest, Postman

---

**Document Version:** 1.0  
**Last Updated:** October 28, 2025  
**Project Status:** Ready for Implementation

---

## Team Signatures

| Name | Student ID | Signature |
|------|------------|-----------|
| Adithya Sankar Menon | 23BRS1079 | _____________ |
| Karthick Swaminathan | 23BRS1063 | _____________ |
| Sambari Bhuvan | 23BRS1189 | _____________ |

**Submitted to:** [Professor Name]  
**Course:** [Course Code]  
**Date:** October 28, 2025
