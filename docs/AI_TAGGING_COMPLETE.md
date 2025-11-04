# AI Image Tagging - Complete Setup

## ✅ Status: WORKING!

The AI-powered automatic image tagging is now fully functional.

## What Was Fixed

### Issue 1: File Extension Mismatch
**Problem:** AnalyzeImage was looking for `.webp` files, but ProcessImage creates `.jpg` files.
**Solution:** Updated AnalyzeImage Lambda to use `.jpg` extension.

### Issue 2: Lambda Invocation Permission
**Problem:** ProcessImage couldn't invoke AnalyzeImage due to `AccessDeniedException`.
```
User: arn:aws:sts::799016889364:assumed-role/PhotoGalleryLambdaRole/PhotoGallery-ProcessImage 
is not authorized to perform: lambda:InvokeFunction
```
**Solution:** Added `lambda:InvokeFunction` permission to IAM policy.

## How It Works

### Upload Flow:
1. User uploads image → S3 `uploads/` bucket
2. **S3 Event Notification** triggers ProcessImage Lambda
3. ProcessImage:
   - Copies image to `processed/` bucket (3 versions: thumb, med, large)
   - Creates DynamoDB entry with metadata
   - **Invokes AnalyzeImage Lambda asynchronously**
4. AnalyzeImage:
   - Calls Amazon Rekognition APIs
   - Detects labels, faces, text, content moderation
   - Updates DynamoDB with tags and AI analysis

### Rekognition APIs Used:
- **DetectLabels** - Objects, scenes, activities (beach, airplane, person)
- **DetectText** - OCR text extraction
- **DetectFaces** - Face detection, age, gender, emotions
- **DetectModerationLabels** - Content safety check

## Current Tag Examples

### Beach Image (ID: 7489e8ae)
```json
["nature", "outdoors", "sky", "horizon", "scenery", "sea", "water", "beach", "coast", "shoreline"]
```

### Jet Aircraft (ID: 7fbbabcd)
```json
["aircraft", "airplane", "transportation", "vehicle", "warplane", "bomber", "jet"]
```

### Person Portrait (ID: 5284892f)
```json
["face", "happy", "head", "person", "smile", "photography", "portrait", "neck", "adult", "man"]
```

## Search Functionality

Tags are stored in lowercase and searchable via `/images/search` endpoint.

**Example Searches:**
- "beach" → Returns beach photos
- "jet" or "aircraft" → Returns airplane photos
- "person" or "happy" → Returns portrait photos
- "water, nature" → Returns images with BOTH tags

**Filters:**
- Face detection (checkbox)
- Text detection (checkbox)
- Date range (from/to)

## Configuration

### Environment Variables (AnalyzeImage Lambda):
```bash
PROCESSED_BUCKET=photogallery-processed-23brs1079
DYNAMODB_TABLE=PhotoGallery-Images
MAX_LABELS=10          # Maximum tags per image
MIN_CONFIDENCE=80      # Minimum 80% confidence for tags
```

### IAM Permissions Required:
```json
{
  "Effect": "Allow",
  "Action": [
    "rekognition:DetectLabels",
    "rekognition:DetectText",
    "rekognition:DetectFaces",
    "rekognition:DetectModerationLabels",
    "lambda:InvokeFunction"
  ],
  "Resource": "*"
}
```

## Testing

### Manual Test:
```bash
aws lambda invoke \
  --function-name PhotoGallery-AnalyzeImage \
  --cli-binary-format raw-in-base64-out \
  --payload '{"imageId":"abc123","userId":"user-id","bucket":"bucket","key":"image.jpg"}' \
  response.json
```

### Verify Tags:
```bash
aws dynamodb get-item \
  --table-name PhotoGallery-Images \
  --key '{"imageId":{"S":"abc123"},"userId":{"S":"user-id"}}' \
  --query 'Item.tags'
```

### Check Logs:
```bash
aws logs tail /aws/lambda/PhotoGallery-ProcessImage --since 10m
aws logs tail /aws/lambda/PhotoGallery-AnalyzeImage --since 10m
```

## Performance

- **ProcessImage**: ~300-600ms (copy + DynamoDB write + invoke)
- **AnalyzeImage**: ~1-2 seconds (Rekognition API calls)
- **Total**: Images available in gallery immediately, tags appear within 2-3 seconds

## Cost Estimate (per 1000 images)

- **Lambda Execution**: $0.20 (1GB memory, ~2s each)
- **Rekognition DetectLabels**: $1.00 (1000 images)
- **Rekognition DetectFaces**: $1.00 (1000 images)
- **Rekognition DetectText**: $1.50 (1000 images)
- **Rekognition DetectModerationLabels**: $1.00 (1000 images)
- **Total**: ~$4.70 per 1000 images

## Troubleshooting

### Tags Not Generated
1. Check ProcessImage logs: `aws logs tail /aws/lambda/PhotoGallery-ProcessImage`
2. Check AnalyzeImage logs: `aws logs tail /aws/lambda/PhotoGallery-AnalyzeImage`
3. Verify IAM permissions include `lambda:InvokeFunction`
4. Check S3 event notification is configured

### Empty Tags
1. Verify image file exists in S3 processed bucket
2. Check file extension matches (`.jpg` not `.webp`)
3. Ensure Rekognition has access to S3 bucket
4. Lower `MIN_CONFIDENCE` if needed (default 80%)

### Search Not Working
1. Verify tags exist in DynamoDB
2. Check SearchImages Lambda logs
3. Ensure tags are lowercase
4. Test with simple single-word search first

## Future Enhancements

- [ ] Custom labels (Amazon Rekognition Custom Labels)
- [ ] Celebrity recognition
- [ ] Unsafe content filtering/blocking
- [ ] Multi-language text detection
- [ ] Image similarity search
- [ ] Batch reprocessing for existing images
- [ ] Tag suggestions/autocomplete

## Status Summary

✅ **S3 Upload** → Working  
✅ **ProcessImage** → Working  
✅ **AnalyzeImage** → Working  
✅ **Rekognition APIs** → Working  
✅ **DynamoDB Tags** → Stored correctly  
✅ **Search** → Ready to test  
✅ **Automatic Trigger** → Working  

**All systems operational!** 🚀
