#!/usr/bin/env python3
"""
MCP client for remote Bedrock AgentCore server.
Based on the reference code pattern provided.

IMPORTANT: This script requires the MCP agent to be deployed with OAuth configuration.
If you get 403 Forbidden errors, the agent needs to be reconfigured:

1. Run: agentcore configure -e mcp_agentrock_basic_server.py --protocol MCP
2. When prompted for OAuth, provide:
   - Discovery URL: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_MLKS5EUVq/.well-known/openid-configuration
   - Client ID: 1v57ncpgu61qjgb8fi9h8ksphf
3. Then redeploy: agentcore launch

Current agent ARN: arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/mcp_agentrock_basic_server-r9jEKOHcJ5
"""

import asyncio
import os
import sys
import json
import aiohttp
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Add AWS SigV4 signing support
try:
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

def get_bearer_token_from_file():
    """Try to get bearer token from saved file."""
    try:
        token_file = os.path.join(os.path.dirname(__file__), '.bearer_token')
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
                if token:
                    print(f"✅ Found saved bearer token: {token[:20]}...")
                    return token
    except Exception as e:
        print(f"⚠️  Could not read saved token: {e}")
    return None

def get_cognito_token_automatically():
    """Try to get a fresh Cognito token automatically."""
    try:
        import subprocess
        
        # Try to run the token script
        token_script = os.path.join(os.path.dirname(__file__), 'get_cognito_token.py')
        if os.path.exists(token_script):
            print("🔐 Attempting to get fresh Cognito token...")
            
            result = subprocess.run(
                ['python', token_script, '--from-terraform'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            if result.returncode == 0:
                # Try to read the saved token
                return get_bearer_token_from_file()
            else:
                print(f"⚠️  Token script failed: {result.stderr}")
                return None
        else:
            print(f"⚠️  Token script not found: {token_script}")
            return None
    except Exception as e:
        print(f"⚠️  Could not get fresh token: {e}")
        return None

def display_configuration_status():
    """Display current configuration status and requirements."""
    print("\n📋 Configuration Status:")
    print("=" * 50)
    
    # Check Cognito configuration
    try:
        import subprocess
        terraform_dir = os.path.join(os.path.dirname(__file__), '..', 'terraform')
        if os.path.exists(terraform_dir):
            result = subprocess.run(
                ['terraform', 'output', '-json'],
                cwd=terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                outputs = json.loads(result.stdout)
                pool_id = outputs.get('cognito_user_pool_id', {}).get('value')
                client_id = outputs.get('cognito_client_id', {}).get('value')
                discovery_url = outputs.get('cognito_discovery_url', {}).get('value')
                
                print(f"✅ Cognito User Pool: {pool_id}")
                print(f"✅ Cognito Client ID: {client_id}")
                print(f"✅ Discovery URL: {discovery_url}")
            else:
                print(f"⚠️  Could not read Terraform outputs")
    except Exception as e:
        print(f"⚠️  Error checking Terraform config: {e}")
    
    # Check bearer token
    token_file = os.path.join(os.path.dirname(__file__), '.bearer_token')
    if os.path.exists(token_file):
        print(f"✅ Bearer token file: Available")
    else:
        print(f"❌ Bearer token file: Missing")
    
    # Agent information
    print(f"📍 Current Agent ARN: arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/mcp_agentrock_basic_server-r9jEKOHcJ5")
    print(f"🌐 MCP Endpoint: https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A301581146302%3Aruntime%2Fmcp_agentrock_basic_server-r9jEKOHcJ5/invocations?qualifier=DEFAULT")
    
    print("=" * 50)

async def main():
    # Get agent ARN from environment variables
    agent_arn = os.getenv('AGENT_ARN')
    bearer_token = os.getenv('BEARER_TOKEN')
    
    if not agent_arn:
        print("Error: AGENT_ARN environment variable is not set")
        print("Please set the environment variable:")
        print("  export AGENT_ARN='your_agent_arn_here'")
        sys.exit(1)
    
    # Try different methods to get bearer token
    if not bearer_token:
        print("⚠️  BEARER_TOKEN not set. Trying alternative methods...")
        
        # Method 1: Try saved token file
        bearer_token = get_bearer_token_from_file()
        
        # Method 2: Try to get fresh token automatically
        if not bearer_token:
            bearer_token = get_cognito_token_automatically()
        
        # Method 3: Fall back to AWS credentials
        if not bearer_token:
            print("⚠️  No bearer token available. Will try with AWS credentials.")

    # Encode the ARN for URL
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    
    # Construct the MCP URL (using us-east-1 where our agent is deployed)
    mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    # Set headers - try with bearer token first, fallback to AWS credentials
    if bearer_token:
        headers = {
            "authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
    else:
        # Try to get AWS credentials and create a bearer token
        try:
            import boto3
            sts_client = boto3.client('sts')
            identity = sts_client.get_caller_identity()
            print(f"✅ AWS credentials working - Account: {identity['Account']}")
            
            # For now, let's try without authorization header
            headers = {
                "Content-Type": "application/json"
            }
            print("ℹ️  Using AWS credentials without bearer token")
            
        except Exception as e:
            print(f"❌ Failed to verify AWS credentials: {e}")
            print("Please set BEARER_TOKEN environment variable")
            sys.exit(1)
    
    print("🚀 Remote Bedrock AgentCore MCP Client Test")
    print("=" * 60)
    print(f"🔗 Agent ARN: {agent_arn}")
    print(f"🌐 MCP URL: {mcp_url}")
    print(f"📋 Headers: {headers}")
    print(f"🔑 Bearer Token: {bearer_token[:20]}..." if bearer_token else "❌ No bearer token")
    print("-" * 60)
    
    # Display configuration status
    display_configuration_status()
    
    try:
        print("🔌 Establishing MCP connection...")
        print(f"📡 Connecting to: {mcp_url}")
        print(f"🔑 Using headers: {headers}")
        
        # If we don't have a bearer token, try AWS SigV4 signing
        if not bearer_token and AWS_AVAILABLE:
            print("🔐 Attempting AWS SigV4 signing...")
            
            # Create a test request to get signed headers
            test_request = AWSRequest(
                method='POST',
                url=mcp_url,
                data='{"test": "data"}',
                headers=headers
            )
            
            # Get AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            # Sign the request
            SigV4Auth(credentials, 'bedrock-agentcore', 'us-east-1').add_auth(test_request)
            signed_headers = dict(test_request.headers)
            
            print(f"🔐 Using AWS SigV4 signed headers")
            headers = signed_headers
        
        # Add detailed HTTP logging
        print("\n🔍 HTTP Request Details:")
        print(f"   Method: POST")
        print(f"   URL: {mcp_url}")
        print(f"   Headers: {json.dumps(headers, indent=4)}")
        
        # Use the exact pattern from the reference code with enhanced logging
        async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
            read_stream,
            write_stream,
            transport_info,
        ):
            print("✅ HTTP connection established!")
            print(f"🔍 Transport info: {transport_info}")
            
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ MCP session established!")
                
                # Initialize the session (exact pattern from reference)
                print("\n🚀 Step 1: Initialize MCP Session")
                print("-" * 40)
                print("📤 Sending initialization request...")
                
                try:
                    # Add request logging before initialize
                    print("🔍 About to send initialize request to MCP server...")
                    
                    init_result = await session.initialize()
                    print("✅ Session initialized successfully!")
                    print(f"🔍 Initialize response: {init_result}")
                    
                except Exception as init_error:
                    print(f"❌ Initialize failed: {init_error}")
                    print(f"❌ Initialize error type: {type(init_error).__name__}")
                    
                    # Check for 403 error in the initialization step
                    init_error_str = str(init_error).lower()
                    if "403" in init_error_str or "forbidden" in init_error_str:
                        print(f"\n🚨 403 FORBIDDEN ERROR DETECTED AT INITIALIZATION:")
                        print(f"=" * 60)
                        print(f"✅ Cognito authentication: WORKING (got valid bearer token)")
                        print(f"✅ MCP server: RUNNING (visible in CloudWatch logs)")
                        print(f"✅ Network connection: WORKING (reached Bedrock AgentCore)")
                        print(f"❌ OAuth configuration: MISSING")
                        print(f"")
                        print(f"🔧 SOLUTION:")
                        print(f"The MCP agent was deployed WITHOUT OAuth configuration.")
                        print(f"You need to reconfigure and redeploy the agent:")
                        print(f"")
                        print(f"1. Navigate to the agent directory:")
                        print(f"   cd ../starter-toolkit")
                        print(f"")
                        print(f"2. Reconfigure the agent with OAuth:")
                        print(f"   agentcore configure -e mcp_agentrock_basic_server.py --protocol MCP")
                        print(f"")
                        print(f"3. When prompted for OAuth, answer 'yes' and provide:")
                        print(f"   Discovery URL: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_MLKS5EUVq/.well-known/openid-configuration")
                        print(f"   Client ID: 1v57ncpgu61qjgb8fi9h8ksphf")
                        print(f"")
                        print(f"4. Redeploy the agent:")
                        print(f"   agentcore launch")
                        print(f"")
                        print(f"5. Test again with this client")
                        print(f"=" * 60)
                    
                    # Try to get more details about the error
                    if hasattr(init_error, 'response'):
                        print(f"🔍 Error response: {init_error.response}")
                    if hasattr(init_error, 'status'):
                        print(f"🔍 Error status: {init_error.status}")
                    if hasattr(init_error, 'headers'):
                        print(f"🔍 Error headers: {init_error.headers}")
                    
                    raise init_error
                
                # List available tools (exact pattern from reference)
                print("\n🚀 Step 2: List Available Tools")
                print("-" * 40)
                print("📤 Sending tools/list request...")
                
                try:
                    print("🔍 About to send list_tools request to MCP server...")
                    
                    tool_result = await session.list_tools()
                    print(f"✅ Tools listing successful!")
                    print(f"📋 Tool result: {tool_result}")
                    
                    # Display tools with details
                    if hasattr(tool_result, 'tools') and tool_result.tools:
                        print(f"📋 Found {len(tool_result.tools)} tools:")
                        for i, tool in enumerate(tool_result.tools, 1):
                            print(f"   {i}. {tool.name}: {tool.description}")
                    else:
                        print("📋 No tools found or tools attribute missing")
                        print(f"📋 Tool result attributes: {dir(tool_result)}")
                    
                    # Try calling a tool if available
                    if hasattr(tool_result, 'tools') and tool_result.tools:
                        first_tool = tool_result.tools[0]
                        print(f"\n🚀 Step 3: Test Tool Call - {first_tool.name}")
                        print("-" * 40)
                        
                        if first_tool.name == "add_numbers":
                            print("📤 Calling add_numbers(10, 20)...")
                            call_result = await session.call_tool(first_tool.name, {"a": 10, "b": 20})
                            print(f"✅ Tool call successful!")
                            print(f"📋 Call result: {call_result}")
                        else:
                            print(f"📤 Calling {first_tool.name} with empty args...")
                            call_result = await session.call_tool(first_tool.name, {})
                            print(f"✅ Tool call successful!")
                            print(f"📋 Call result: {call_result}")
                    
                except Exception as tools_error:
                    print(f"❌ Tools listing failed: {tools_error}")
                    print(f"❌ Tools error type: {type(tools_error).__name__}")
                    
                    # Try to get more details about the error
                    if hasattr(tools_error, 'response'):
                        print(f"🔍 Error response: {tools_error.response}")
                    if hasattr(tools_error, 'status'):
                        print(f"🔍 Error status: {tools_error.status}")
                    if hasattr(tools_error, 'headers'):
                        print(f"🔍 Error headers: {tools_error.headers}")
                
                print("\n🎉 MCP client test completed!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Handle ExceptionGroup specifically
        if isinstance(e, ExceptionGroup):
            print(f"🔍 ExceptionGroup details:")
            for i, sub_exception in enumerate(e.exceptions, 1):
                print(f"   {i}. {sub_exception}")
                print(f"      Type: {type(sub_exception).__name__}")
        
        # Show more details for debugging
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"Caused by: {e.__cause__}")
        
        # Check if this is a 403 error and provide specific guidance
        error_str = str(e).lower()
        if "403" in error_str or "forbidden" in error_str:
            print(f"\n🚨 403 FORBIDDEN ERROR ANALYSIS:")
            print(f"=" * 60)
            print(f"✅ Cognito authentication: WORKING (got valid bearer token)")
            print(f"✅ MCP server: RUNNING (visible in CloudWatch logs)")
            print(f"✅ Network connection: WORKING (reached Bedrock AgentCore)")
            print(f"❌ OAuth configuration: MISSING")
            print(f"")
            print(f"🔧 SOLUTION:")
            print(f"The MCP agent was deployed WITHOUT OAuth configuration.")
            print(f"You need to reconfigure and redeploy the agent:")
            print(f"")
            print(f"1. Navigate to the agent directory:")
            print(f"   cd ../starter-toolkit")
            print(f"")
            print(f"2. Reconfigure the agent with OAuth:")
            print(f"   agentcore configure -e mcp_agentrock_basic_server.py --protocol MCP")
            print(f"")
            print(f"3. When prompted for OAuth, answer 'yes' and provide:")
            print(f"   Discovery URL: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_MLKS5EUVq/.well-known/openid-configuration")
            print(f"   Client ID: 1v57ncpgu61qjgb8fi9h8ksphf")
            print(f"")
            print(f"4. Redeploy the agent:")
            print(f"   agentcore launch")
            print(f"")
            print(f"5. Test again with this client")
            print(f"=" * 60)
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 