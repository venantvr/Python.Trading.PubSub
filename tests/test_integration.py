"""Integration tests for the PubSub system."""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.python_trading_pubsub.core.pubsub_client import PubSubClient


# noinspection PyUnresolvedReferences,PyShadowingNames
class TestPubSubIntegration:
    """Integration tests for PubSub system."""

    @pytest.fixture
    def mock_socketio_server(self):
        """Mock a Socket.IO server for integration testing."""
        with patch("src.python_trading_pubsub.core.pubsub_client.socketio.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Store callbacks registered by the client
            callbacks = {}

            def on_side_effect(event, callback):
                callbacks[event] = callback

            mock_client.on.side_effect = on_side_effect
            mock_client.callbacks = callbacks

            yield mock_client

    @pytest.fixture
    def integration_client(self, mock_socketio_server):
        """Create a client for integration testing."""
        client = PubSubClient(url="http://localhost:5000", consumer="integration_test", topics=["test_topic"])
        # Make callbacks accessible for testing
        client._test_callbacks = mock_socketio_server.callbacks
        return client

    def test_end_to_end_message_flow(self, integration_client):
        """Test complete message flow from publish to handler execution."""
        received_messages = []

        def message_handler(message):
            received_messages.append(message)

        # Register handler
        integration_client.register_handler("test_topic", message_handler)

        # Simulate connection
        if "connect" in integration_client._test_callbacks:
            integration_client._test_callbacks["connect"]()

        # Simulate receiving a message
        test_message = {
            "topic": "test_topic",
            "message_id": "test_123",
            "message": {"content": "integration test"},
            "producer": "test_producer",
        }

        if "message" in integration_client._test_callbacks:
            integration_client._test_callbacks["message"](test_message)

        # Wait for processing
        time.sleep(0.2)

        # Stop processing
        integration_client.running = False

        # Verify message was processed
        assert len(received_messages) == 1
        assert received_messages[0] == {"content": "integration test"}

    def test_multiple_clients_different_topics(self):
        """Test multiple clients subscribed to different topics."""
        with patch("src.python_trading_pubsub.core.pubsub_client.socketio.Client") as mock_client_class:
            mock_clients = []

            # noinspection PyUnusedLocal
            def create_mock_client(*args, **kwargs):
                mock = MagicMock()
                callbacks = {}
                mock.on.side_effect = lambda e, c: callbacks.update({e: c})
                mock.callbacks = callbacks
                mock_clients.append(mock)
                return mock

            mock_client_class.side_effect = create_mock_client

            # Create multiple clients
            client1 = PubSubClient("http://localhost:5000", "client1", ["topic1"])
            client2 = PubSubClient("http://localhost:5000", "client2", ["topic2"])
            client3 = PubSubClient("http://localhost:5000", "client3", ["topic1", "topic2"])

            received1 = []
            received2 = []
            received3 = []

            client1.register_handler("topic1", lambda m: received1.append(m))
            client2.register_handler("topic2", lambda m: received2.append(m))
            client3.register_handler("topic1", lambda m: received3.append(("topic1", m)))
            client3.register_handler("topic2", lambda m: received3.append(("topic2", m)))

            # Simulate connections
            for mock in mock_clients:
                if "connect" in mock.callbacks:
                    mock.callbacks["connect"]()

            # Simulate messages
            msg1 = {"topic": "topic1", "message_id": "1", "message": "msg1", "producer": "p1"}
            msg2 = {"topic": "topic2", "message_id": "2", "message": "msg2", "producer": "p2"}

            # Send to appropriate clients
            if "message" in mock_clients[0].callbacks:
                mock_clients[0].callbacks["message"](msg1)
            if "message" in mock_clients[1].callbacks:
                mock_clients[1].callbacks["message"](msg2)
            if "message" in mock_clients[2].callbacks:
                mock_clients[2].callbacks["message"](msg1)
                mock_clients[2].callbacks["message"](msg2)

            # Wait for processing
            time.sleep(0.2)

            # Stop all clients
            client1.running = False
            client2.running = False
            client3.running = False

            # Verify messages received
            assert len(received1) == 1
            assert received1[0] == "msg1"

            assert len(received2) == 1
            assert received2[0] == "msg2"

            assert len(received3) == 2
            assert ("topic1", "msg1") in received3
            assert ("topic2", "msg2") in received3

    def test_reconnection_scenario(self, integration_client):
        """Test client behavior during disconnection and reconnection."""
        connection_events = []

        # Track connection events
        def track_connect():
            connection_events.append("connected")
            integration_client.on_connect()

        def track_disconnect():
            connection_events.append("disconnected")
            integration_client.on_disconnect()

        integration_client._test_callbacks["connect"] = track_connect
        integration_client._test_callbacks["disconnect"] = track_disconnect

        # Simulate connection lifecycle
        integration_client._test_callbacks["connect"]()
        assert integration_client.running is True
        assert "connected" in connection_events

        integration_client._test_callbacks["disconnect"]()
        assert integration_client.running is False
        assert "disconnected" in connection_events

        # Simulate reconnection
        integration_client._test_callbacks["connect"]()
        assert integration_client.running is True
        assert connection_events.count("connected") == 2

    def test_message_ordering(self, integration_client):
        """Test that messages are processed in order."""
        processed_order = []

        def ordered_handler(message):
            processed_order.append(message["id"])
            # Simulate some processing time
            time.sleep(0.01)

        integration_client.register_handler("test_topic", ordered_handler)

        # Simulate connection
        if "connect" in integration_client._test_callbacks:
            integration_client._test_callbacks["connect"]()

        # Queue multiple messages
        for i in range(5):
            msg = {"topic": "test_topic", "message_id": f"msg_{i}", "message": {"id": i}, "producer": "test"}
            if "message" in integration_client._test_callbacks:
                integration_client._test_callbacks["message"](msg)

        # Wait for all messages to be processed
        time.sleep(0.3)
        integration_client.running = False

        # Verify order is preserved
        assert processed_order == [0, 1, 2, 3, 4]

    def test_publish_and_consume_flow(self, integration_client):
        """Test publishing and consuming in the same client."""
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_post.return_value = mock_response

            received = []

            def handler(message):
                received.append(message)

            integration_client.register_handler("test_topic", handler)

            # Start client
            if "connect" in integration_client._test_callbacks:
                integration_client._test_callbacks["connect"]()

            # Publish a message
            integration_client.publish(
                topic="test_topic", message={"action": "test"}, producer="integration_test", message_id="pub_123"
            )

            # Simulate receiving the published message back
            if "message" in integration_client._test_callbacks:
                integration_client._test_callbacks["message"](
                    {
                        "topic": "test_topic",
                        "message_id": "pub_123",
                        "message": {"action": "test"},
                        "producer": "integration_test",
                    }
                )

            # Wait for processing
            time.sleep(0.1)
            integration_client.running = False

            # Verify
            assert mock_post.called
            assert len(received) == 1
            assert received[0] == {"action": "test"}

    def test_error_recovery(self, integration_client):
        """Test client recovery from various error conditions."""
        error_count = [0]
        success_count = [0]

        def problematic_handler(message):
            if message.get("error"):
                error_count[0] += 1
                raise Exception("Simulated error")
            else:
                success_count[0] += 1

        integration_client.register_handler("test_topic", problematic_handler)

        # Start client
        if "connect" in integration_client._test_callbacks:
            integration_client._test_callbacks["connect"]()

        # Send mix of good and bad messages
        messages = [{"error": True}, {"error": False}, {"error": True}, {"error": False}, {"error": False}]

        for i, msg_content in enumerate(messages):
            msg = {"topic": "test_topic", "message_id": f"msg_{i}", "message": msg_content, "producer": "test"}
            if "message" in integration_client._test_callbacks:
                integration_client._test_callbacks["message"](msg)

        # Wait for processing
        time.sleep(0.2)
        integration_client.running = False

        # Verify all messages were attempted
        assert error_count[0] == 2
        assert success_count[0] == 3
