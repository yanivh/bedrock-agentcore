#!/usr/bin/env python3
"""
Test script for the user's specific event format.
"""

import boto3
import json

def test_your_event():
    """Test the Lambda function with the user's exact event format."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Your exact event format
    event = {
        "input_text": "What is the weather like in London?",
        "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
        "region": "us-east-1",
        "qualifier": "DEFAULT"
    }
    
    print("Testing Your Event Format")
    print("=" * 50)
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
        
        print(f"✅ Lambda function invoked successfully!")
        print(f"Status Code: {response['StatusCode']}")
        print(f"Response: {json.dumps(response_payload, indent=2)}")
        
        # Check if it was successful
        if response_payload.get('statusCode') == 200:
            print("\n🎉 SUCCESS! Your Lambda function is working perfectly!")
            body = json.loads(response_payload.get('body', '{}'))
            if body.get('success'):
                print("✅ Bedrock AgentCore responded successfully!")
                print(f"Agent Response: {body.get('response', {})}")
            else:
                print("⚠️  Lambda function worked but Bedrock AgentCore had an issue")
        else:
            print(f"❌ Lambda function returned error: {response_payload.get('body')}")
        
    except Exception as e:
        print(f"❌ Error invoking Lambda function: {e}")
        print(f"Error type: {type(e).__name__}")

def test_minimal_event():
    """Test with minimal event (using defaults)."""
    
    print("\n" + "=" * 50)
    print("Testing Minimal Event (Using Defaults)")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Minimal event (uses defaults)
    event = {}
    
    print(f"Event: {json.dumps(event, indent=2)}")
    print("-" * 50)
    
    try:
        response = lambda_client.invoke(
            FunctionName='bedrock-agentcore-lambda-agentcore_babbel_data_team',
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        print(f"✅ Lambda function invoked successfully!")
        print(f"Status Code: {response['StatusCode']}")
        print(f"Response: {json.dumps(response_payload, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Your Lambda Function")
    print("=" * 60)
    
    # Test your exact event format
    test_your_event()
    
    # Test minimal event
    test_minimal_event() 