#!/bin/bash

# Test MCP client with Cognito authentication
# This script sets up the environment and runs the MCP client

set -e

echo "🚀 MCP Client with Cognito Authentication"
echo "=========================================="

# Configuration
AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/mcp_agentrock_basic_server-r9jEKOHcJ5"

# Export the agent ARN
export AGENT_ARN="$AGENT_ARN"

echo "🔗 Agent ARN: $AGENT_ARN"

# Check if bearer token is already set
if [ -z "$BEARER_TOKEN" ]; then
    echo "🔐 No BEARER_TOKEN set. Will try to get one from Cognito..."
    
    # Try to get a fresh token
    echo "📋 Running token generator..."
    if uv run python get_cognito_token.py --from-terraform --export; then
        echo "✅ Token generation successful"
        
        # Try to source the token from the saved file
        if [ -f ".bearer_token" ]; then
            export BEARER_TOKEN=$(cat .bearer_token)
            echo "✅ Bearer token loaded from file"
        else
            echo "⚠️  No token file found, MCP client will try automatic methods"
        fi
    else
        echo "⚠️  Token generation failed, MCP client will try fallback methods"
    fi
else
    echo "✅ Using existing BEARER_TOKEN: ${BEARER_TOKEN:0:20}..."
fi

echo ""
echo "🚀 Starting MCP Client..."
echo "=========================="

# Run the MCP client
uv run python my_mcp_client_remote.py

echo ""
echo "🎉 MCP Client test completed!" 