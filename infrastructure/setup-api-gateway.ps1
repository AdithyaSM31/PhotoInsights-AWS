# API Gateway Configuration Script
# Sets up all endpoints with Lambda integrations and Cognito authorization

$API_ID = "fjr24hbqvb"
$AUTHORIZER_ID = "1uduie"
$REGION = "us-east-1"
$ACCOUNT_ID = "799016889364"

# Resource IDs
$UPLOAD_RESOURCE = "m17kxe"
$IMAGES_RESOURCE = "ye8t2t"
$SEARCH_RESOURCE = "p9s8z1"
$IMAGE_ID_RESOURCE = "hhcp8n"

# Lambda ARNs
$GET_UPLOAD_URL_ARN = "arn:aws:lambda:us-east-1:799016889364:function:PhotoGallery-GetUploadUrl"
$GET_IMAGES_ARN = "arn:aws:lambda:us-east-1:799016889364:function:PhotoGallery-GetImages"
$SEARCH_IMAGES_ARN = "arn:aws:lambda:us-east-1:799016889364:function:PhotoGallery-SearchImages"
$DELETE_IMAGE_ARN = "arn:aws:lambda:us-east-1:799016889364:function:PhotoGallery-DeleteImage"

Write-Host "Setting up API Gateway endpoints..." -ForegroundColor Green

# 1. POST /upload -> GetUploadUrl
Write-Host "`n1. Creating POST /upload" -ForegroundColor Cyan
aws apigateway put-method `
  --rest-api-id $API_ID `
  --resource-id $UPLOAD_RESOURCE `
  --http-method POST `
  --authorization-type COGNITO_USER_POOLS `
  --authorizer-id $AUTHORIZER_ID `
  --request-parameters "method.request.header.Authorization=true"

aws apigateway put-integration `
  --rest-api-id $API_ID `
  --resource-id $UPLOAD_RESOURCE `
  --http-method POST `
  --type AWS_PROXY `
  --integration-http-method POST `
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${GET_UPLOAD_URL_ARN}/invocations"

# Grant permission
aws lambda add-permission `
  --function-name PhotoGallery-GetUploadUrl `
  --statement-id apigateway-post-upload `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com `
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/POST/upload"

# 2. GET /images -> GetImages
Write-Host "`n2. Creating GET /images" -ForegroundColor Cyan
aws apigateway put-method `
  --rest-api-id $API_ID `
  --resource-id $IMAGES_RESOURCE `
  --http-method GET `
  --authorization-type COGNITO_USER_POOLS `
  --authorizer-id $AUTHORIZER_ID `
  --request-parameters "method.request.header.Authorization=true"

aws apigateway put-integration `
  --rest-api-id $API_ID `
  --resource-id $IMAGES_RESOURCE `
  --http-method GET `
  --type AWS_PROXY `
  --integration-http-method POST `
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${GET_IMAGES_ARN}/invocations"

aws lambda add-permission `
  --function-name PhotoGallery-GetImages `
  --statement-id apigateway-get-images `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com `
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/images"

# 3. GET /images/search -> SearchImages
Write-Host "`n3. Creating GET /images/search" -ForegroundColor Cyan
aws apigateway put-method `
  --rest-api-id $API_ID `
  --resource-id $SEARCH_RESOURCE `
  --http-method GET `
  --authorization-type COGNITO_USER_POOLS `
  --authorizer-id $AUTHORIZER_ID `
  --request-parameters "method.request.header.Authorization=true"

aws apigateway put-integration `
  --rest-api-id $API_ID `
  --resource-id $SEARCH_RESOURCE `
  --http-method GET `
  --type AWS_PROXY `
  --integration-http-method POST `
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${SEARCH_IMAGES_ARN}/invocations"

aws lambda add-permission `
  --function-name PhotoGallery-SearchImages `
  --statement-id apigateway-search-images `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com `
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/images/search"

# 4. DELETE /images/{imageId} -> DeleteImage
Write-Host "`n4. Creating DELETE /images/{imageId}" -ForegroundColor Cyan
aws apigateway put-method `
  --rest-api-id $API_ID `
  --resource-id $IMAGE_ID_RESOURCE `
  --http-method DELETE `
  --authorization-type COGNITO_USER_POOLS `
  --authorizer-id $AUTHORIZER_ID `
  --request-parameters "method.request.header.Authorization=true","method.request.path.imageId=true"

aws apigateway put-integration `
  --rest-api-id $API_ID `
  --resource-id $IMAGE_ID_RESOURCE `
  --http-method DELETE `
  --type AWS_PROXY `
  --integration-http-method POST `
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${DELETE_IMAGE_ARN}/invocations"

aws lambda add-permission `
  --function-name PhotoGallery-DeleteImage `
  --statement-id apigateway-delete-image `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com `
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/DELETE/images/*"

Write-Host "`n✓ All endpoints created!" -ForegroundColor Green

# Enable CORS for all endpoints
Write-Host "`n5. Enabling CORS..." -ForegroundColor Cyan

function Enable-CORS {
    param($ResourceId)
    
    # OPTIONS method for CORS preflight
    aws apigateway put-method `
      --rest-api-id $API_ID `
      --resource-id $ResourceId `
      --http-method OPTIONS `
      --authorization-type NONE
    
    # Mock integration for OPTIONS
    aws apigateway put-integration `
      --rest-api-id $API_ID `
      --resource-id $ResourceId `
      --http-method OPTIONS `
      --type MOCK `
      --request-templates '{\"application/json\": \"{\\\"statusCode\\\": 200}\"}'
    
    # Method response
    aws apigateway put-method-response `
      --rest-api-id $API_ID `
      --resource-id $ResourceId `
      --http-method OPTIONS `
      --status-code 200 `
      --response-parameters "method.response.header.Access-Control-Allow-Headers=true,method.response.header.Access-Control-Allow-Methods=true,method.response.header.Access-Control-Allow-Origin=true"
    
    # Integration response with CORS headers
    aws apigateway put-integration-response `
      --rest-api-id $API_ID `
      --resource-id $ResourceId `
      --http-method OPTIONS `
      --status-code 200 `
      --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,Authorization'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'GET,POST,DELETE,OPTIONS'"'"'\",\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\"}'
}

Enable-CORS $UPLOAD_RESOURCE
Enable-CORS $IMAGES_RESOURCE
Enable-CORS $SEARCH_RESOURCE
Enable-CORS $IMAGE_ID_RESOURCE

Write-Host "`n✓ CORS enabled for all endpoints!" -ForegroundColor Green

# Deploy API
Write-Host "`n6. Deploying API to 'prod' stage..." -ForegroundColor Cyan
aws apigateway create-deployment `
  --rest-api-id $API_ID `
  --stage-name prod `
  --stage-description "Production Stage" `
  --description "Initial deployment with all endpoints"

Write-Host "`n🎉 API Gateway setup complete!" -ForegroundColor Green
Write-Host "`nYour API URL:" -ForegroundColor Yellow
Write-Host "https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod" -ForegroundColor Cyan
Write-Host "`nEndpoints:" -ForegroundColor Yellow
Write-Host "  POST   /upload" -ForegroundColor White
Write-Host "  GET    /images" -ForegroundColor White
Write-Host "  GET    /images/search" -ForegroundColor White
Write-Host "  DELETE /images/{imageId}" -ForegroundColor White
