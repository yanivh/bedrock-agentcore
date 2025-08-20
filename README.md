# bedrock-agentcore

A comprehensive toolkit for deploying and operating agents securely at scale using any agentic framework and any LLM model, with specialized support for MCP (Model Context Protocol).

## 📁 Project Structure

```
bedrock-agentcore/
├── 📂 starter-toolkit-mcp/          # MCP (Model Context Protocol) implementation
│   ├── mcp_agentrock_basic_server.py    # MCP server with AWS Glue tools
│   ├── my_mcp_client_remote.py          # Local MCP client for testing
│   ├── test_mcp_with_cognito.sh         # Automated testing script
│   ├── get_cognito_token.py             # Cognito authentication helper
│   ├── .bedrock_agentcore.yaml          # Agent deployment configuration
│   ├── Dockerfile                       # Container definition
│   └── requirements.txt                 # Python dependencies
│
├── 📂 starter-toolkit/              # Standard agent implementation
│   ├── agent_example.py                 # Basic agent example
│   ├── .bedrock_agentcore.yaml          # Agent configuration
│   └── Dockerfile                       # Container definition
│
├── 📂 terraform/                    # Infrastructure as Code
│   ├── main.tf                          # Terraform main configuration
│   ├── lambda_function.py               # Lambda deployment scripts
│   └── deploy_lambda.py                 # Lambda deployment helper
│
├── 🔧 Configuration Files
│   ├── pyproject.toml                   # Python project configuration
│   ├── requirements.txt                 # Root dependencies
│   ├── mcp.json                         # MCP-specific configuration
│   └── setup_env.sh                     # Environment setup script
│
└── 🛠️ Utilities
    ├── debug_agent_runtime.py           # Runtime debugging tools
    ├── check_agent_config.py            # Configuration validation
    └── check_logs.py                    # Log analysis tools
```

## 🚀 Quick Start Guide

### Prerequisites
- AWS CLI configured with appropriate permissions
- run ```aws sso login ```
- Python 3.10+ (automatically checked by setup script)
- Docker installed
- AgentCore CLI installed

### 🔧 Environment Setup (Required First)

**1. Clone and navigate to the project:**
```bash
git clone <repository-url>
cd bedrock-agentcore
```

**2. Run the automated environment setup:**
```bash
bash setup_env.sh
```

This script will automatically:
- ✅ Check for Python 3.10+ requirement
- ✅ Install `uv` package manager if not present
- ✅ Create virtual environment (`.venv`)
- ✅ Initialize uv project
- ✅ Install all dependencies from `requirements.txt`

**3. Activate the environment for future sessions:**
```bash
source .venv/bin/activate
# Or use the provided activation scripts:
source activate_env.sh     # For bash/zsh
source activate_env.fish    # For fish shell
```

### Option 1: MCP (Model Context Protocol) Deployment

**Navigate to MCP directory:**
```bash
cd starter-toolkit-mcp/
```

**1. Install MCP-specific dependencies:**
```bash
uv pip install -r requirements.txt
```

**2. Configure the MCP Agent:**
usually this happen only on init the Agent Runtime creation , not need to repeat when changing code for the mcp
```bash
agentcore configure -e mcp_agentrock_basic_server.py --protocol MCP
```

**3. When prompted for OAuth configuration, provide:**
- **Discovery URL:** `https://cognito-idp.us-east-1.amazonaws.com/us-east-1_MLKS5EUVq/.well-known/openid-configuration`
- **Client ID:** `1v57ncpgu61qjgb8fi9h8ksphf`

**4. Deploy to AWS:**
this step can be repeated once new code intreduce to the mcp
```bash
agentcore launch
```

**5. Test the deployment:**
```bash
bash test_mcp_with_cognito.sh
```

## 🔧 MCP Client-Server Architecture

The reason we use `my_mcp_client_remote.py` to test `mcp_agentrock_basic_server.py` is because they serve different roles in the **MCP (Model Context Protocol) client-server architecture**:

