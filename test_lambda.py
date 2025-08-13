#!/usr/bin/env python3
"""
Test script for the Bedrock AgentCore Lambda function.
This script calls the test script in the terraform directory.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main test function."""
    
    # Change to terraform directory
    terraform_dir = Path("terraform")
    if not terraform_dir.exists():
        print("Error: terraform directory not found.")
        exit(1)
    
    # Change to terraform directory
    os.chdir(terraform_dir)
    
    print("Running tests from terraform directory...")
    
    try:
        # Run the test script
        subprocess.run([sys.executable, "test_lambda.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during testing: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 