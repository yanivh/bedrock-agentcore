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