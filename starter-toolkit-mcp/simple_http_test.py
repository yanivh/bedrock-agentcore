#!/usr/bin/env python3
"""
Simple HTTP test to get more detailed error information.
"""

import requests
import json
import os

def test_simple_http():
    """Test with simple HTTP request to get detailed error response."""
    
    # Get the bearer token
    with open('.bearer_token', 'r') as f:
        bearer_token = f.read().strip()
    
    # Configuration
    agent_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/mcp_agentrock_basic_server-r9jEKOHcJ5"
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Simple initialization payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "simple-test",
                "version": "1.0.0"
            }
        }
    }
    
    print("🚀 Simple HTTP Test")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 40)
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Text: {response.text}")
        
        if response.status_code == 403:
            print("\n🔍 403 Error Analysis:")
            print("- Check if token has required audience claim")
            print("- Verify token is being validated correctly")
            print("- Check if there are additional claims required")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_simple_http() 