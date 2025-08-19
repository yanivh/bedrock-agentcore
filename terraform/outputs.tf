output "s3_bucket_name" {
  description = "The name of the S3 bucket."
  value       = aws_s3_bucket.example.bucket
}

# Lambda function outputs
output "lambda_function_arn" {
  description = "The ARN of the Lambda function."
  value       = aws_lambda_function.bedrock_agentcore.arn
}

output "lambda_function_name" {
  description = "The name of the Lambda function."
  value       = aws_lambda_function.bedrock_agentcore.function_name
}

output "api_gateway_url" {
  description = "The URL of the API Gateway."
  value       = "${aws_api_gateway_stage.prod.invoke_url}/"
}

output "lambda_role_arn" {
  description = "The ARN of the Lambda execution role."
  value       = aws_iam_role.lambda_role.arn
}

# Cognito outputs for MCP authentication
output "cognito_user_pool_id" {
  description = "The ID of the Cognito User Pool for MCP authentication"
  value       = aws_cognito_user_pool.mcp_auth.id
}

output "cognito_client_id" {
  description = "The ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.mcp_client.id
}

output "cognito_discovery_url" {
  description = "The OpenID Connect discovery URL for the Cognito User Pool"
  value       = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.mcp_auth.id}/.well-known/openid-configuration"
}

output "test_user_credentials" {
  description = "Test user credentials for MCP authentication"
  value = {
    username = aws_cognito_user.test_user.username
    email    = var.test_user_email
  }
  sensitive = false
} 