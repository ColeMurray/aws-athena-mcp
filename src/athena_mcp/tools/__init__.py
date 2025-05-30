"""
Tools package for AWS Athena MCP Server.

Contains modular tool registration functions.
"""

from .query import register_query_tools
from .schema import register_schema_tools

__all__ = ["register_query_tools", "register_schema_tools"] 