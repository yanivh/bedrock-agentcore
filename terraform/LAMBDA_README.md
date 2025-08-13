# Bedrock AgentCore Lambda Function

This Lambda function allows you to invoke AWS Bedrock AgentCore agents from AWS Lambda. It provides a serverless way to interact with your Bedrock AgentCore agents.

## Features

- ✅ Invoke Bedrock AgentCore agents via Lambda
- ✅ Configurable region and agent runtime ARN
- ✅ Error handling and logging
- ✅ Input validation
- ✅ JSON response format
- ✅ Terraform deployment configuration
- ✅ Local testing capabilities

## Files Overview

- `lambda_function.py` - Main Lambda function code
- `lambda_requirements.txt` - Python dependencies for Lambda
- `deploy_lambda.py` - Deployment script to package the Lambda function
- `test_lambda.py` - Test script for local and AWS testing
- `terraform_lambda.tf` - Terraform configuration for infrastructure
- `LAMBDA_README.md` - This documentation

## Quick Start

### 1. Deploy the Lambda Function

```bash
# Create the deployment package
python deploy_lambda.py
```

This will create:
- `bedrock_agentcore_lambda.zip` - Deployment package
- `terraform_lambda.tf` - Terraform configuration

### 2. Deploy with Terraform

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Deploy
terraform apply
```

### 3. Test the Function

```bash
# Run the test script
python test_lambda.py
```

## Input Format

The Lambda function expects the following JSON input:

```json
{
  "input_text": "Hello, how can you assist me today?",
  "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
  "region": "us-east-1",
  "qualifier": "DEFAULT"
}
```

### Parameters

- `input_text` (required): The text to send to the Bedrock AgentCore agent
- `agent_runtime_arn` (required): The ARN of your Bedrock AgentCore runtime
- `region` (optional): AWS region (defaults to "us-east-1")
- `qualifier` (optional): Agent qualifier (defaults to "DEFAULT")

## Output Format

Successful response:
```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "response": {
      // Bedrock AgentCore response content
    },
    "input_text": "Hello, how can you assist me today?",
    "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
  }
}
```

Error response:
```json
{
  "statusCode": 400,
  "body": {
    "error": "input_text is required"
  }
}
```

## Usage Examples

### 1. Direct Lambda Invocation

```python
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

event = {
    "input_text": "What is the weather like today?",
    "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
    "region": "us-east-1",
    "qualifier": "DEFAULT"
}

response = lambda_client.invoke(
    FunctionName='bedrock-agentcore-lambda',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

result = json.loads(response['Payload'].read())
print(result)
```

### 2. API Gateway Integration

If you deploy with the provided Terraform configuration, you can also invoke via HTTP:

```bash
curl -X POST https://your-api-gateway-url/prod/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Hello, how can you assist me today?",
    "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
    "region": "us-east-1",
    "qualifier": "DEFAULT"
  }'
```

### 3. AWS CLI Invocation

```bash
aws lambda invoke \
  --function-name bedrock-agentcore-lambda \
  --payload '{"input_text": "Hello", "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"}' \
  response.json
```

## IAM Permissions

The Lambda function requires the following IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore-control:InvokeAgentRuntime"
      ],
      "Resource": "*"
    }
  ]
}
```

## Configuration

### Environment Variables

The Lambda function can be configured with the following environment variables:

- `PYTHONPATH`: Set to `/opt/python` for proper module resolution

### Lambda Configuration

- **Runtime**: Python 3.11
- **Timeout**: 30 seconds (configurable)
- **Memory**: 256 MB (configurable)
- **Handler**: `lambda_function.lambda_handler`

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the Lambda execution role has the required Bedrock AgentCore permissions
2. **Timeout**: Increase the Lambda timeout if your agent takes longer to respond
3. **Invalid ARN**: Verify the agent runtime ARN is correct and accessible
4. **Region Mismatch**: Ensure the region in the event matches your agent's region

### Logs

Check CloudWatch logs for detailed error information:
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/bedrock-agentcore-lambda"
```

## Security Considerations

- Use IAM roles with minimal required permissions
- Consider using AWS Secrets Manager for sensitive configuration
- Enable VPC if your agent requires private network access
- Use API Gateway with authentication for HTTP triggers

## Cost Optimization

- Set appropriate timeout values to avoid unnecessary charges
- Use provisioned concurrency for predictable workloads
- Monitor CloudWatch metrics for performance optimization

## Support

For issues related to:
- Bedrock AgentCore: Check AWS Bedrock documentation
- Lambda deployment: Check AWS Lambda documentation
- This function: Review the code and logs for debugging 