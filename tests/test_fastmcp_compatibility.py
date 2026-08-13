"""FastMCP compatibility tests for the server's public tool contract."""

import json
from unittest.mock import MagicMock

import pytest
from fastmcp import Client, FastMCP

from athena_mcp.athena import AthenaClient
from athena_mcp.tools import register_query_tools, register_schema_tools


@pytest.fixture
def mcp_server() -> FastMCP:
    """Create the MCP server without requiring AWS configuration or credentials."""
    server = FastMCP(name="aws-athena-mcp", version="1.0.0")
    athena_client = MagicMock(spec=AthenaClient)
    register_query_tools(server, athena_client)
    register_schema_tools(server, athena_client)
    return server


async def test_tools_are_discoverable_and_callable(mcp_server: FastMCP) -> None:
    """Verify the FastMCP APIs used by the server work through an MCP client."""
    async with Client(mcp_server) as client:
        tools = await client.list_tools()
        result = await client.call_tool("run_query", {"database": "", "query": "SELECT 1"})

    assert {tool.name for tool in tools} == {
        "run_query",
        "get_status",
        "get_result",
        "list_tables",
        "describe_table",
    }
    assert not result.is_error
    assert json.loads(result.content[0].text) == {
        "error": "Database name cannot be empty",
        "code": "INVALID_REQUEST",
    }