### 🖥️ **Server Side: `mcp_agentrock_basic_server.py`**
- **Role**: This is the **MCP server** that provides tools and functionality
- **Where it runs**: Deployed on **AWS Bedrock AgentCore** infrastructure  
- **What it does**: 
  - Defines MCP tools like `add_numbers()`, `multiply_numbers()`, `get_glue_table_schema()`
  - Uses `FastMCP` to create an HTTP-accessible MCP server
  - Gets containerized and deployed to AWS via `agentcore launch`
- **URL**: `https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{agent_arn}/invocations`

### 📱 **Client Side: `my_mcp_client_remote.py`**
- **Role**: This is the **MCP client** that connects to and tests the remote server
- **Where it runs**: Locally on your development machine
- **What it does**:
  - Connects to the deployed MCP server via HTTP
  - Handles authentication (Cognito tokens, AWS credentials)
  - Tests the MCP protocol by calling `session.initialize()`, `session.list_tools()`, `session.call_tool()`
  - Validates that the deployed server works correctly

### 🔄 **The Testing Flow**

```
Local Machine                     AWS Bedrock AgentCore
┌─────────────────────┐          ┌──────────────────────┐
│ my_mcp_client_remote│  ────────▶│ mcp_agentrock_basic_ │
│ .py                 │  HTTP/MCP │ server.py           │
│                     │  requests │                     │
│ - Authentication    │          │ - Tool definitions   │
│ - Protocol testing  │          │ - Business logic     │
│ - Error handling    │          │ - AWS integrations   │
└─────────────────────┘          └──────────────────────┘
```

### 📋 **Why We Need Both**

1. **Separation of Concerns**: 
   - Server focuses on **providing functionality**
   - Client focuses on **consuming and testing** that functionality

2. **Remote Testing**: 
   - The server runs on AWS infrastructure, not locally
   - We need a client to verify it works from the outside

3. **Authentication Testing**:
   - The client handles complex Cognito authentication 
   - Tests that the OAuth configuration is working correctly

4. **Protocol Validation**:
   - Ensures the MCP protocol is working end-to-end
   - Tests real network conditions, not just local code

## 🛠️ Available MCP Tools

The MCP server provides the following tools:

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `add_numbers` | Add two integers | `add_numbers(10, 20)` → `30` |
| `multiply_numbers` | Multiply two integers | `multiply_numbers(5, 6)` → `30` |
| `greet_user` | Greet a user by name | `greet_user("Alice")` → `"Hello, Alice!"` |
| `get_glue_table_schema` | Extract AWS Glue table schema | Get column info, data types, metadata |
| `list_glue_tables_in_database` | List tables in Glue database | Get table names and basic info |

## 🔐 Authentication Setup

The MCP implementation uses **AWS Cognito** for authentication:

- **Cognito User Pool ID**: `us-east-1_MLKS5EUVq`
- **Client ID**: `1v57ncpgu61qjgb8fi9h8ksphf`
- **Region**: `us-east-1`

Authentication tokens are automatically managed by the test scripts.

## 📊 Example Usage

**Test AWS Glue integration:**
```bash
# After deployment, use in playground or Cursor with prompt:
"use list_glue_tables_in_database to get tables in database name b2b-data and region eu-west-1"
```

## 🔧 Configuration Details

Looking at the `.bedrock_agentcore.yaml`, we can see:
- `entrypoint: mcp_agentrock_basic_server.py` - This gets deployed as the server
- `server_protocol: MCP` - Confirms it's using MCP protocol
- `customJWTAuthorizer` - Shows authentication is configured

## 🐛 Troubleshooting

**Common Issues:**

1. **403 Forbidden errors**: Agent needs OAuth reconfiguration
2. **Token errors**: Run `get_cognito_token.py` to refresh
3. **Connection issues**: Check AWS credentials and region settings

**Debug tools:**
- `debug_agent_runtime.py` - Runtime debugging
- `check_agent_config.py` - Configuration validation
- `check_logs.py` - Log analysis

## 📚 Summary

- **`mcp_agentrock_basic_server.py`** gets deployed to AWS as your MCP server
- **`my_mcp_client_remote.py`** is your local testing tool to verify deployment
- **Authentication** is handled via AWS Cognito with JWT tokens
- **Tools** provide AWS Glue integration and basic mathematical operations
- **Testing** is automated via the provided shell scripts