# Lambda Function: AnalyzeImage

## Purpose
Use Amazon Rekognition AI to automatically analyze images and generate tags, detect faces, extract text, and check content safety.

## Trigger Options
1. **Direct Invocation** - Called manually or by ProcessImage Lambda
2. **DynamoDB Stream** - Auto-triggered when new image added
3. **API Gateway** - User-initiated analysis

## AI Analysis Features

### 1. Label Detection
- Detects objects, scenes, activities, concepts
- Returns top 10 labels with confidence scores
- Examples: "sunset", "beach", "person", "outdoor", "nature"

### 2. Text Detection (OCR)
- Extracts text from images
- Detects signs, documents, captions
- Returns text with confidence and location

### 3. Face Detection
- Counts faces in image
- Analyzes age range, gender, emotions
- Detects facial features (smile, glasses, beard)
- Does NOT store face recognition data

### 4. Content Moderation
- Checks for inappropriate content
- Flags explicit, suggestive, or violent imagery
- Returns safety status

## Configuration

### Environment Variables
- `PROCESSED_BUCKET` - S3 bucket with processed images (default: photogallery-processed-23brs1079)
- `DYNAMODB_TABLE` - Metadata table (default: PhotoGallery-Images)
- `MAX_LABELS` - Maximum labels to return (default: 10)
- `MIN_CONFIDENCE` - Minimum confidence threshold (default: 80%)

### IAM Permissions Required
- `rekognition:DetectLabels` - Object/scene detection
- `rekognition:DetectText` - OCR text extraction
- `rekognition:DetectFaces` - Face analysis
- `rekognition:DetectModerationLabels` - Content moderation
- `s3:GetObject` - Read images from S3
- `dynamodb:UpdateItem` - Store analysis results

### Lambda Configuration
- **Runtime:** Python 3.11
- **Memory:** 512 MB (Rekognition needs more memory)
- **Timeout:** 30 seconds
- **Handler:** lambda_function.lambda_handler

## Event Format

### Direct Invocation
```json
{
  "imageId": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "user-123",
  "bucket": "photogallery-processed-23brs1079"
}
```

### Response
```json
{
  "statusCode": 200,
  "body": {
    "message": "Image analyzed successfully",
    "imageId": "550e8400-e29b-41d4-a716-446655440000",
    "analysis": {
      "labels": [
        {"name": "Sunset", "confidence": 98.5},
        {"name": "Sky", "confidence": 97.2},
        {"name": "Beach", "confidence": 95.8}
      ],
      "faceCount": 2,
      "hasText": true,
      "isSafe": true,
      "text": [
        {"text": "Welcome", "confidence": 99.1, "type": "LINE"}
      ],
      "faces": [
        {
          "confidence": 99.9,
          "ageRange": {"low": 25, "high": 35},
          "gender": "Male",
          "emotions": [
            {"type": "HAPPY", "confidence": 95.2}
          ],
          "smile": true,
          "eyeglasses": false
        }
      ],
      "moderation": []
    }
  }
}
```

## DynamoDB Update

Updates image metadata with:

```json
{
  "tags": ["sunset", "sky", "beach", "ocean", "water"],
  "aiAnalysis": {
    "labels": [...],
    "faceCount": 2,
    "hasText": true,
    "isSafe": true,
    "textDetections": [...],
    "faces": [...],
    "moderationFlags": []
  },
  "analysisStatus": "completed"
}
```

## Rekognition API Calls

| API | Purpose | Output | Cost per 1000 |
|-----|---------|--------|---------------|
| DetectLabels | Object/scene detection | Labels with confidence | $1.00 |
| DetectText | OCR text extraction | Text with location | $1.50 |
| DetectFaces | Face analysis | Demographics, emotions | $1.00 |
| DetectModerationLabels | Content safety | Moderation flags | $1.00 |

**Total cost:** ~$4.50 per 1000 images

## Deployment

