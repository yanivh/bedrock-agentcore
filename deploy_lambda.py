#!/usr/bin/env python3
"""
Deployment script for the Bedrock AgentCore Lambda function.
This script calls the deployment script in the terraform directory.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main deployment function."""
    
    # Change to terraform directory
    terraform_dir = Path("terraform")
    if not terraform_dir.exists():
        print("Error: terraform directory not found.")
        exit(1)
    
    # Change to terraform directory
    os.chdir(terraform_dir)
    
    print("Running deployment from terraform directory...")
    
    try:
        # Run the deployment script
        subprocess.run([sys.executable, "deploy_lambda.py"], check=True)
        
        print("\nDeployment completed successfully!")
        print("Files created in terraform/ directory:")
        print("- bedrock_agentcore_lambda.zip")
        print("- terraform_lambda.tf")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 