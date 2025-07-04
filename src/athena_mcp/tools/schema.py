"""
Schema discovery tools for AWS Athena MCP Server.

Simple tools for discovering database and table schemas.
"""

import json
from typing import TYPE_CHECKING, Optional

from ..athena import AthenaClient, AthenaError

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_schema_tools(mcp: "FastMCP", athena_client: AthenaClient) -> None:
    """Register schema-related MCP tools."""

    @mcp.tool()
    async def list_tables(database: str, search: Optional[str] = None) -> str:
        """
        List all tables in the specified Athena database.

        Args:
            database: The Athena database to list tables from
            search: Optional search string to filter tables

        Returns:
            JSON string with list of tables
        """
        try:
            if not database.strip():
                raise ValueError("Database name cannot be empty")

            database_info = await athena_client.list_tables(database, search)
            return json.dumps(database_info.dict(), indent=2)

        except AthenaError as e:
            return json.dumps(
                {"error": e.message, "code": e.code, "query_execution_id": e.query_execution_id},
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e), "code": "INVALID_REQUEST"}, indent=2)

    @mcp.tool()
    async def describe_table(database: str, table_name: str) -> str:
        """
        Get detailed schema information for a specific table.

        Args:
            database: The Athena database containing the table
            table_name: The name of the table to describe

        Returns:
            JSON string with table schema information
        """
        try:
            if not database.strip():
                raise ValueError("Database name cannot be empty")
            if not table_name.strip():
                raise ValueError("Table name cannot be empty")

            table_info = await athena_client.describe_table(database, table_name)
            return json.dumps(table_info.dict(), indent=2)

        except AthenaError as e:
            return json.dumps(
                {"error": e.message, "code": e.code, "query_execution_id": e.query_execution_id},
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e), "code": "INVALID_REQUEST"}, indent=2)
