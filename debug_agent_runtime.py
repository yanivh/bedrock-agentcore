#!/usr/bin/env python3
"""
Debug script to test Bedrock AgentCore runtime invocation.
"""

import boto3
import json

def test_bedrock_agentcore_direct():
    """Test direct Bedrock AgentCore invocation to understand the issue."""
    
    print("Testing Bedrock AgentCore Direct Invocation")
    print("=" * 50)
    
    # Initialize the client
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    
    # Test different payload formats
    test_cases = [
        {
            "name": "Simple text payload",
            "payload": "What is the weather like in New York?"
        },
        {
            "name": "JSON string payload",
            "payload": json.dumps({"message": "What is the weather like in New York?"})
        },
        {
            "name": "Empty payload",
            "payload": ""
        },
        {
            "name": "Complex query",
            "payload": "Can you help me analyze the sales data for Q4 2024?"
        }
    ]
    
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Payload: {test_case['payload']}")
        print("-" * 30)
        
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                qualifier="DEFAULT",
                payload=test_case['payload']
            )
            
            print("✅ Success!")
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Check if it's a specific error type
            if hasattr(e, 'response'):
                print(f"Error response: {e.response}")
                if 'Error' in e.response:
                    print(f"Error code: {e.response['Error'].get('Code')}")
                    print(f"Error message: {e.response['Error'].get('Message')}")

def check_agent_runtime_status():
    """Check the status of the agent runtime."""
    
    print("\nChecking Agent Runtime Status")
    print("=" * 50)
    
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Try to get agent runtime info
        agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
        
        # Extract agent ID from ARN
        agent_id = agent_runtime_arn.split('/')[-1]
        
        print(f"Agent ID: {agent_id}")
        
        # Try to list agent runtimes
        response = client.list_agent_runtimes()
        print(f"Available agent runtimes: {response}")
        
    except Exception as e:
        print(f"Error checking agent runtime: {e}")

def test_different_qualifiers():
    """Test different qualifiers."""
    
    print("\nTesting Different Qualifiers")
    print("=" * 50)
    
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
    
    qualifiers = ["DEFAULT", "LATEST", "v1", "production"]
    
    for qualifier in qualifiers:
        print(f"\nTesting qualifier: {qualifier}")
        print("-" * 20)
        
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                qualifier=qualifier,
                payload="Hello"
            )
            
            print("✅ Success!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Bedrock AgentCore Debug Script")
    print("=" * 60)
    
    # Check agent runtime status
    check_agent_runtime_status()
    
    # Test different qualifiers
    test_different_qualifiers()
    
    # Test direct invocation
    test_bedrock_agentcore_direct() 