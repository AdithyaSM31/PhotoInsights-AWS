# Fixing CORS Issues

## Problem
The frontend shows "Failed to fetch" error when loading the gallery. This is a CORS (Cross-Origin Resource Sharing) issue.

## Root Causes
1. **API Gateway CORS not configured** - Preflight OPTIONS requests need proper handling
2. **S3 Bucket not public** - Processed images bucket needs public read access ✅ FIXED

## Solutions Applied

### 1. S3 Bucket Policy (✅ Completed)
Made the processed images bucket publicly readable:
```bash
aws s3api delete-public-access-block --bucket photogallery-processed-23brs1079
aws s3api put-bucket-policy --bucket photogallery-processed-23brs1079 --policy file://processed-bucket-policy.json
```

### 2. API Gateway CORS (⚠️ Needs Manual Fix)

The Lambda functions already return proper CORS headers:
```python
{
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS'
}
```

However, **API Gateway needs OPTIONS method for CORS preflight requests**.

## Manual Fix via AWS Console

Since PowerShell JSON escaping is causing issues, follow these steps in AWS Console:

### Step 1: Open API Gateway Console
1. Go to AWS Console → API Gateway
2. Click on `PhotoGalleryAPI` (ID: fjr24hbqvb)

### Step 2: Enable CORS for each resource

For **each** of these resources:
- `/upload`
- `/images`
- `/images/search`
- `/images/{imageId}`

Do the following:

1. Click on the resource
2. Click **Actions** → **Enable CORS**
3. In the Enable CORS dialog:
   - **Access-Control-Allow-Origin**: `*`
   - **Access-Control-Allow-Headers**: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
   - **Access-Control-Allow-Methods**: Check all methods (GET, POST, DELETE, OPTIONS)
4. Click **Enable CORS and replace existing CORS headers**
5. Click **Yes, replace existing values**

### Step 3: Deploy API
1. Click **Actions** → **Deploy API**
2. Deployment stage: `prod`
3. Description: "Enable CORS for all endpoints"
4. Click **Deploy**

### Step 4: Test
1. Refresh your photo gallery website
2. Sign in
3. The gallery should now load without "Failed to fetch" error

## Alternative: Using AWS CLI (if PowerShell issues resolved)

```bash
# For /upload endpoint
aws apigateway put-integration \
  --rest-api-id fjr24hbqvb \
  --resource-id m17kxe \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json":"{\"statusCode\": 200}"}'

aws apigateway put-integration-response \
  --rest-api-id fjr24hbqvb \
  --resource-id m17kxe \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters '{"method.response.header.Access-Control-Allow-Headers":"'"'"'Content-Type,Authorization'"'"'","method.response.header.Access-Control-Allow-Methods":"'"'"'POST,OPTIONS'"'"'","method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}'
```

Repeat for other endpoints (ye8t2t, p9s8z1, hhcp8n).

## Testing CORS
Once configured, test with:
```powershell
# Should return CORS headers
Invoke-WebRequest -Uri "https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod/images" `
  -Method OPTIONS `
  -Headers @{"Origin"="http://photogallery-website-23brs1079.s3-website-us-east-1.amazonaws.com"}
```

## Why This Matters
- Browsers send **preflight OPTIONS requests** before actual requests
- Without OPTIONS handler, browser blocks the actual request
- This causes "Failed to fetch" or "CORS policy" errors in console

## Status
- ✅ Lambda functions return CORS headers
- ✅ S3 bucket is publicly accessible
- ⚠️ API Gateway OPTIONS methods need manual configuration
- ⬜ After fix, test end-to-end upload/view workflow
