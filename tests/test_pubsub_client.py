"""Tests for PubSubClient class."""

import queue
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from core.pubsub_client import PubSubClient


class TestPubSubClient:
    """Test suite for PubSubClient."""

    @pytest.fixture
    def mock_sio(self):
        """Create a mock Socket.IO client."""
        with patch("core.pubsub_client.socketio.Client") as mock:
            yield mock.return_value

    @pytest.fixture
    def client(self, mock_sio):
        """Create a PubSubClient instance with mocked Socket.IO."""
        with patch("core.pubsub_client.socketio.Client", return_value=mock_sio):
            client = PubSubClient(url="http://localhost:5000", consumer="test_consumer", topics=["topic1", "topic2"])
            return client

    def test_client_initialization(self):
        """Test client initialization with correct parameters."""
        with patch("core.pubsub_client.socketio.Client") as mock_sio_class:
            mock_sio = MagicMock()
            mock_sio_class.return_value = mock_sio

            client = PubSubClient(url="http://localhost:5000/", consumer="alice", topics=["orders", "trades"])

            assert client.url == "http://localhost:5000"
            assert client.consumer == "alice"
            assert client.topics == ["orders", "trades"]
            assert client.handlers == {}
            assert isinstance(client.message_queue, queue.Queue)
            assert client.running is False

            # Verify Socket.IO client configuration
            mock_sio_class.assert_called_once_with(
                reconnection=True, reconnection_attempts=0, reconnection_delay=2000, reconnection_delay_max=10000
            )

            # Verify event handlers are registered
            assert mock_sio.on.call_count == 4
            mock_sio.on.assert_any_call("connect", client.on_connect)
            mock_sio.on.assert_any_call("message", client.on_message)
            mock_sio.on.assert_any_call("disconnect", client.on_disconnect)
            mock_sio.on.assert_any_call("new_message", client.on_new_message)

    def test_register_handler(self, client):
        """Test registering custom handlers for topics."""
        handler1 = Mock()
        handler2 = Mock()

        client.register_handler("topic1", handler1)
        client.register_handler("topic2", handler2)

        assert client.handlers["topic1"] == handler1
        assert client.handlers["topic2"] == handler2

    def test_on_connect(self, client):
        """Test connection handling."""
        with patch.object(client.sio, "emit") as mock_emit, patch("threading.Thread") as mock_thread:
            client.on_connect()

            # Verify subscription message is sent
            mock_emit.assert_called_once_with(
                "subscribe", {"consumer": "test_consumer", "topics": ["topic1", "topic2"]}
            )

            # Verify processing thread is started
            assert client.running is True
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()

    def test_on_message_queuing(self, client):
        """Test that messages are properly queued."""
        test_data = {
            "topic": "topic1",
            "message_id": "msg_123",
            "message": {"content": "test"},
            "producer": "producer1",
        }

        client.on_message(test_data)

        # Verify message is in queue
        assert not client.message_queue.empty()
        queued_data = client.message_queue.get_nowait()
        assert queued_data == test_data

    def test_process_queue_with_handler(self, client):
        """Test message processing with registered handler."""
        handler = Mock()
        client.register_handler("topic1", handler)
        client.running = True

        test_message = {
            "topic": "topic1",
            "message_id": "msg_123",
            "message": {"data": "test"},
            "producer": "producer1",
        }

        client.message_queue.put(test_message)

        with patch.object(client.sio, "emit") as mock_emit:
            # Run process_queue in a thread
            thread = threading.Thread(target=client.process_queue)
            thread.daemon = True
            thread.start()

            # Give time for processing
            time.sleep(0.1)
            client.running = False
            thread.join(timeout=2)

            # Verify handler was called
            handler.assert_called_once_with({"data": "test"})

            # Verify consumption confirmation was sent
            mock_emit.assert_called_with(
                "consumed",
                {"consumer": "test_consumer", "topic": "topic1", "message_id": "msg_123", "message": {"data": "test"}},
            )

    def test_process_queue_without_handler(self, client):
        """Test message processing when no handler is registered."""
        client.running = True

        test_message = {"topic": "unknown_topic", "message_id": "msg_123", "message": "test", "producer": "producer1"}

        client.message_queue.put(test_message)

        with patch.object(client.sio, "emit") as mock_emit:
            # Run process_queue briefly
            thread = threading.Thread(target=client.process_queue)
            thread.daemon = True
            thread.start()

            time.sleep(0.1)
            client.running = False
            thread.join(timeout=2)

            # Consumption should still be confirmed even without handler
            mock_emit.assert_called_with(
                "consumed",
                {"consumer": "test_consumer", "topic": "unknown_topic", "message_id": "msg_123", "message": "test"},
            )

    def test_process_queue_handler_exception(self, client):
        """Test that handler exceptions are caught and processing continues."""
        handler = Mock(side_effect=Exception("Handler error"))
        client.register_handler("topic1", handler)
        client.running = True

        test_message = {"topic": "topic1", "message_id": "msg_123", "message": "test", "producer": "producer1"}

        client.message_queue.put(test_message)

        with patch.object(client.sio, "emit") as mock_emit:
            thread = threading.Thread(target=client.process_queue)
            thread.daemon = True
            thread.start()

            time.sleep(0.1)
            client.running = False
            thread.join(timeout=2)

            # Handler should have been called despite exception
            handler.assert_called_once()

            # Consumption should still be confirmed
            mock_emit.assert_called()

    def test_on_disconnect(self, client):
        """Test disconnection handling."""
        client.running = True
        client.on_disconnect()

        assert client.running is False

    def test_publish_success(self, client):
        """Test successful message publishing."""
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_post.return_value = mock_response

            client.publish(topic="topic1", message={"data": "test"}, producer="test_producer", message_id="msg_123")

            # Verify POST request
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:5000/publish"

            json_data = call_args[1]["json"]
            assert json_data["topic"] == "topic1"
            assert json_data["message"] == {"data": "test"}
            assert json_data["producer"] == "test_producer"
            assert json_data["message_id"] == "msg_123"

    def test_publish_connection_error(self, client):
        """Test publishing with connection error."""
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

            # Should not raise exception
            client.publish(topic="topic1", message="test", producer="test_producer", message_id="msg_123")

            mock_post.assert_called_once()

    def test_publish_http_error(self, client):
        """Test publishing with HTTP error response."""
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            http_error = requests.exceptions.HTTPError()
            http_error.response = mock_response
            mock_response.raise_for_status.side_effect = http_error
            mock_post.return_value = mock_response

            # Should not raise exception
            client.publish(topic="topic1", message="test", producer="test_producer", message_id="msg_123")

            mock_post.assert_called_once()

    def test_start_client(self, client):
        """Test starting the client."""
        with patch.object(client.sio, "connect") as mock_connect, patch.object(client.sio, "wait") as mock_wait:
            client.start()

            mock_connect.assert_called_once_with("http://localhost:5000")
            mock_wait.assert_called_once()

    def test_url_trailing_slash_removal(self):
        """Test that trailing slash is removed from URL."""
        with patch("core.pubsub_client.socketio.Client"):
            client = PubSubClient(url="http://localhost:5000///", consumer="test", topics=[])
            assert client.url == "http://localhost:5000"

    def test_multiple_handlers_same_topic(self, client):
        """Test that only the last registered handler is used for a topic."""
        handler1 = Mock()
        handler2 = Mock()

        client.register_handler("topic1", handler1)
        client.register_handler("topic1", handler2)

        assert client.handlers["topic1"] == handler2
        assert len(client.handlers) == 1

    def test_on_new_message(self, client):
        """Test new message event handling."""
        test_data = {"test": "data"}

        # Should just log, not raise exception
        client.on_new_message(test_data)
