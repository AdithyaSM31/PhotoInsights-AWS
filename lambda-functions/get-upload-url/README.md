# Lambda Function: GetUploadUrl

## Purpose
Generates pre-signed S3 URLs for direct browser-to-S3 uploads, avoiding the need to upload through the API Gateway/Lambda.

## How It Works

1. User requests an upload URL via API Gateway
2. Lambda validates the request and file details
3. Generates a pre-signed S3 URL (valid for 5 minutes)
4. Returns URL to client
5. Client uploads directly to S3 using the URL

## API Endpoint

**POST** `/upload`

**Headers:**
- `Authorization: Bearer {JWT_TOKEN}` (from Cognito)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "filename": "sunset.jpg",
  "contentType": "image/jpeg",
  "fileSize": 2458624
}
```

**Response (Success):**
```json
{
  "uploadUrl": "https://photogallery-uploads-23brs1079.s3.amazonaws.com/uploads/user123/uuid-timestamp-sunset.jpg?...",
  "imageId": "550e8400-e29b-41d4-a716-446655440000",
  "key": "uploads/user123/uuid-timestamp-sunset.jpg",
  "bucket": "photogallery-uploads-23brs1079",
  "expiresIn": 300,
  "message": "Upload URL generated successfully"
}
```

**Response (Error):**
```json
{
  "error": "Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .webp"
}
```

## Configuration

### Environment Variables
- `UPLOADS_BUCKET` - S3 bucket name for uploads (default: photogallery-uploads-23brs1079)
- `AWS_REGION` - AWS region (default: us-east-1)

### IAM Permissions Required
- `s3:PutObject` on uploads bucket
- `s3:PutObjectAcl` on uploads bucket

### Lambda Configuration
- **Runtime:** Python 3.11
- **Memory:** 256 MB
- **Timeout:** 10 seconds
- **Handler:** lambda_function.lambda_handler

## File Validation

### Allowed File Types
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.gif` - GIF images (animated supported)
- `.webp` - WebP images

### File Size Limit
- Maximum: 10 MB

## Security

- User authentication via Cognito JWT token
- User ID extracted from JWT claims
- Pre-signed URLs expire after 5 minutes
- Files uploaded to user-specific S3 prefix: `uploads/{userId}/`
- CORS headers included for browser access

## Client Usage Example

### JavaScript/Fetch
```javascript
// 1. Get upload URL from API
const response = await fetch('https://api.example.com/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    filename: file.name,
    contentType: file.type,
    fileSize: file.size
  })
});

const { uploadUrl, imageId } = await response.json();

// 2. Upload directly to S3
await fetch(uploadUrl, {
  method: 'PUT',
  headers: {
    'Content-Type': file.type
  },
  body: file
});

console.log('Upload complete! Image ID:', imageId);
```

## Local Testing

Run the test at the bottom of `lambda_function.py`:

```bash
python lambda_function.py
```

## Deployment

See `DEPLOYMENT.md` for deployment instructions.

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - URL generated |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid JWT |
| 500 | Internal Server Error |

## Next Steps After Upload

Once the file is uploaded to S3:
1. S3 triggers the **ProcessImage** Lambda function
2. Image is resized and watermarked
3. **AnalyzeImage** Lambda runs Rekognition
4. Metadata saved to DynamoDB
5. User can view image in gallery
