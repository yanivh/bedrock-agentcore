#!/usr/bin/env python3
"""
Get bearer token from Cognito for MCP authentication.
This script authenticates with Cognito and retrieves an access token
that can be used with the MCP client.
"""

import boto3
import json
import os
import sys
import argparse
from botocore.exceptions import ClientError, NoCredentialsError

def get_cognito_token(pool_id, client_id, username, password, region='us-east-1'):
    """
    Authenticate with Cognito and get an access token.
    
    Args:
        pool_id: Cognito User Pool ID
        client_id: Cognito User Pool Client ID
        username: Username for authentication
        password: Password for authentication
        region: AWS region (default: us-east-1)
    
    Returns:
        dict: Authentication result with access token
    """
    try:
        # Create Cognito Identity Provider client
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        print(f"🔐 Authenticating with Cognito...")
        print(f"   Pool ID: {pool_id}")
        print(f"   Client ID: {client_id}")
        print(f"   Username: {username}")
        print(f"   Region: {region}")
        
        # Initiate authentication
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        if 'AuthenticationResult' in response:
            auth_result = response['AuthenticationResult']
            access_token = auth_result['AccessToken']
            
            print(f"✅ Authentication successful!")
            print(f"🎫 Access Token: {access_token[:20]}...")
            
            return {
                'access_token': access_token,
                'id_token': auth_result.get('IdToken'),
                'refresh_token': auth_result.get('RefreshToken'),
                'expires_in': auth_result.get('ExpiresIn'),
                'token_type': auth_result.get('TokenType', 'Bearer')
            }
        else:
            print(f"❌ Authentication failed: No AuthenticationResult in response")
            return None
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'NotAuthorizedException':
            print(f"❌ Authentication failed: Invalid username or password")
        elif error_code == 'UserNotConfirmedException':
            print(f"❌ User not confirmed. Please confirm the user first.")
        elif error_code == 'UserNotFoundException':
            print(f"❌ User not found: {username}")
        else:
            print(f"❌ Cognito error ({error_code}): {error_message}")
        
        return None
        
    except NoCredentialsError:
        print(f"❌ AWS credentials not found. Please configure your AWS credentials.")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def get_cognito_config_from_terraform():
    """
    Try to get Cognito configuration from Terraform outputs.
    """
    try:
        # Try to run terraform output
        import subprocess
        
        # Change to terraform directory
        terraform_dir = os.path.join(os.path.dirname(__file__), '..', 'terraform')
        
        if os.path.exists(terraform_dir):
            print(f"📋 Reading Terraform outputs from {terraform_dir}...")
            
            # Get terraform outputs
            result = subprocess.run(
                ['terraform', 'output', '-json'],
                cwd=terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                outputs = json.loads(result.stdout)
                
                return {
                    'pool_id': outputs.get('cognito_user_pool_id', {}).get('value'),
                    'client_id': outputs.get('cognito_client_id', {}).get('value'),
                    'discovery_url': outputs.get('cognito_discovery_url', {}).get('value'),
                    'test_user': outputs.get('test_user_credentials', {}).get('value', {})
                }
            else:
                print(f"⚠️  Could not read Terraform outputs: {result.stderr}")
                return None
        else:
            print(f"⚠️  Terraform directory not found: {terraform_dir}")
            return None
            
    except Exception as e:
        print(f"⚠️  Could not read Terraform config: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Get Cognito bearer token for MCP authentication')
    parser.add_argument('--pool-id', help='Cognito User Pool ID')
    parser.add_argument('--client-id', help='Cognito User Pool Client ID')
    parser.add_argument('--username', default='testuser', help='Username (default: testuser)')
    parser.add_argument('--password', default='SecurePass123!', help='Password')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--export', action='store_true', help='Output export commands')
    parser.add_argument('--from-terraform', action='store_true', help='Get config from Terraform outputs')
    
    args = parser.parse_args()
    
    print("🚀 Cognito Bearer Token Generator")
    print("=" * 50)
    
    # Try to get config from Terraform if requested or if no explicit config provided
    if args.from_terraform or (not args.pool_id or not args.client_id):
        terraform_config = get_cognito_config_from_terraform()
        
        if terraform_config:
            pool_id = args.pool_id or terraform_config['pool_id']
            client_id = args.client_id or terraform_config['client_id']
            
            # Use test user credentials if available
            if terraform_config['test_user']:
                username = args.username if args.username != 'testuser' else terraform_config['test_user'].get('username', 'testuser')
            else:
                username = args.username
        else:
            pool_id = args.pool_id
            client_id = args.client_id
            username = args.username
    else:
        pool_id = args.pool_id
        client_id = args.client_id
        username = args.username
    
    # Validate required parameters
    if not pool_id or not client_id:
        print("❌ Missing required parameters:")
        print("   Use --pool-id and --client-id, or --from-terraform")
        print("   Or run: python get_cognito_token.py --from-terraform")
        sys.exit(1)
    
    # Get the token
    token_info = get_cognito_token(
        pool_id=pool_id,
        client_id=client_id,
        username=username,
        password=args.password,
        region=args.region
    )
    
    if token_info:
        access_token = token_info['access_token']
        
        print(f"\n🎉 Token Retrieved Successfully!")
        print(f"=" * 50)
        print(f"🎫 Access Token: {access_token}")
        print(f"⏰ Expires in: {token_info.get('expires_in', 'Unknown')} seconds")
        
        if args.export:
            print(f"\n📋 Export Commands:")
            print(f"=" * 50)
            print(f"export BEARER_TOKEN='{access_token}'")
            print(f"export COGNITO_POOL_ID='{pool_id}'")
            print(f"export COGNITO_CLIENT_ID='{client_id}'")
        
        # Save to file for easy reuse
        token_file = os.path.join(os.path.dirname(__file__), '.bearer_token')
        with open(token_file, 'w') as f:
            f.write(access_token)
        print(f"\n💾 Token saved to: {token_file}")
        
        return True
    else:
        print(f"\n❌ Failed to get token")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 