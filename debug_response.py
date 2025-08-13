#!/usr/bin/env python3
"""
Debug script to test different questions and see agent responses.
"""

import boto3
import json

def test_different_questions():
    """Test the agent with different types of questions."""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    test_questions = [
        "Where is ledro located?",
        "What is the weather like in London?",
        "Can you help me find information about ledro?",
        "Tell me about ledro location",
        "Hello, where is ledro?",
        "What is ledro?",
        "Give me the location of ledro"
    ]
    
    print("Testing Different Questions with Your Agent")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {question}")
        print(f"{'='*50}")
        
        event = {
            "input_text": question,
            "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
            "region": "us-east-1",
            "qualifier": "DEFAULT"
        }
        
        try:
            response = lambda_client.invoke(
                FunctionName='bedrock-agentcore-lambda-agentcore_babbel_data_team',
                InvocationType='RequestResponse',
                Payload=json.dumps(event)
            )
            
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload.get('body', '{}'))
                agent_response = body.get('response', '')
                
                print(f"✅ Success!")
                print(f"Question: {question}")
                print(f"Agent Response: {agent_response}")
                
                # Check if response is generic
                if "Hello" in agent_response or "How are you" in agent_response:
                    print("⚠️  WARNING: Generic greeting response detected!")
                else:
                    print("✅ Specific response detected!")
                    
            else:
                print(f"❌ Error: {response_payload.get('body')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_payload_format():
    """Test different payload formats to see if that affects the response."""
    
    print("\n" + "="*60)
    print("Testing Different Payload Formats")
    print("="*60)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test direct Bedrock AgentCore invocation
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    
    test_payloads = [
        {"message": "Where is ledro located?"},
        {"query": "Where is ledro located?"},
        {"input": "Where is ledro located?"},
        {"text": "Where is ledro located?"},
        {"question": "Where is ledro located?"}
    ]
    
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam"
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\nTest {i}: {payload}")
        print("-" * 30)
        
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                qualifier="DEFAULT",
                payload=json.dumps(payload)
            )
            
            # Read the response
            if hasattr(response.get('response'), 'read'):
                response_content = response['response'].read().decode('utf-8')
                print(f"✅ Direct Response: {response_content}")
            else:
                print(f"✅ Direct Response: {response.get('response')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Debugging Agent Response Issues")
    print("=" * 60)
    
    # Test different questions
    test_different_questions()
    
    # Test different payload formats
    test_payload_format() 