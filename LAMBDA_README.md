# Bedrock AgentCore Lambda Function

This project contains a Lambda function for invoking AWS Bedrock AgentCore agents. All Lambda-related files are organized in the `terraform/` directory.

## Project Structure

```
bedrock-agentcore/
├── terraform/                    # Lambda function and infrastructure
│   ├── lambda_function.py       # Main Lambda function code
│   ├── lambda_requirements.txt  # Python dependencies for Lambda
│   ├── deploy_lambda.py         # Deployment script
│   ├── test_lambda.py           # Test script
│   ├── terraform_lambda.tf      # Terraform configuration
│   └── LAMBDA_README.md         # Detailed documentation
├── deploy_lambda.py             # Root deployment script (calls terraform/)
├── test_lambda.py               # Root test script (calls terraform/)
├── LAMBDA_README.md             # This file
└── activate_env.fish            # Virtual environment activation (fish shell)
```

## Quick Start

### 1. Activate Virtual Environment

For Fish shell:
```bash
source activate_env.fish
```

For Bash shell:
```bash
source activate_env.sh
```

### 2. Deploy the Lambda Function

From the root directory:
```bash
python deploy_lambda.py
```

This will:
- Create the deployment package in `terraform/bedrock_agentcore_lambda.zip`
- Generate Terraform configuration in `terraform/terraform_lambda.tf`

### 3. Deploy with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 4. Test the Function

From the root directory:
```bash
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

## Usage Examples

### Direct Lambda Invocation

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

### AWS CLI Invocation

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

## For Detailed Documentation

See `terraform/LAMBDA_README.md` for comprehensive documentation about the Lambda function implementation.

## Support

For issues related to:
- Bedrock AgentCore: Check AWS Bedrock documentation
- Lambda deployment: Check AWS Lambda documentation
- This function: Review the code and logs for debugging 