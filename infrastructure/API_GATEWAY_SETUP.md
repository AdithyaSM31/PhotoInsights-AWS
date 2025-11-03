# API Gateway Setup Guide

## Step 1: Create REST API

```powershell
aws apigateway create-rest-api `
  --name "PhotoGalleryAPI" `
  --description "Serverless Photo Gallery REST API" `
  --endpoint-configuration types=REGIONAL
```

This returns an `apiId` - save it!

## Step 2: Create Cognito Authorizer

```powershell
aws apigateway create-authorizer `
  --rest-api-id YOUR_API_ID `
  --name "CognitoAuthorizer" `
  --type COGNITO_USER_POOLS `
  --provider-arns "arn:aws:cognito-idp:us-east-1:799016889364:userpool/us-east-1_EhhMCMyy3" `
  --identity-source "method.request.header.Authorization"
```

Save the `authorizerId`!

## Step 3: Create Resources and Methods

We'll create these endpoints:
- POST /upload
- GET /images
- GET /images/search
- DELETE /images/{imageId}

## Step 4: Deploy API

```powershell
aws apigateway create-deployment `
  --rest-api-id YOUR_API_ID `
  --stage-name prod `
  --stage-description "Production Stage" `
  --description "Initial deployment"
```

## API Endpoint Structure

```
https://{api-id}.execute-api.us-east-1.amazonaws.com/prod
├── /upload (POST)           → GetUploadUrl Lambda
├── /images (GET)            → GetImages Lambda
├── /images/search (GET)     → SearchImages Lambda
└── /images/{imageId}
    └── (DELETE)             → DeleteImage Lambda
```

Let's automate this with a script!
