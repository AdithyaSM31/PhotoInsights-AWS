# API Gateway Summary

## API Details
- **API Name:** PhotoGalleryAPI
- **API ID:** fjr24hbqvb
- **Region:** us-east-1
- **Stage:** prod
- **Base URL:** https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod

## Authentication
- **Type:** Cognito User Pools
- **Authorizer ID:** 1uduie
- **User Pool:** us-east-1_EhhMCMyy3
- **Header:** Authorization: Bearer {JWT_TOKEN}

## Endpoints

### 1. POST /upload
- **Lambda:** PhotoGallery-GetUploadUrl
- **Purpose:** Get pre-signed URL for image upload
- **Auth:** Required (Cognito JWT)
- **Request Body:**
```json
{
  "filename": "sunset.jpg",
  "contentType": "image/jpeg",
  "fileSize": 2458624
}
```
- **Response:**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/...",
  "imageId": "uuid",
  "expiresIn": 300
}
```

### 2. GET /images
- **Lambda:** PhotoGallery-GetImages
- **Purpose:** Get user's photo gallery
- **Auth:** Required
- **Query Parameters:**
  - `limit` (optional, default: 20)
  - `sortOrder` (optional, default: desc)
  - `lastKey` (optional, pagination token)
- **Response:**
```json
{
  "images": [...],
  "count": 20,
  "hasMore": true,
  "nextKey": "..."
}
```

### 3. GET /images/search
- **Lambda:** PhotoGallery-SearchImages
- **Purpose:** Search images by tags, date, etc.
- **Auth:** Required
- **Query Parameters:**
  - `tags` (comma-separated)
  - `filename` (search string)
  - `dateFrom`, `dateTo` (dates)
  - `hasFaces`, `hasText` (boolean)
  - `limit`, `sortOrder`, `lastKey`
- **Response:** Same as GET /images

### 4. DELETE /images/{imageId}
- **Lambda:** PhotoGallery-DeleteImage
- **Purpose:** Delete an image
- **Auth:** Required
- **Path Parameter:** imageId (UUID)
- **Response:**
```json
{
  "message": "Image deleted successfully",
  "imageId": "uuid"
}
```

## CORS Configuration
- **Allowed Origins:** * (all origins)
- **Allowed Methods:** GET, POST, DELETE, OPTIONS
- **Allowed Headers:** Content-Type, Authorization
- Lambda functions return CORS headers in responses (AWS_PROXY integration)

## Testing with cURL

### 1. Get Upload URL
```bash
curl -X POST \
  https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg","contentType":"image/jpeg","fileSize":100000}'
```

### 2. Get Images
```bash
curl -X GET \
  "https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod/images?limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Search Images
```bash
curl -X GET \
  "https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod/images/search?tags=sunset,beach" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Delete Image
```bash
curl -X DELETE \
  "https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod/images/IMAGE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Deployment History
- Initial deployment: 2025-11-03 (ID: xu4p0q)
- CORS update: 2025-11-03 (ID: k2q7eh)

## Next Steps
1. ✅ API Gateway created and deployed
2. ⬜ Test endpoints with Postman/cURL
3. ⬜ Build frontend application
4. ⬜ Add CloudFront CDN
5. ⬜ Production testing

## Monitoring
- **CloudWatch Logs:** API Gateway execution logs
- **Metrics:** Latency, 4XX/5XX errors, request count
- **X-Ray:** Distributed tracing (can be enabled)

## Cost Estimation
- **API Gateway:** $3.50 per million requests
- **Data Transfer:** $0.09/GB
- **Expected monthly cost:** ~$1-5 for moderate usage
