#!/usr/bin/env python3
"""
Script to check CloudWatch logs for the Lambda function.
"""

import boto3
import json
from datetime import datetime, timedelta

def check_lambda_logs():
    """Check the latest logs from the Lambda function."""
    
    # Initialize CloudWatch Logs client
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    log_group_name = "/aws/lambda/bedrock-agentcore-lambda-agentcore_babbel_data_team"
    
    try:
        # Get the latest log stream
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not response['logStreams']:
            print("No log streams found.")
            return
        
        latest_stream = response['logStreams'][0]['logStreamName']
        print(f"Latest log stream: {latest_stream}")
        
        # Get the latest events
        events_response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=latest_stream,
            limit=20
        )
        
        print("\nLatest log events:")
        print("-" * 50)
        
        for event in events_response['events']:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {event['message']}")
            
    except Exception as e:
        print(f"Error checking logs: {e}")

if __name__ == "__main__":
    check_lambda_logs() 