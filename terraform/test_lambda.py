#!/usr/bin/env python3
"""
Test script for the Bedrock AgentCore Lambda function.
This script demonstrates how to invoke the Lambda function locally and shows the expected format.
"""

import json
import boto3
from lambda_function import lambda_handler

def test_lambda_locally():
    """Test the Lambda function locally."""
    
    # Sample event that would be passed to the Lambda function
    test_event = {
        "input_text": "Hello, how can you assist me today?",
        "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
        "region": "us-east-1",
        "qualifier": "DEFAULT"
    }
    
    print("Testing Lambda function locally...")
    print(f"Input event: {json.dumps(test_event, indent=2)}")
    print("-" * 50)
    
    try:
        # Call the Lambda function
        response = lambda_handler(test_event, None)
        
        print(f"Response status: {response['statusCode']}")
        print(f"Response body: {json.dumps(json.loads(response['body']), indent=2)}")
        
    except Exception as e:
        print(f"Error testing Lambda function: {e}")

def test_with_aws_lambda():
    """Test the Lambda function deployed on AWS."""
    
    # Initialize AWS Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test event
    test_event = {
        "input_text": "Hello, how can you assist me today?",
        "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
        "region": "us-east-1",
        "qualifier": "DEFAULT"
    }
    
    print("Testing Lambda function on AWS...")
    print(f"Input event: {json.dumps(test_event, indent=2)}")
    print("-" * 50)
    
    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName='bedrock-agentcore-lambda',  # Replace with your actual function name
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read())
        print(f"Response: {json.dumps(response_payload, indent=2)}")
        
    except Exception as e:
        print(f"Error testing AWS Lambda function: {e}")

def create_sample_events():
    """Create sample events for different use cases."""
    
    events = {
        "basic_query": {
            "input_text": "What is the weather like today?",
            "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
            "region": "us-east-1",
            "qualifier": "DEFAULT"
        },
        "data_analysis": {
            "input_text": "Analyze the sales data for Q4 2024",
            "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
            "region": "us-east-1",
            "qualifier": "DEFAULT"
        },
        "custom_region": {
            "input_text": "Hello, how can you assist me today?",
            "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-west-2:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
            "region": "us-west-2",
            "qualifier": "DEFAULT"
        }
    }
    
    print("Sample events for different use cases:")
    print("=" * 50)
    
    for name, event in events.items():
        print(f"\n{name.upper()}:")
        print(json.dumps(event, indent=2))
        print("-" * 30)

if __name__ == "__main__":
    print("Bedrock AgentCore Lambda Function Test")
    print("=" * 50)
    
    # Show sample events
    create_sample_events()
    
    print("\n" + "=" * 50)
    
    # Test locally (uncomment to test)
    # test_lambda_locally()
    
    # Test with AWS Lambda (uncomment to test)
    # test_with_aws_lambda()
    
    print("\nTo test the Lambda function:")
    print("1. Uncomment the test functions above")
    print("2. Ensure you have proper AWS credentials configured")
    print("3. Update the agent_runtime_arn with your actual ARN")
    print("4. Run: python test_lambda.py") 