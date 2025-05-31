"""
AWS Athena MCP Server

A simple, clean MCP server for AWS Athena integration.
"""

__version__ = "1.0.0"
__author__ = "AWS Athena MCP Contributors"


# All imports are lazy to avoid import issues
def Config():
    """Get the Config class."""
    from .config import Config as _Config

    return _Config


def create_server():
    """Create and configure the AWS Athena MCP server."""
    from .server import create_server as _create_server

    return _create_server()


def AthenaClient(config):
    """Create an Athena client."""
    from .athena import AthenaClient as _AthenaClient

    return _AthenaClient(config)


# Export main classes and functions
__all__ = ["create_server", "AthenaClient", "Config", "__version__"]
