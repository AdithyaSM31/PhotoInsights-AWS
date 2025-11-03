# Lambda Function: ProcessImage

## Purpose
Automatically process uploaded images: resize to multiple sizes, add watermark, optimize format.

## Trigger
**S3 Event** - Automatically triggered when files uploaded to `uploads/` folder in uploads bucket.

## Processing Pipeline

### Input
Original image uploaded to: `s3://uploads-bucket/uploads/{userId}/{imageId}-{timestamp}-{filename}`

### Output (3 versions created)
1. **Thumbnail** - 150x150 JPEG (square crop, 85% quality)
   - `processed/{userId}/thumb-{imageId}.jpg`
   - Used for: Gallery grid view
   
2. **Medium** - 800x800 max JPEG (aspect ratio maintained, 85% quality)
   - `processed/{userId}/med-{imageId}.jpg`
   - Used for: Preview/lightbox
   
3. **Large** - 1920x1920 max WebP (with watermark, 90% quality)
   - `processed/{userId}/{imageId}.webp`
   - Used for: Full-size viewing

### Metadata Update
Updates DynamoDB with:
- Image dimensions
- File size
- Processed URLs for all 3 versions
- Processing status
- Timestamp

## Configuration

### Environment Variables
- `UPLOADS_BUCKET` - Source S3 bucket (default: photogallery-uploads-23brs1079)
- `PROCESSED_BUCKET` - Destination S3 bucket (default: photogallery-processed-23brs1079)
- `DYNAMODB_TABLE` - Metadata table (default: PhotoGallery-Images)
- `WATERMARK_TEXT` - Watermark text (default: "PhotoGallery")

### IAM Permissions Required
- `s3:GetObject` - Read from uploads bucket
- `s3:PutObject` - Write to processed bucket
- `dynamodb:PutItem` - Store metadata

### Lambda Configuration
- **Runtime:** Python 3.11
- **Memory:** 1024 MB (image processing is memory-intensive)
- **Timeout:** 60 seconds (for large images)
- **Handler:** lambda_function.lambda_handler
- **Layer:** Pillow (PIL) library

### Lambda Layer
Requires Pillow library for image manipulation. Two options:

**Option 1: Use Public Layer (Recommended)**
```bash
# Klayers Pillow for Python 3.11 (us-east-1)
arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-pillow:17
```

**Option 2: Create Your Own Layer**
```powershell
# See lambda-layers/LAYER_SETUP.md for instructions
pip install --target python Pillow
Compress-Archive -Path python -DestinationPath pillow-layer.zip
aws lambda publish-layer-version --layer-name pillow-python311 ...
```

## Image Processing Details

### Thumbnail Creation
- **Method:** Center crop to square
- **Size:** 150x150 pixels
- **Format:** JPEG
- **Quality:** 85%
- **Use case:** Gallery grid, list views

### Medium Resize
- **Method:** Scale maintaining aspect ratio
- **Max size:** 800x800 pixels
- **Format:** JPEG  
- **Quality:** 85%
- **Use case:** Image preview, lightbox

### Large Optimization
- **Method:** Scale maintaining aspect ratio
- **Max size:** 1920x1920 pixels
- **Format:** WebP (better compression)
- **Quality:** 90%
- **Watermark:** Bottom-right corner
- **Use case:** Full-size viewing

### Format Conversion
- Converts RGBA/PNG to RGB with white background
- Handles transparency properly
- Optimizes during save

## Watermarking

- **Position:** Bottom-right corner (10px padding)
- **Text:** Configurable via `WATERMARK_TEXT` env var
- **Style:** White text with black shadow
- **Transparency:** Semi-transparent for subtlety
- **Font:** Default PIL font (can use custom .ttf)

## Deployment

### Step 1: Package function
```powershell
cd lambda-functions/process-image
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force
```

### Step 2: Create Lambda function
```powershell
aws lambda create-function `
  --function-name PhotoGallery-ProcessImage `
  --runtime python3.11 `
  --role arn:aws:iam::799016889364:role/PhotoGalleryLambdaRole `
  --handler lambda_function.lambda_handler `
  --zip-file fileb://function.zip `
  --environment "Variables={UPLOADS_BUCKET=photogallery-uploads-23brs1079,PROCESSED_BUCKET=photogallery-processed-23brs1079,DYNAMODB_TABLE=PhotoGallery-Images,WATERMARK_TEXT=PhotoGallery}" `
  --timeout 60 `
  --memory-size 1024 `
  --layers arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-pillow:17 `
  --description "Process uploaded images - resize, watermark, optimize"
```

### Step 3: Configure S3 Trigger
```powershell
# Add permission for S3 to invoke Lambda
aws lambda add-permission `
  --function-name PhotoGallery-ProcessImage `
  --principal s3.amazonaws.com `
  --statement-id s3-trigger `
  --action lambda:InvokeFunction `
  --source-arn arn:aws:s3:::photogallery-uploads-23brs1079

# Create S3 event notification (see s3-event-config.json)
aws s3api put-bucket-notification-configuration `
  --bucket photogallery-uploads-23brs1079 `
  --notification-configuration file://s3-event-config.json
```

### S3 Event Configuration (`s3-event-config.json`)
```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "ProcessImageTrigger",
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:799016889364:function:PhotoGallery-ProcessImage",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "uploads/"
            },
            {
              "Name": "suffix",
              "Value": ".jpg"
            }
          ]
        }
      }
    }
  ]
}
```

## Testing

### Manual Invocation (Simulated S3 Event)
```powershell
aws lambda invoke `
  --function-name PhotoGallery-ProcessImage `
  --payload file://test-event.json `
  response.json
```

### Real Test
1. Get pre-signed URL from GetUploadUrl Lambda
2. Upload an image to S3 using the URL
3. ProcessImage Lambda automatically triggered
4. Check processed bucket for 3 new images
5. Check DynamoDB for metadata

## Performance

- **Cold start:** ~3-5 seconds (with layer)
- **Warm execution:** ~1-3 seconds per image
- **Memory usage:** ~200-500 MB (depends on image size)
- **Recommended memory:** 1024 MB for large images

## Error Handling

### Common Issues
1. **Out of memory** - Increase Lambda memory to 1536 MB
2. **Timeout** - Increase timeout to 90 seconds for very large images
3. **Invalid format** - Function handles JPEG, PNG, GIF, WebP
4. **Missing layer** - Verify Pillow layer is attached

### Logs
Check CloudWatch Logs: `/aws/lambda/PhotoGallery-ProcessImage`

## Cost Estimation

Per 1000 images processed:
- **Lambda compute:** ~$0.02 (1024 MB, 2 sec avg)
- **S3 PUT requests:** ~$0.015 (3 processed + 1 metadata)
- **Data transfer:** Free (within same region)
- **Total:** ~$0.035 per 1000 images

## Image Quality Examples

| Version | Dimensions | Format | Size (approx) | Use Case |
|---------|-----------|--------|---------------|----------|
| Original | 4000x3000 | JPEG | 3 MB | Stored only |
| Thumbnail | 150x150 | JPEG | 8 KB | Gallery grid |
| Medium | 800x600 | JPEG | 80 KB | Preview |
| Large | 1920x1440 | WebP | 200 KB | Full view |

**Total storage:** ~3.3 MB per image (original + 3 versions)

## Future Enhancements

- [ ] Face detection for smart cropping
- [ ] EXIF data preservation
- [ ] Custom watermark image (logo)
- [ ] Progressive JPEG encoding
- [ ] Automatic rotation based on EXIF
- [ ] Batch processing for existing images
- [ ] Custom size configurations per user
