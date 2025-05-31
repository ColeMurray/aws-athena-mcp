"""
Tests for configuration module.
"""

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from athena_mcp.config import Config


class TestConfig:
    """Test configuration loading and validation."""

    def test_from_env_success(self):
        """Test successful configuration loading from environment."""
        env_vars = {
            "ATHENA_S3_OUTPUT_LOCATION": "s3://test-bucket/results/",
            "AWS_REGION": "us-west-2",
            "ATHENA_WORKGROUP": "test-workgroup",
            "ATHENA_TIMEOUT_SECONDS": "120",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()

            assert config.s3_output_location == "s3://test-bucket/results/"
            assert config.aws_region == "us-west-2"
            assert config.athena_workgroup == "test-workgroup"
            assert config.timeout_seconds == 120

    def test_from_env_defaults(self):
        """Test configuration with default values."""
        env_vars = {"ATHENA_S3_OUTPUT_LOCATION": "s3://test-bucket/results/"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()

            assert config.s3_output_location == "s3://test-bucket/results/"
            assert config.aws_region == "us-east-1"  # default
            assert config.athena_workgroup is None  # default
            assert config.timeout_seconds == 60  # default

    def test_missing_required_env_var(self):
        """Test error when required environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="ATHENA_S3_OUTPUT_LOCATION environment variable is required"
            ):
                Config.from_env()

    def test_invalid_s3_path(self):
        """Test error when S3 path is invalid."""
        env_vars = {"ATHENA_S3_OUTPUT_LOCATION": "invalid-path"}

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="must be a valid S3 path"):
                Config.from_env()

    def test_invalid_timeout(self):
        """Test error when timeout is invalid."""
        env_vars = {
            "ATHENA_S3_OUTPUT_LOCATION": "s3://test-bucket/results/",
            "ATHENA_TIMEOUT_SECONDS": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="must be a positive integer"):
                Config.from_env()

    def test_zero_timeout(self):
        """Test error when timeout is zero."""
        env_vars = {
            "ATHENA_S3_OUTPUT_LOCATION": "s3://test-bucket/results/",
            "ATHENA_TIMEOUT_SECONDS": "0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="Timeout must be at least 1 second"):
                Config.from_env()

    def test_str_representation(self):
        """Test string representation doesn't expose sensitive data."""
        env_vars = {"ATHENA_S3_OUTPUT_LOCATION": "s3://test-bucket/results/"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            config_str = str(config)

            assert "s3://test-bucket/results/" in config_str
            assert "us-east-1" in config_str
            assert "60" in config_str
