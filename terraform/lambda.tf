# Lambda function for Bedrock AgentCore

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "bedrock-agentcore-lambda-role-${var.agent_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Bedrock AgentCore permissions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "bedrock-agentcore-lambda-policy-${var.agent_name}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:InvokeAgentRuntime"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/*",
          "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
        ]
      }
    ]
  })
}

# Lambda function
resource "aws_lambda_function" "bedrock_agentcore" {
  filename         = "bedrock_agentcore_lambda.zip"
  function_name    = "bedrock-agentcore-lambda-${var.agent_name}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  source_code_hash = filebase64sha256("bedrock_agentcore_lambda.zip")

  environment {
    variables = {
      PYTHONPATH = "/opt/python"
    }
  }

  tags = {
    Name        = "bedrock-agentcore-lambda"
    Environment = "production"
    Project     = "bedrock-agentcore"
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.bedrock_agentcore.function_name}"
  retention_in_days = 14

  tags = {
    Name        = "bedrock-agentcore-lambda-logs"
    Environment = "production"
    Project     = "bedrock-agentcore"
  }
}

# API Gateway (optional - for HTTP triggers)
resource "aws_api_gateway_rest_api" "bedrock_agentcore_api" {
  name = "bedrock-agentcore-api-${var.agent_name}"

  tags = {
    Name        = "bedrock-agentcore-api"
    Environment = "production"
    Project     = "bedrock-agentcore"
  }
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_agentcore_api.id
  parent_id   = aws_api_gateway_rest_api.bedrock_agentcore_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.bedrock_agentcore_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.bedrock_agentcore_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.bedrock_agentcore.invoke_arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.bedrock_agentcore.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.bedrock_agentcore_api.execution_arn}/*/*"
}

# API Gateway Stage
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.bedrock_agentcore_api.id
  stage_name    = "prod"

  tags = {
    Name        = "bedrock-agentcore-api-stage"
    Environment = "production"
    Project     = "bedrock-agentcore"
  }
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda,
  ]

  rest_api_id = aws_api_gateway_rest_api.bedrock_agentcore_api.id

  lifecycle {
    create_before_destroy = true
  }
} 