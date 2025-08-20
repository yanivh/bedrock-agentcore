resource "aws_s3_bucket" "example" {
  bucket        = "bedrock-agentcore-example-bucket-${random_id.suffix.hex}"
  force_destroy = true
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_iam_role" "agentcore_runtime_execution" {
  name = "agentcore-runtime-execution-role-${var.agent_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AssumeRolePolicy"
        Effect = "Allow"
        Principal = {
          Service = "bedrock-agentcore.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = var.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock-agentcore:${var.aws_region}:${var.account_id}:*"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "agentcore_runtime_policy" {
  name = "agentcore-runtime-policy-${var.agent_name}"
  role = aws_iam_role.agentcore_runtime_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRImageAccess"
        Effect = "Allow"
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:${var.account_id}:repository/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogStreams",
          "logs:CreateLogGroup"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${var.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${var.account_id}:log-group:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${var.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
        ]
      },
      {
        Sid    = "ECRTokenAccess"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets"
        ]
        Resource = "*"
      },
      {
        Sid    = "XRayTraceDestination"
        Effect = "Allow"
        Action = [
          "xray:UpdateTraceSegmentDestination",
          "xray:GetTraceSegmentDestination"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Resource = "*"
        Action   = "cloudwatch:PutMetricData"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "bedrock-agentcore"
          }
        }
      },
      {
        Sid    = "GetAgentAccessToken"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:GetWorkloadAccessToken",
          "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
          "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${var.account_id}:workload-identity-directory/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${var.account_id}:workload-identity-directory/default/workload-identity/${var.agent_name}-*",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${var.account_id}:workload-identity-directory/default/workload-identity/mcp_agentrock_basic_server-*"
        ]
      },
      {
        Sid    = "BedrockModelInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:${var.aws_region}:${var.account_id}:*"
        ]
      },
      {
        Sid    = "GlueDataCatalogAccess"
        Effect = "Allow"
        Action = [
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:BatchGetPartition"
        ]
        Resource = [
          "arn:aws:glue:*:${var.account_id}:catalog",
          "arn:aws:glue:*:${var.account_id}:database/*",
          "arn:aws:glue:*:${var.account_id}:table/*/*"
        ]
      }
    ]
  })
}

# Cognito User Pool for MCP authentication
resource "aws_cognito_user_pool" "mcp_auth" {
  name = "mcp-agentcore-pool-${var.agent_name}"

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  # User pool configuration
  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]

  # Schema for user attributes
  schema {
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    name                     = "email"
    required                 = true

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  tags = {
    Name        = "MCP AgentCore Authentication"
    Environment = "development"
    Purpose     = "MCP server authentication"
  }
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "mcp_client" {
  name         = "mcp-agentcore-client-${var.agent_name}"
  user_pool_id = aws_cognito_user_pool.mcp_auth.id

  # Authentication flows
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  # Token validity
  access_token_validity  = 24 # 24 hours
  refresh_token_validity = 30 # 30 days
  id_token_validity      = 24 # 24 hours

  # Token validity units
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"

  # Don't generate a client secret (for simplicity)
  generate_secret = false
}

# Create a test user (optional, can be created manually)
resource "aws_cognito_user" "test_user" {
  user_pool_id = aws_cognito_user_pool.mcp_auth.id
  username     = var.test_user_email # Use email as username since username_attributes = ["email"]

  attributes = {
    email          = var.test_user_email
    email_verified = "true"
  }

  # Set temporary password - user will be forced to change on first login
  temporary_password = var.test_user_temp_password
  message_action     = "SUPPRESS" # Don't send welcome email

  lifecycle {
    ignore_changes = [
      temporary_password,
      attributes["email"]
    ]
  }
}

# Note: Password will be set via AWS CLI after user creation
# Run: aws cognito-idp admin-set-user-password --user-pool-id <pool-id> --username testuser --password <password> --permanent 