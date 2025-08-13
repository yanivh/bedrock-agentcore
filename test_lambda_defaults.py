#!/usr/bin/env python3
"""
Test script to demonstrate Lambda function with default values.
"""

import boto3
import json

def test_lambda_with_defaults():
    """Test the Lambda function with different input scenarios."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    test_cases = [
        {
            "name": "Empty event (uses all defaults)",
            "event": {}
        },
        {
            "name": "Only input_text provided",
            "event": {
                "input_text": "Can you help me with customer support?"
            }
        },
        {
            "name": "Only agent_runtime_arn provided",
            "event": {
                "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
            }
        },
        {
            "name": "Custom input and region",
            "event": {
                "input_text": "Analyze the sales data for Q4 2024",
                "region": "us-west-2"
            }
        },
        {
            "name": "Full custom event",
            "event": {
                "input_text": "What is the weather like in London?",
                "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
                "region": "us-east-1",
                "qualifier": "DEFAULT"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test_case['name']}")
        print(f"{'='*60}")
        print(f"Input event: {json.dumps(test_case['event'], indent=2)}")
        print("-" * 40)
        
        try:
            # Invoke the Lambda function
            response = lambda_client.invoke(
                FunctionName='bedrock-agentcore-lambda-agentcore_babbel_data_team',
                InvocationType='RequestResponse',
                Payload=json.dumps(test_case['event'])
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            print(f"✅ Lambda function invoked successfully!")
            print(f"Status Code: {response['StatusCode']}")
            print(f"Response: {json.dumps(response_payload, indent=2)}")
            
        except Exception as e:
            print(f"❌ Error invoking Lambda function: {e}")
            print(f"Error type: {type(e).__name__}")

def test_minimal_invocation():
    """Test the simplest possible invocation."""
    
    print(f"\n{'='*60}")
    print("MINIMAL INVOCATION TEST")
    print(f"{'='*60}")
    print("Testing with empty event (should use all defaults)...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Invoke with empty event
        response = lambda_client.invoke(
            FunctionName='bedrock-agentcore-lambda-agentcore_babbel_data_team',
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        print("✅ Success! Lambda function used default values.")
        print(f"Response: {json.dumps(response_payload, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Lambda Function with Default Values")
    print("=" * 60)
    
    # Test minimal invocation first
    test_minimal_invocation()
    
    # Test all scenarios
    test_lambda_with_defaults() 