#!/usr/bin/env python3
"""
Setup script for configuring AWS Athena MCP with Claude Desktop.

This script helps users configure their Claude Desktop to use the AWS Athena MCP server.
"""

import json
import os
import sys
from pathlib import Path
import platform


def get_claude_config_path():
    """Get the Claude Desktop configuration file path for the current OS."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:
        # Linux or other Unix-like systems
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"


def create_config():
    """Create the MCP server configuration."""
    s3_location = input("Enter your S3 output location (e.g., s3://my-bucket/athena-results/): ").strip()
    if not s3_location:
        print("❌ S3 output location is required!")
        return None
    
    aws_region = input("Enter AWS region [us-east-1]: ").strip() or "us-east-1"
    workgroup = input("Enter Athena workgroup [primary]: ").strip() or "primary"
    timeout = input("Enter timeout in seconds [60]: ").strip() or "60"
    
    return {
        "mcpServers": {
            "aws-athena-mcp": {
                "command": "uvx",
                "args": ["aws-athena-mcp"],
                "env": {
                    "ATHENA_S3_OUTPUT_LOCATION": s3_location,
                    "AWS_REGION": aws_region,
                    "ATHENA_WORKGROUP": workgroup,
                    "ATHENA_TIMEOUT_SECONDS": timeout
                }
            }
        }
    }


def update_claude_config(config_path, new_config):
    """Update the Claude Desktop configuration file."""
    # Read existing config if it exists
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not read existing config: {e}")
            print("Creating new configuration file...")
    
    # Merge configurations
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["aws-athena-mcp"] = new_config["mcpServers"]["aws-athena-mcp"]
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write updated config
    with open(config_path, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    return existing_config


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("\n🔍 Checking AWS credentials...")
    
    # Check environment variables
    if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
        print("✅ AWS credentials found in environment variables")
        return True
    
    # Check AWS profile
    if os.environ.get("AWS_PROFILE"):
        print(f"✅ AWS profile found: {os.environ.get('AWS_PROFILE')}")
        return True
    
    # Check AWS credentials file
    aws_creds_file = Path.home() / ".aws" / "credentials"
    if aws_creds_file.exists():
        print("✅ AWS credentials file found")
        return True
    
    print("⚠️  No AWS credentials found!")
    print("Please configure AWS credentials using one of these methods:")
    print("  1. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
    print("  2. AWS CLI: aws configure")
    print("  3. AWS profile: export AWS_PROFILE=your-profile")
    return False


def main():
    """Main setup function."""
    print("🚀 AWS Athena MCP Setup for Claude Desktop")
    print("=" * 50)
    
    # Check if uvx is available
    try:
        import subprocess
        subprocess.run(["uvx", "--version"], capture_output=True, check=True)
        print("✅ uvx is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uvx is not installed or not available")
        print("Please install uvx first: https://github.com/astral-sh/uv")
        return 1
    
    # Get Claude config path
    config_path = get_claude_config_path()
    print(f"📁 Claude config path: {config_path}")
    
    # Create configuration
    print("\n📝 Creating MCP server configuration...")
    new_config = create_config()
    if not new_config:
        return 1
    
    # Update Claude config
    try:
        updated_config = update_claude_config(config_path, new_config)
        print(f"✅ Configuration saved to {config_path}")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return 1
    
    # Check AWS credentials
    check_aws_credentials()
    
    # Show final configuration
    print("\n📋 Final configuration:")
    print(json.dumps(updated_config, indent=2))
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Restart Claude Desktop")
    print("2. Verify the connection by asking Claude to list your Athena databases")
    print("3. Example: 'List all tables in my default database'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 