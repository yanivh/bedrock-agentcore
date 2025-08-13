import json
import boto3
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function to invoke Bedrock AgentCore.
    
    Expected event structure:
    {
        "input_text": "Hello, how can you assist me today?",
        "agent_runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam",
        "region": "us-east-1",
        "qualifier": "DEFAULT"
    }
    """
    
    try:
        # Extract parameters from the event with defaults
        input_text = event.get('input_text', 'What is the weather like in New York?')
        agent_runtime_arn = event.get('agent_runtime_arn', 'arn:aws:bedrock-agentcore:us-east-1:301581146302:runtime/bedrock_agentrock_data-9WCS993Xam')
        region = event.get('region', 'us-east-1')
        qualifier = event.get('qualifier', 'DEFAULT')
        
        # Initialize Bedrock AgentCore client
        client = boto3.client('bedrock-agentcore', region_name=region)
        
        logger.info(f"Using agent runtime ARN: {agent_runtime_arn}")
        logger.info(f"Invoking Bedrock AgentCore with input: {input_text}")
        
        # Create the proper payload format for Bedrock AgentCore
        # The payload should be a JSON string containing the user's input
        payload_json = json.dumps({
            "prompt": input_text
        })
        
        logger.info(f"Payload being sent: {payload_json}")
        
        # Invoke the agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier=qualifier,
            payload=payload_json
        )
        
        logger.info(f"Raw response: {response}")
        
        # Extract and process the response
        response_body = response.get('response', {})
        response_content = ""
        
        # Handle different response formats
        if hasattr(response_body, 'read'):
            # If it's a StreamingBody, read the content
            response_content = response_body.read().decode('utf-8')
            logger.info(f"StreamingBody content: {response_content}")
        elif isinstance(response_body, dict):
            # If it's already a dict, extract the content
            response_content = response_body.get('content', str(response_body))
        else:
            # Otherwise, convert to string
            response_content = str(response_body)
        
        # Try to parse as JSON if it looks like JSON
        try:
            if response_content.strip().startswith('{'):
                parsed_response = json.loads(response_content)
                response_content = parsed_response.get('content', response_content)
        except json.JSONDecodeError:
            # If it's not valid JSON, use as-is
            pass
        
        logger.info(f"Final response content: {response_content}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'response': response_content,
                'input_text': input_text,
                'agent_runtime_arn': agent_runtime_arn,
                'raw_response': response
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"Error invoking Bedrock AgentCore: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}',
                'error_type': str(type(e))
            })
        } 