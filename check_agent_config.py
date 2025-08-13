#!/usr/bin/env python3
"""
Script to check Bedrock AgentCore agent configuration.
"""

import boto3
import json

def check_agent_configuration():
    """Check the agent configuration to understand its capabilities."""
    
    print("Checking Bedrock AgentCore Agent Configuration")
    print("=" * 60)
    
    try:
        # Try to get agent information
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Extract agent ID from ARN
        agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
        agent_id = agent_runtime_arn.split('/')[-1]
        
        print(f"Agent ID: {agent_id}")
        print(f"Agent Runtime ARN: {agent_runtime_arn}")
        
        # Try to get agent runtime details
        try:
            response = client.get_agent_runtime(
                agentRuntimeArn=agent_runtime_arn
            )
            print(f"\n✅ Agent Runtime Details:")
            print(f"Response: {json.dumps(response, indent=2, default=str)}")
        except Exception as e:
            print(f"❌ Could not get agent runtime details: {e}")
        
        # Try to list agent runtimes
        try:
            response = client.list_agent_runtimes()
            print(f"\n✅ Available Agent Runtimes:")
            print(f"Response: {json.dumps(response, indent=2, default=str)}")
        except Exception as e:
            print(f"❌ Could not list agent runtimes: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_agent_capabilities():
    """Test what the agent can actually do."""
    
    print("\n" + "="*60)
    print("Testing Agent Capabilities")
    print("="*60)
    
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
    
    # Test different types of interactions
    test_interactions = [
        "Hello",
        "What can you help me with?",
        "What are your capabilities?",
        "Do you have access to any knowledge base?",
        "Can you search for information?",
        "What tools do you have available?",
        "Tell me about yourself"
    ]
    
    for interaction in test_interactions:
        print(f"\nTesting: {interaction}")
        print("-" * 30)
        
        try:
            payload = json.dumps({"message": interaction})
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                qualifier="DEFAULT",
                payload=payload
            )
            
            if hasattr(response.get('response'), 'read'):
                response_content = response['response'].read().decode('utf-8')
                print(f"Response: {response_content}")
            else:
                print(f"Response: {response.get('response')}")
                
        except Exception as e:
            print(f"Error: {e}")

def check_agent_status():
    """Check if the agent is properly configured and active."""
    
    print("\n" + "="*60)
    print("Agent Status Check")
    print("="*60)
    
    # Test a simple interaction to see if agent is responsive
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
    
    try:
        payload = json.dumps({"message": "Hello"})
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier="DEFAULT",
            payload=payload
        )
        
        print("✅ Agent is responsive")
        
        if hasattr(response.get('response'), 'read'):
            response_content = response['response'].read().decode('utf-8')
            print(f"Response: {response_content}")
        else:
            print(f"Response: {response.get('response')}")
            
        # Check response metadata
        print(f"\nResponse Metadata:")
        print(f"Runtime Session ID: {response.get('runtimeSessionId')}")
        print(f"Trace ID: {response.get('traceId')}")
        print(f"Content Type: {response.get('contentType')}")
        print(f"Status Code: {response.get('statusCode')}")
        
    except Exception as e:
        print(f"❌ Agent is not responsive: {e}")

if __name__ == "__main__":
    print("Bedrock AgentCore Configuration Check")
    print("=" * 60)
    
    # Check agent configuration
    check_agent_configuration()
    
    # Test agent capabilities
    test_agent_capabilities()
    
    # Check agent status
    check_agent_status() 