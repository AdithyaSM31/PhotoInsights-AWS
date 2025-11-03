# Lambda Function: GetImages

## Purpose
Retrieve user's photo gallery with metadata and image URLs from DynamoDB.

## API Endpoint

**GET** `/images`

**Headers:**
- `Authorization: Bearer {JWT_TOKEN}` (from Cognito)

**Query Parameters:**
- `limit` (optional) - Number of images to return (1-100, default: 20)
- `sortOrder` (optional) - Sort order: `asc` or `desc` (default: `desc` - newest first)
- `lastKey` (optional) - Pagination token from previous response

**Example Request:**
```
GET /images?limit=20&sortOrder=desc
```

**Response (Success):**
```json
{
  "images": [
    {
      "imageId": "550e8400-e29b-41d4-a716-446655440000",
      "imageName": "sunset.jpg",
      "uploadTimestamp": 1698765432,
      "fileSize": 2458624,
      "width": 3840,
      "height": 2160,
      "urls": {
        "thumbnail": "https://cdn.../processed/user123/thumb-uuid.jpg",
        "medium": "https://cdn.../processed/user123/med-uuid.jpg",
        "large": "https://cdn.../processed/user123/uuid.webp",
        "original": "https://cdn.../uploads/user123/uuid-sunset.jpg"
      },
      "tags": ["sunset", "beach", "ocean", "sky"],
      "aiAnalysis": {
        "faceCount": 2,
        "hasText": true,
        "moderationFlags": []
      },
      "processingStatus": "completed"
    }
  ],
  "count": 20,
  "userId": "user-id-123",
  "hasMore": true,
  "nextKey": "{base64_encoded_key}"
}
```

## Configuration

### Environment Variables
- `DYNAMODB_TABLE` - DynamoDB table name (default: PhotoGallery-Images)
- `PROCESSED_BUCKET` - S3 bucket for processed images (default: photogallery-processed-23brs1079)
- `CLOUDFRONT_DOMAIN` - CloudFront domain (optional, uses S3 URLs if not set)

### IAM Permissions Required
- `dynamodb:Query` on PhotoGallery-Images table
- `dynamodb:Query` on UploadTimeIndex GSI

### Lambda Configuration
- **Runtime:** Python 3.11
- **Memory:** 256 MB
- **Timeout:** 10 seconds
- **Handler:** lambda_function.lambda_handler

## Features

### Pagination
- Returns up to 100 images per request (default: 20)
- Provides `nextKey` for fetching next page
- `hasMore` indicates if more results available

### Sorting
- Default: Newest first (descending by upload time)
- Uses DynamoDB GSI (UploadTimeIndex) for efficient sorting
- Can sort ascending or descending

### Image URLs
- Returns 4 URLs per image:
  - **thumbnail** - 150x150px (for grid view)
  - **medium** - 800x800px (for preview)
  - **large** - Full size WebP (for full view)
  - **original** - Original uploaded file

### Data Returned
- Basic metadata (name, size, dimensions, upload time)
- AI analysis summary (face count, text detection, flags)
- Processing status
- Auto-generated tags

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Images retrieved |
| 401 | Unauthorized - Missing/invalid JWT |
| 500 | Internal Server Error |

## Client Usage Example

### JavaScript/Fetch
```javascript
async function getGallery(limit = 20, lastKey = null) {
  const url = new URL('https://api.example.com/images');
  url.searchParams.append('limit', limit);
  if (lastKey) {
    url.searchParams.append('lastKey', lastKey);
  }
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${jwtToken}`
    }
  });
  
  const data = await response.json();
  return data;
}

// Usage
const gallery = await getGallery(20);
console.log(`Loaded ${gallery.count} images`);

// Load more (pagination)
if (gallery.hasMore) {
  const nextPage = await getGallery(20, gallery.nextKey);
}
```

### Display Images
```javascript
gallery.images.forEach(image => {
  // Use thumbnail for grid
  const img = document.createElement('img');
  img.src = image.urls.thumbnail;
  img.alt = image.imageName;
  img.dataset.imageId = image.imageId;
  
  // Show tags
  console.log(`Tags: ${image.tags.join(', ')}`);
  
  // Click to view full size
  img.onclick = () => {
    viewFullImage(image.urls.large);
  };
  
  gallery.appendChild(img);
});
```

## Local Testing

```bash
python lambda_function.py
```

## Deployment

Package and deploy:
```bash
cd lambda-functions/get-images
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force
aws lambda create-function --function-name PhotoGallery-GetImages ...
```

## Performance

- **Query Time:** ~50-200ms (DynamoDB query with GSI)
- **Response Size:** ~2-10KB per image
- **Pagination:** Efficient with DynamoDB LastEvaluatedKey
- **Caching:** Consider adding CloudFront/API Gateway cache

## Future Enhancements

- [ ] Filter by tags
- [ ] Filter by date range
- [ ] Filter by processing status
- [ ] Search by filename
- [ ] Cache frequently accessed galleries
