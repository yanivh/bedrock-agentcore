# bedrock-agentcore
capabilities to deploy and operate agents securely, at scale using any agentic framework and any LLM model.


   cd /Users/agozlan/Bebbel/code/bedrock-agentcore/starter-toolkit
   agentcore configure --entrypoint agent_example.py
   agentcore launch

    -- mcp
    agentcore configure -e mcp_agentrock_basic_server.py --protocol MCP

    When prompted for OAuth, provide:

    Discovery URL: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_MLKS5EUVq/.well-known/openid-configuration

    Client ID: 1v57ncpgu61qjgb8fi9h8ksphf

   agentcore launch

   bash test_mcp_with_cognito.sh

    --- mcp ends 

   mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data_mcp-SasgiU4udw/invocations?qualifier=DEFAULT"
    headers = {
        "Content-Type": "application/json"
    }


curl -X POST https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data_mcp-SasgiU4udw/invocations?qualifier=DEFAULT \
-H "Content-Type: application/json"



curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "where is ledro  located in italy  !"}'