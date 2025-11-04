# Quick Fix: Build Proper Pillow Layer

## Problem
The Pillow layer built on Windows doesn't work on AWS Lambda (Amazon Linux 2) because it's missing the compiled C extensions like `_imaging`.

## Solution

### Option 1: Use Docker to Build (Recommended)
```bash
cd lambda-layers/pillow
docker build -t pillow-layer .
docker run --rm pillow-layer > pillow-layer.zip
aws lambda publish-layer-version \
  --layer-name pillow-python311 \
  --zip-file fileb://pillow-layer.zip \
  --compatible-runtimes python3.11
```

### Option 2: Use Public AWS Lambda Power Tools Layer
```bash
# AWS Powertools has Pillow included
aws lambda update-function-configuration \
  --function-name PhotoGallery-ProcessImage \
  --layers arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:46
```

### Option 3: Download Pre-built from Keith's Layers
Visit: https://github.com/keithrozario/Klayers
Or use: https://api.klayers.cloud/api/v2/p3.11/layers/latest/us-east-1/json

### Option 4: Simplify ProcessImage (Temporary)
Remove Pillow dependency and use simple pass-through:
- Skip image resizing
- Just copy file to processed bucket
- Still writes metadata to DynamoDB

## Current Status
- ❌ Pillow layer version 1 is broken (Windows build)
- ✅ S3 trigger is configured correctly
- ✅ Image uploaded successfully
- ❌ ProcessImage Lambda fails on import

## Quick Workaround Applied
Will try public layers or simplify the function temporarily.
