"""PubSub client for real-time messaging."""

import logging
import queue
import threading
from typing import Any, Callable, Dict, List

import requests
import socketio

from src.python_trading_pubsub.core.pubsub_message import PubSubMessage

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PubSubClient:
    """Client for publish-subscribe messaging system."""

    def __init__(self, url: str, consumer: str, topics: List[str]):
        """
        Initialize the PubSub client.

        :param url: URL of the Socket.IO server, e.g., http://localhost:5000
        :param consumer: Consumer name (e.g., 'alice')
        :param topics: List of topics to subscribe to
        """
        self.url = url.rstrip("/")
        self.consumer = consumer
        self.topics = topics
        self.handlers: Dict[str, Callable[[Any], None]] = {}  # topic → function
        self.message_queue: queue.Queue[Dict[str, Any]] = queue.Queue()  # Queue for processing messages sequentially
        self.running = False

        # Create Socket.IO client with explicit reconnection settings
        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=0,  # Infinite reconnection attempts
            reconnection_delay=2000,  # Delay between reconnection attempts (ms)
            reconnection_delay_max=10000,  # Max delay for reconnection
        )

        # Register generic events
        self.sio.on("connect", self.on_connect)
        self.sio.on("message", self.on_message)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("new_message", self.on_new_message)

    def register_handler(self, topic: str, handler_func: Callable[[Any], None]) -> None:
        """
        Register a custom handler for a given topic.

        :param topic: Topic to handle
        :param handler_func: Function to call when a message is received
        """
        self.handlers[topic] = handler_func

    def on_connect(self) -> None:
        """Handle connection to the server."""
        logger.info(f"[{self.consumer}] Connected to server {self.url}")
        self.sio.emit("subscribe", {"consumer": self.consumer, "topics": self.topics})
        if not self.running:
            self.running = True
            threading.Thread(target=self.process_queue, daemon=True).start()

    def on_message(self, data: Dict[str, Any]) -> None:
        """
        Handle incoming messages by adding them to the queue.

        :param data: Message data containing topic, message_id, message, and producer
        """
        logger.info(f"[{self.consumer}] Queuing message: {data}")
        self.message_queue.put(data)

    def process_queue(self) -> None:
        """Process messages from the queue one by one."""
        while self.running:
            try:
                data = self.message_queue.get(timeout=1.0)
                topic = data["topic"]
                message_id = data.get("message_id")
                message = data["message"]
                producer = data.get("producer")

                logger.info(
                    f"[{self.consumer}] Processing message from topic [{topic}]: {message} "
                    f"(from {producer}, ID={message_id})"
                )

                if topic in self.handlers:
                    try:
                        self.handlers[topic](message)
                    except Exception as e:
                        logger.error(f"[{self.consumer}] Error in handler for topic {topic}: {e}")
                else:
                    logger.warning(f"[{self.consumer}] No handler for topic {topic}.")

                # Notify consumption
                self.sio.emit(
                    "consumed",
                    {"consumer": self.consumer, "topic": topic, "message_id": message_id, "message": message},
                )

                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"[{self.consumer}] Error processing message: {e}")

    def on_disconnect(self) -> None:
        """Handle disconnection from the server."""
        logger.info(f"[{self.consumer}] Disconnected from server. Reconnection will be attempted automatically.")
        self.running = False  # Stop queue processing until reconnected

    def on_new_message(self, data: Dict[str, Any]) -> None:
        """Handle new message events."""
        logger.info(f"[{self.consumer}] New message: {data}")

    def publish(self, topic: str, message: Any, producer: str, message_id: str) -> None:
        """
        Publish a message via HTTP POST to the pubsub backend.

        :param topic: Topic to publish to
        :param message: Message content
        :param producer: Name of the producer
        :param message_id: Unique message ID
        """
        msg = PubSubMessage.new(topic, message, producer, message_id)
        url = f"{self.url}/publish"
        logger.info(f"[{self.consumer}] Publishing to {topic}: {msg.to_dict()}")
        try:
            resp = requests.post(url, json=msg.to_dict(), timeout=30)
            resp.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            logger.info(f"[{self.consumer}] Publish response: {resp.json()}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[{self.consumer}] Connection error during publish: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"[{self.consumer}] HTTP error during publish: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"[{self.consumer}] An unexpected error occurred during publish: {e}")

    def start(self) -> None:
        """Start the client and connect to the server."""
        logger.info(f"Starting client {self.consumer} with topics {self.topics}")
        self.sio.connect(self.url)
        self.sio.wait()
