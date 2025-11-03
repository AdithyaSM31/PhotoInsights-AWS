# Fix CORS for API Gateway
$API_ID = "fjr24hbqvb"
$REGION = "us-east-1"

Write-Host "Adding CORS to API Gateway endpoints..." -ForegroundColor Cyan

# Resources and their IDs
$resources = @(
    @{path="/upload"; id="m17kxe"},
    @{path="/images"; id="ye8t2t"},
    @{path="/images/search"; id="p9s8z1"},
    @{path="/images/{imageId}"; id="hhcp8n"}
)

foreach ($resource in $resources) {
    Write-Host "`nConfiguring CORS for $($resource.path)..." -ForegroundColor Yellow
    
    # Create OPTIONS method
    try {
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $resource.id `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION `
            --no-cli-pager
        Write-Host "  - OPTIONS method created" -ForegroundColor Green
    } catch {
        Write-Host "  - OPTIONS method may already exist" -ForegroundColor Yellow
    }
    
    # Create MOCK integration
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $resource.id `
        --http-method OPTIONS `
        --type MOCK `
        --request-templates '{\"application/json\":\"{\\\"statusCode\\\": 200}\"}' `
        --region $REGION `
        --no-cli-pager
    Write-Host "  - MOCK integration created" -ForegroundColor Green
    
    # Create method response
    aws apigateway put-method-response `
        --rest-api-id $API_ID `
        --resource-id $resource.id `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false" `
        --region $REGION `
        --no-cli-pager
    Write-Host "  - Method response created" -ForegroundColor Green
    
    # Create integration response with CORS headers
    aws apigateway put-integration-response `
        --rest-api-id $API_ID `
        --resource-id $resource.id `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'GET,POST,DELETE,OPTIONS'"'"'\",\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\"}' `
        --region $REGION `
        --no-cli-pager
    Write-Host "  - Integration response with CORS headers created" -ForegroundColor Green
}

Write-Host "`nDeploying API to prod stage..." -ForegroundColor Cyan
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --description "CORS configuration update" `
    --region $REGION `
    --no-cli-pager

Write-Host "`nCORS configuration complete!" -ForegroundColor Green
Write-Host "API URL: https://$API_ID.execute-api.$REGION.amazonaws.com/prod" -ForegroundColor Cyan
