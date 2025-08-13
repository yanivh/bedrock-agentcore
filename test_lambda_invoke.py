#!/usr/bin/env python3
"""
Test script to invoke the deployed Lambda function.
"""

import boto3
import json

def test_lambda_invocation():
    """Test the Lambda function with sample data."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test event with your agent runtime ARN
    event = {
        "input_text": "Hello, how can you assist me today?",
        "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
        "region": "us-east-1",
        "qualifier": "DEFAULT"
    }
    
    print("Testing Lambda function invocation...")
    print(f"Function: bedrock-agentcore-lambda-agentcore_babbel_data_team")
    print(f"Event: {json.dumps(event, indent=2)}")
    print("-" * 50)
    
    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName='bedrock-agentcore-lambda-agentcore_babbel_data_team',
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read())
        
        print("✅ Lambda function invoked successfully!")
        print(f"Status Code: {response['StatusCode']}")
        print(f"Response: {json.dumps(response_payload, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error invoking Lambda function: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_lambda_invocation() 