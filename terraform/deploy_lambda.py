#!/usr/bin/env python3
"""
Deployment script for the Bedrock AgentCore Lambda function.
This script packages the Lambda function and its dependencies for deployment.
"""

import os
import subprocess
import shutil
import zipfile
from pathlib import Path

def create_lambda_package():
    """Create a deployment package for the Lambda function."""
    
    # Create deployment directory
    deployment_dir = Path("lambda_deployment")
    if deployment_dir.exists():
        shutil.rmtree(deployment_dir)
    deployment_dir.mkdir()
    
    print("Creating Lambda deployment package...")
    
    # Copy the Lambda function
    shutil.copy("lambda_function.py", deployment_dir / "lambda_function.py")
    
    # Install dependencies
    print("Installing dependencies...")
    
    # Try to use uv if available, otherwise fall back to pip
    try:
        # First try uv with correct syntax
        subprocess.run([
            "uv", "pip", "install", 
            "--target", str(deployment_dir),
            "--python-platform", "x86_64-manylinux2014",
            "--only-binary=all",
            "-r", "lambda_requirements.txt"
        ], check=True)
        print("Used uv to install dependencies")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fall back to pip
            subprocess.run([
                "pip", "install", 
                "-r", "lambda_requirements.txt",
                "-t", str(deployment_dir),
                "--platform", "manylinux2014_x86_64",
                "--only-binary=all"
            ], check=True)
            print("Used pip to install dependencies")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Last resort: try python -m pip
            subprocess.run([
                "python", "-m", "pip", "install", 
                "-r", "lambda_requirements.txt",
                "-t", str(deployment_dir),
                "--platform", "manylinux2014_x86_64",
                "--only-binary=all"
            ], check=True)
            print("Used python -m pip to install dependencies")
    
    # Create ZIP file
    zip_filename = "bedrock_agentcore_lambda.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in deployment_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(deployment_dir)
                zipf.write(file_path, arcname)
    
    print(f"Created deployment package: {zip_filename}")
    print(f"Package size: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")
    
    # Clean up
    shutil.rmtree(deployment_dir)
    
    return zip_filename

def create_terraform_config():
    """Create Terraform configuration for the Lambda function."""
    
    terraform_config = '''# Terraform configuration for Bedrock AgentCore Lambda function

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "bedrock_agentcore_lambda_role"

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
  name = "bedrock_agentcore_lambda_policy"
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
          "bedrock-agentcore-control:InvokeAgentRuntime"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda function
resource "aws_lambda_function" "bedrock_agentcore" {
  filename         = "bedrock_agentcore_lambda.zip"
  function_name    = "bedrock-agentcore-lambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      PYTHONPATH = "/opt/python"
    }
  }
}

# API Gateway (optional - for HTTP triggers)
resource "aws_api_gateway_rest_api" "api" {
  name = "bedrock-agentcore-api"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.bedrock_agentcore.invoke_arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.bedrock_agentcore.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Outputs
output "lambda_function_arn" {
  value = aws_lambda_function.bedrock_agentcore.arn
}

output "api_gateway_url" {
  value = "${aws_api_gateway_rest_api.api.execution_arn}/prod/"
}
'''
    
    with open("terraform_lambda.tf", "w") as f:
        f.write(terraform_config)
    
    print("Created Terraform configuration: terraform_lambda.tf")

if __name__ == "__main__":
    try:
        # Create the deployment package
        zip_filename = create_lambda_package()
        
        # Create Terraform configuration
        create_terraform_config()
        
        print("\nDeployment package created successfully!")
        print(f"Next steps:")
        print(f"1. Upload {zip_filename} to AWS Lambda")
        print(f"2. Use terraform_lambda.tf for infrastructure as code deployment")
        print(f"3. Configure the Lambda function with appropriate IAM permissions")
        
    except Exception as e:
        print(f"Error creating deployment package: {e}")
        exit(1) 