### Package and deploy
```powershell
cd lambda-functions/analyze-image
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force

aws lambda create-function `
  --function-name PhotoGallery-AnalyzeImage `
  --runtime python3.11 `
  --role arn:aws:iam::799016889364:role/PhotoGalleryLambdaRole `
  --handler lambda_function.lambda_handler `
  --zip-file fileb://function.zip `
  --environment "Variables={PROCESSED_BUCKET=photogallery-processed-23brs1079,DYNAMODB_TABLE=PhotoGallery-Images,MAX_LABELS=10,MIN_CONFIDENCE=80}" `
  --timeout 30 `
  --memory-size 512 `
  --description "Analyze images with Amazon Rekognition AI"
```

## Testing

### Test with AWS CLI
```powershell
aws lambda invoke `
  --function-name PhotoGallery-AnalyzeImage `
  --payload file://test-event.json `
  --cli-binary-format raw-in-base64-out `
  response.json

Get-Content response.json | ConvertFrom-Json
```

### View CloudWatch Logs
```powershell
aws logs tail /aws/lambda/PhotoGallery-AnalyzeImage --follow
```

## Usage Patterns

### Pattern 1: Automatic Analysis (Recommended)
1. User uploads image → ProcessImage Lambda creates versions
2. ProcessImage invokes AnalyzeImage directly
3. AnalyzeImage updates DynamoDB with tags
4. User sees tags immediately in gallery

### Pattern 2: DynamoDB Stream Trigger
1. ProcessImage writes to DynamoDB
2. DynamoDB Stream triggers AnalyzeImage
3. AnalyzeImage updates record with tags
4. Slight delay but decoupled architecture

### Pattern 3: On-Demand Analysis
1. User clicks "Re-analyze" button
2. Frontend calls API Gateway → AnalyzeImage
3. Fresh analysis performed
4. Results returned to user

## Example Analysis Results

### Photo 1: Beach Sunset
```
Labels: sunset, sky, beach, ocean, water, cloud, horizon, dusk, nature, outdoors
Faces: 0
Text: None
Safe: ✓
```

### Photo 2: Restaurant Menu
```
Labels: text, document, food, menu, restaurant, indoor
Faces: 0
Text: "MENU", "Appetizers", "Main Course", "Desserts", prices...
Safe: ✓
```

### Photo 3: Group Photo
```
Labels: people, person, human, group, indoor, smile, happy
Faces: 5 (ages 20-60, mixed genders, mostly smiling)
Text: None
Safe: ✓
```

## Performance

- **Cold start:** ~2-3 seconds
- **Warm execution:** ~1-2 seconds per image
- **Rekognition latency:** ~500ms - 1.5s per API call
- **Memory usage:** ~256-400 MB

## Error Handling

### Common Issues
1. **Image too small** - Rekognition requires min 80x80 pixels
2. **Unsupported format** - Use JPEG, PNG, WebP
3. **Rate limiting** - Default: 50 TPS per API
4. **No faces detected** - Returns empty array (not an error)

### Confidence Thresholds
- **MIN_CONFIDENCE=80** - Good balance (default)
- **MIN_CONFIDENCE=90** - High precision, fewer results
- **MIN_CONFIDENCE=70** - More results, some false positives

## Privacy & Compliance

### Data Storage
- ✓ Analysis results stored in DynamoDB
- ✓ No images stored by Rekognition
- ✓ No face recognition/matching performed
- ✓ No biometric data retained

### GDPR/Privacy
- Face detection ≠ face recognition
- Only facial attributes analyzed (age, emotion)
- No personal identification
- User can delete all data via DeleteImage

## Future Enhancements

- [ ] Celebrity recognition (DetectCelebrities)
- [ ] Custom label detection (trained models)
- [ ] Image similarity search (SearchFacesByImage)
- [ ] Batch processing for existing images
- [ ] User feedback to improve accuracy
- [ ] Multi-language text detection
- [ ] Video analysis support
