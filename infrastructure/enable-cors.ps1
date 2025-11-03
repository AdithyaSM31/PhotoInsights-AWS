# Enable CORS for all API Gateway resources
$API_ID = "fjr24hbqvb"
$RESOURCES = @("m17kxe", "ye8t2t", "p9s8z1", "hhcp8n")

foreach ($resourceId in $RESOURCES) {
    Write-Host "Enabling CORS for resource $resourceId..." -ForegroundColor Cyan
    
    # Method response for OPTIONS
    aws apigateway put-method-response `
      --rest-api-id $API_ID `
      --resource-id $resourceId `
      --http-method OPTIONS `
      --status-code 200 `
      --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":false,\"method.response.header.Access-Control-Allow-Methods\":false,\"method.response.header.Access-Control-Allow-Origin\":false}'
    
    # Integration response for OPTIONS with CORS headers
    aws apigateway put-integration-response `
      --rest-api-id $API_ID `
      --resource-id $resourceId `
      --http-method OPTIONS `
      --status-code 200 `
      --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,Authorization'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'GET,POST,DELETE,OPTIONS'"'"'\",\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\"}'
}

Write-Host "`nCORS enabled! Redeploying API..." -ForegroundColor Green
aws apigateway create-deployment --rest-api-id $API_ID --stage-name prod --description "CORS enabled"

Write-Host "`nAPI deployed with CORS support!" -ForegroundColor Green
