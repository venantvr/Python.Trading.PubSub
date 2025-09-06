"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_message_data():
    """Provide sample message data for tests."""
    return {
        "topic": "test_topic",
        "message_id": "test_msg_123",
        "message": {"key": "value", "number": 42},
        "producer": "test_producer"
    }


@pytest.fixture
def sample_topics():
    """Provide sample topics list."""
    return ["orders", "trades", "market_data", "signals"]


@pytest.fixture
def mock_server_url():
    """Provide mock server URL."""
    return "http://localhost:5000"


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration for each test."""
    import logging
    # Reset logging to avoid interference between tests
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
