"""Tests for PubSubMessage class."""

from uuid import UUID

from core.pubsub_message import PubSubMessage


class TestPubSubMessage:
    """Test suite for PubSubMessage."""

    def test_create_message_with_auto_id(self):
        """Test creating a message with automatic ID generation."""
        msg = PubSubMessage.new(
            topic="test_topic",
            message={"data": "test"},
            producer="test_producer"
        )

        assert msg.topic == "test_topic"
        assert msg.message == {"data": "test"}
        assert msg.producer == "test_producer"
        assert msg.message_id is not None
        # Verify it's a valid UUID
        UUID(msg.message_id)

    def test_create_message_with_custom_id(self):
        """Test creating a message with a custom ID."""
        custom_id = "custom_123"
        msg = PubSubMessage.new(
            topic="test_topic",
            message="test message",
            producer="test_producer",
            message_id=custom_id
        )

        assert msg.message_id == custom_id

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = PubSubMessage.new(
            topic="test_topic",
            message={"key": "value"},
            producer="test_producer",
            message_id="test_id"
        )

        result = msg.to_dict()

        assert isinstance(result, dict)
        assert result["topic"] == "test_topic"
        assert result["message"] == {"key": "value"}
        assert result["producer"] == "test_producer"
        assert result["message_id"] == "test_id"

    def test_message_with_different_data_types(self):
        """Test message with various data types."""
        test_cases = [
            ("string message", str),
            (123, int),
            (45.67, float),
            (["list", "of", "items"], list),
            ({"nested": {"dict": "value"}}, dict),
            (True, bool),
            (None, type(None))
        ]

        for message_content, expected_type in test_cases:
            msg = PubSubMessage.new(
                topic="test",
                message=message_content,
                producer="test"
            )
            assert isinstance(msg.message, expected_type)
            assert msg.to_dict()["message"] == message_content

    def test_message_immutability_concept(self):
        """Test that message fields are accessible but follow dataclass patterns."""
        msg = PubSubMessage.new(
            topic="original_topic",
            message="original_message",
            producer="original_producer"
        )

        # Dataclass fields are accessible
        assert msg.topic == "original_topic"
        assert msg.message == "original_message"
        assert msg.producer == "original_producer"

    def test_message_equality(self):
        """Test message equality based on all fields."""
        msg1 = PubSubMessage(
            topic="test",
            message_id="same_id",
            message="same_message",
            producer="same_producer"
        )

        msg2 = PubSubMessage(
            topic="test",
            message_id="same_id",
            message="same_message",
            producer="same_producer"
        )

        msg3 = PubSubMessage(
            topic="test",
            message_id="different_id",
            message="same_message",
            producer="same_producer"
        )

        assert msg1 == msg2
        assert msg1 != msg3

    def test_message_repr(self):
        """Test string representation of message."""
        msg = PubSubMessage.new(
            topic="test_topic",
            message="test",
            producer="test_producer",
            message_id="test_123"
        )

        repr_str = repr(msg)
        assert "PubSubMessage" in repr_str
        assert "test_topic" in repr_str
        assert "test_123" in repr_str
        assert "test_producer" in repr_str
