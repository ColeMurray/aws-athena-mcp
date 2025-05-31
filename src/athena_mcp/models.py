"""
Data models for AWS Athena MCP Server.

Simple, clean Pydantic models for type safety and validation.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryState(str, Enum):
    """Athena query execution states."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class QueryRequest(BaseModel):
    """Request to execute a query."""

    database: str = Field(..., description="The Athena database to query")
    query: str = Field(..., description="SQL query to execute")
    max_rows: int = Field(1000, ge=1, le=10000, description="Maximum rows to return")


class QueryResult(BaseModel):
    """Result of a completed query."""

    query_execution_id: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    bytes_scanned: int = 0
    execution_time_ms: int = 0


class QueryStatus(BaseModel):
    """Status of a query execution."""

    query_execution_id: str
    state: QueryState
    state_change_reason: Optional[str] = None
    bytes_scanned: int = 0
    execution_time_ms: int = 0


class TableInfo(BaseModel):
    """Information about a database table."""

    database: str
    table_name: str
    columns: List[Dict[str, str]]  # [{"name": "col1", "type": "string", "comment": "..."}]


class DatabaseInfo(BaseModel):
    """Information about a database."""

    database: str
    tables: List[str]
    table_count: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    code: str
    query_execution_id: Optional[str] = None
