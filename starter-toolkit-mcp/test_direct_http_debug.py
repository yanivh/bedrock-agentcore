#!/usr/bin/env python3
"""
Direct HTTP test to debug the 403 error.
This will help us see exactly what the server is returning.
"""

import asyncio
import aiohttp
import json
import os

async def test_direct_http():
    """Test direct HTTP request to the MCP endpoint."""
    
    # Get the bearer token
    token_file = os.path.join(os.path.dirname(__file__), '.bearer_token')
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            bearer_token = f.read().strip()
        print(f"✅ Using bearer token: {bearer_token[:20]}...")
    else:
        print("❌ No bearer token file found")
        return
    
    # Configuration
    agent_arn = "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/mcp_agentrock_basic_server-r9jEKOHcJ5"
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # MCP Initialize request payload
    initialize_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print("🚀 Direct HTTP Test to MCP Endpoint")
    print("=" * 50)
    print(f"🔗 URL: {mcp_url}")
    print(f"🔑 Headers: {json.dumps(headers, indent=2)}")
    print(f"📤 Payload: {json.dumps(initialize_payload, indent=2)}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Sending HTTP POST request...")
            
            async with session.post(
                mcp_url,
                headers=headers,
                json=initialize_payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"📥 Response Status: {response.status}")
                print(f"📥 Response Headers: {dict(response.headers)}")
                
                # Get response text
                response_text = await response.text()
                print(f"📥 Response Body: {response_text}")
                
                # Try to parse as JSON
                try:
                    response_json = json.loads(response_text)
                    print(f"📥 Parsed JSON: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    print(f"📥 Response is not valid JSON")
                
                if response.status == 403:
                    print("\n❌ 403 Forbidden Error Analysis:")
                    print("   - Bearer token is valid (got past authentication)")
                    print("   - Request reached the server")
                    print("   - Server rejected the request for authorization reasons")
                    print("   - Possible issues:")
                    print("     * Cognito user lacks permissions for MCP operations")
                    print("     * Agent configuration doesn't allow this token/user")
                    print("     * Missing IAM permissions on the agent runtime role")
                
                elif response.status == 200:
                    print("✅ Success! The request worked.")
                else:
                    print(f"⚠️  Unexpected status: {response.status}")
    
    except Exception as e:
        print(f"❌ HTTP request failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_direct_http()) 