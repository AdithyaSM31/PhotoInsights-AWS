# Lambda Function: DeleteImage

## Purpose
Delete an image and all its versions from S3 buckets and DynamoDB database.

## API Endpoint

**DELETE** `/images/{imageId}`

**Headers:**
- `Authorization: Bearer {JWT_TOKEN}` (from Cognito)

**Path Parameters:**
- `imageId` (required) - UUID of the image to delete

**Example Request:**
```
DELETE /images/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer eyJraWQiOiJ...
```

**Response (Success):**
```json
{
  "message": "Image deleted successfully",
  "imageId": "550e8400-e29b-41d4-a716-446655440000",
  "deletedFiles": {
    "original": true,
    "processed": true,
    "metadata": true
  }
}
```

**Response (Not Found):**
```json
{
  "error": "Image not found",
  "message": "Image 550e8400... does not exist or does not belong to user"
}
```

## Configuration

### Environment Variables
- `UPLOADS_BUCKET` - S3 bucket for original uploads (default: photogallery-uploads-23brs1079)
- `PROCESSED_BUCKET` - S3 bucket for processed images (default: photogallery-processed-23brs1079)
- `DYNAMODB_TABLE` - DynamoDB table name (default: PhotoGallery-Images)

### IAM Permissions Required
- `dynamodb:GetItem` - Verify image ownership
- `dynamodb:DeleteItem` - Delete metadata record
- `s3:DeleteObject` - Delete from uploads bucket
- `s3:DeleteObject` - Delete from processed bucket

### Lambda Configuration
- **Runtime:** Python 3.11
- **Memory:** 256 MB
- **Timeout:** 10 seconds
- **Handler:** lambda_function.lambda_handler

## Deletion Process

### Step 1: Verify Ownership
1. Query DynamoDB for image metadata
2. Check if image belongs to requesting user
3. Return 404 if not found or unauthorized

### Step 2: Delete from S3
Deletes these files from S3:
- **Original:** `uploads/{userId}/{imageId}-{timestamp}-{filename}`
- **Thumbnail:** `processed/{userId}/thumb-{imageId}.jpg` (150x150)
- **Medium:** `processed/{userId}/med-{imageId}.jpg` (800x800)
- **Large:** `processed/{userId}/{imageId}.webp` (full size)

### Step 3: Delete from DynamoDB
- Remove metadata record from `PhotoGallery-Images` table
- This includes: image name, size, dimensions, tags, AI analysis

## Security Features

### Ownership Verification
- **Before deletion**, function queries DynamoDB to verify the image belongs to the user
- Uses userId from Cognito JWT token
- Prevents users from deleting other users' images

### Atomic Operations
- DynamoDB delete is atomic
- S3 deletes are idempotent (safe to retry)
- If S3 file doesn't exist, operation continues

### Error Handling
- Continues deleting remaining files even if one fails
- Logs all deletion attempts
- Returns success if DynamoDB record deleted

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Image deleted |
| 400 | Bad Request - Missing imageId or authorization |
| 404 | Not Found - Image doesn't exist or wrong owner |
| 500 | Internal Server Error |

## Client Usage Example

### JavaScript/Fetch
```javascript
async function deleteImage(imageId) {
  const response = await fetch(
    `https://api.example.com/images/${imageId}`, 
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${jwtToken}`
      }
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  const result = await response.json();
  console.log(result.message); // "Image deleted successfully"
  return result;
}

// Usage with confirmation
async function deleteWithConfirmation(imageId, imageName) {
  if (confirm(`Delete "${imageName}"? This cannot be undone.`)) {
    try {
      await deleteImage(imageId);
      alert('Image deleted successfully');
      refreshGallery();
    } catch (error) {
      alert(`Failed to delete: ${error.message}`);
    }
  }
}
```

### React Component
```jsx
const ImageCard = ({ image }) => {
  const [deleting, setDeleting] = useState(false);
  
  const handleDelete = async () => {
    if (!confirm(`Delete "${image.imageName}"?`)) return;
    
    setDeleting(true);
    try {
      await fetch(`${API_URL}/images/${image.imageId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
      
      // Remove from UI
      onImageDeleted(image.imageId);
      toast.success('Image deleted');
    } catch (error) {
      toast.error('Delete failed');
    } finally {
      setDeleting(false);
    }
  };
  
  return (
    <div className="image-card">
      <img src={image.urls.thumbnail} alt={image.imageName} />
      <button 
        onClick={handleDelete} 
        disabled={deleting}
        className="delete-btn"
      >
        {deleting ? 'Deleting...' : 'Delete'}
      </button>
    </div>
  );
};
```

## Local Testing

```bash
python lambda_function.py
```

## Deployment

Package and deploy:
```bash
cd lambda-functions/delete-image
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force

aws lambda create-function \
  --function-name PhotoGallery-DeleteImage \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/PhotoGalleryLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --environment "Variables={UPLOADS_BUCKET=photogallery-uploads-23brs1079,PROCESSED_BUCKET=photogallery-processed-23brs1079,DYNAMODB_TABLE=PhotoGallery-Images}" \
  --timeout 10 \
  --memory-size 256 \
  --description "Delete image from S3 and DynamoDB"
```

## Testing

### Test with AWS CLI
```bash
aws lambda invoke \
  --function-name PhotoGallery-DeleteImage \
  --payload '{"pathParameters":{"imageId":"test-123"},"requestContext":{"authorizer":{"claims":{"sub":"user-123"}}}}' \
  response.json
```

### Test with Postman
1. Set method to `DELETE`
2. URL: `https://your-api.execute-api.us-east-1.amazonaws.com/prod/images/{imageId}`
3. Headers: `Authorization: Bearer {token}`
4. Expected: 200 with success message

## Performance

- **Execution Time:** ~200-500ms
- **Cost per Delete:** ~$0.0000002 (Lambda) + ~$0.000005 (S3) + ~$0.0000025 (DynamoDB)
- **S3 Operations:** 4 DELETE requests (1 original + 3 processed)
- **DynamoDB Operations:** 1 GetItem + 1 DeleteItem

## Important Notes

### Permanent Deletion
- **This operation is irreversible**
- All image versions are permanently deleted
- Metadata cannot be recovered
- Consider implementing soft delete for production

### S3 Versioning
- If S3 versioning is enabled, creates delete markers
- Previous versions still stored (incurs cost)
- Use S3 lifecycle policies to permanently delete old versions

### Batch Deletion
- This function deletes one image at a time
- For bulk deletion, call multiple times or create separate batch function
- Consider using S3 batch operations for large-scale deletions

## Future Enhancements

- [ ] Soft delete (mark as deleted, keep files)
- [ ] Restore deleted images (within time window)
- [ ] Batch delete multiple images
- [ ] Delete user's entire gallery
- [ ] CloudWatch metrics for deletions
- [ ] SNS notification on deletion
