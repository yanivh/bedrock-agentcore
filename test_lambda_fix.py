#!/usr/bin/env python3
"""
Test script to verify the lambda function fix with correct payload format.
"""

import boto3
import json

def test_lambda_fix():
    """Test the Lambda function with the corrected payload format."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test event with the specific question about ledro
    event = {
        "input_text": "Where is ledro located?",
        "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
        "region": "us-east-1",
        "qualifier": "DEFAULT"
    }
    
    print("Testing Lambda Function Fix")
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
            print("\n🎉 SUCCESS! Lambda function is working!")
            body = json.loads(response_payload.get('body', '{}'))
            if body.get('success'):
                print("✅ Bedrock AgentCore responded successfully!")
                agent_response = body.get('response', '')
                print(f"Agent Response: {agent_response}")
                
                # Check if response is specific to the question
                if "ledro" in agent_response.lower() or "location" in agent_response.lower():
                    print("✅ Specific response about ledro detected!")
                elif "hello" in agent_response.lower() or "how are you" in agent_response.lower():
                    print("⚠️  Still getting generic response - agent may need configuration")
                else:
                    print("✅ Non-generic response received!")
            else:
                print("⚠️  Lambda function worked but Bedrock AgentCore had an issue")
        else:
            print(f"❌ Lambda function returned error: {response_payload.get('body')}")
        
    except Exception as e:
        print(f"❌ Error invoking Lambda function: {e}")
        print(f"Error type: {type(e).__name__}")

def test_direct_bedrock_invocation():
    """Test direct Bedrock AgentCore invocation with correct payload format."""
    
    print("\n" + "="*60)
    print("Testing Direct Bedrock AgentCore Invocation")
    print("="*60)
    
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
    
    # Test with the correct payload format
    payload = {"prompt": "Where is ledro located?"}
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 30)
    
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier="DEFAULT",
            payload=json.dumps(payload)
        )
        
        print("✅ Direct Bedrock AgentCore invocation successful!")
        print(f"Raw response: {response}")
        
        # Read the response
        if hasattr(response.get('response'), 'read'):
            response_content = response['response'].read().decode('utf-8')
            print(f"Response content: {response_content}")
        else:
            print(f"Response: {response.get('response')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    print("Testing Lambda Function Fix with Correct Payload Format")
    print("=" * 80)
    
    # Test the lambda function
    test_lambda_fix()
    
    # Test direct Bedrock invocation
    test_direct_bedrock_invocation() 