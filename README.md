# Python Trading PubSub

A professional Python library for building publish-subscribe messaging systems tailored for trading applications. This library provides a robust, asynchronous messaging
infrastructure using Socket.IO for real-time communication between trading components.

## Features

- **Real-time Communication**: Built on Socket.IO for low-latency message delivery
- **Topic-based Routing**: Subscribe to specific topics for targeted message consumption
- **Automatic Reconnection**: Resilient client with automatic reconnection capabilities
- **Message Queue Processing**: Sequential message processing with built-in queue management
- **Custom Handler Registration**: Register custom handlers for different topics
- **HTTP/WebSocket Hybrid**: Publish via HTTP POST, consume via WebSocket
- **Thread-safe Operations**: Built-in threading support for concurrent operations
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Installation

### From Source

```bash
git clone https://github.com/yourusername/python-trading-pubsub.git
cd python-trading-pubsub
pip install -e .
```

### Using pip

```bash
pip install python-trading-pubsub
```

## Quick Start

### Basic Usage

```python
from core.pubsub_client import PubSubClient

# Initialize client
client = PubSubClient(
    url="http://localhost:5000",
    consumer="trader_1",
    topics=["market_data", "signals"]
)

# Register message handlers
def handle_market_data(message):
    print(f"Received market data: {message}")

def handle_signals(message):
    print(f"Received trading signal: {message}")

client.register_handler("market_data", handle_market_data)
client.register_handler("signals", handle_signals)

# Start the client
client.start()
```

### Publishing Messages

```python
# Publish a message
# noinspection PyUnresolvedReferences
client.publish(
    topic="market_data",
    message={"symbol": "BTC/USD", "price": 50000, "volume": 1000},
    producer="market_feed",
    message_id="msg_123"
)
```

### Creating Custom Messages

```python
from core.pubsub_message import PubSubMessage

# Create a message
msg = PubSubMessage.new(
    topic="signals",
    message={"action": "BUY", "symbol": "ETH/USD", "quantity": 10},
    producer="signal_generator"
)

# Convert to dictionary for transmission
msg_dict = msg.to_dict()
```

## Architecture

### Components

- **PubSubClient**: Main client class for connecting to the PubSub server
- **PubSubMessage**: Message data structure with metadata
- **Message Queue**: Internal queue for sequential message processing
- **Handler Registry**: Topic-to-function mapping for message routing

### Message Flow

1. **Publishing**: Messages are sent via HTTP POST to the server
2. **Distribution**: Server broadcasts messages to subscribed clients
3. **Reception**: Clients receive messages via WebSocket connection
4. **Queuing**: Messages are queued for sequential processing
5. **Processing**: Registered handlers process messages by topic
6. **Acknowledgment**: Consumption confirmation sent back to server

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/python-trading-pubsub.git
cd python-trading-pubsub

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/test_pubsub_client.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make typecheck

# Run all checks
make check
```

## API Reference

### PubSubClient

#### Constructor

```code
# noinspection PyUnresolvedReferences
PubSubClient(url: str, consumer: str, topics: List[str])
```

- `url`: Socket.IO server URL
- `consumer`: Unique consumer identifier
- `topics`: List of topics to subscribe to

#### Methods

- `register_handler(topic: str, handler_func: Callable)`: Register a message handler
- `publish(topic: str, message: Any, producer: str, message_id: str)`: Publish a message
- `start()`: Start the client and connect to server

### PubSubMessage

#### Static Methods

```code
# noinspection PyUnresolvedReferences
PubSubMessage.new(topic: str, message: Any, producer: str, message_id: str = None)
```

Creates a new message instance with automatic UUID generation if message_id is not provided.

#### Instance Methods

- `to_dict()`: Convert message to dictionary representation

## Configuration

### Logging

Configure logging level in your application:

```python
import logging

# Set to DEBUG for detailed output
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('core.pubsub_client')
logger.setLevel(logging.WARNING)
```

### Connection Settings

Customize connection parameters:

```python
# noinspection PyUnresolvedReferences
client = PubSubClient(url, consumer, topics)

# Access underlying Socket.IO client for advanced configuration
client.sio.reconnection_delay = 5000  # 5 seconds
client.sio.reconnection_delay_max = 30000  # 30 seconds
```

## Examples

### Trading Signal Distribution

```python
# Signal generator
# noinspection PyUnresolvedReferences
generator = PubSubClient("http://localhost:5000", "signal_gen", [])

# Generate and publish signals
signal = {
    "timestamp": "2024-01-20T10:30:00Z",
    "symbol": "AAPL",
    "action": "BUY",
    "price": 185.50,
    "stop_loss": 183.00,
    "take_profit": 190.00
}

generator.publish("trading_signals", signal, "signal_gen", None)
```

### Market Data Aggregation

```python
# Market data aggregator
# noinspection PyUnresolvedReferences
aggregator = PubSubClient("http://localhost:5000", "aggregator", ["raw_prices"])

prices = {}

def aggregate_prices(message):
    symbol = message.get("symbol")
    price = message.get("price")
    prices[symbol] = price
    
    # Publish aggregated data every 10 updates
    if len(prices) >= 10:
        aggregator.publish("aggregated_prices", prices.copy(), "aggregator", None)
        prices.clear()

aggregator.register_handler("raw_prices", aggregate_prices)
aggregator.start()
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for all public methods
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/python-trading-pubsub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/python-trading-pubsub/discussions)
- **Documentation**: [Full Documentation](https://python-trading-pubsub.readthedocs.io)

## Acknowledgments

- Built with [python-socketio](https://python-socketio.readthedocs.io/)
- Inspired by enterprise messaging patterns
- Designed for high-frequency trading applications

## Roadmap

- [ ] Add message persistence layer
- [ ] Implement message encryption
- [ ] Add metrics and monitoring
- [ ] Support for message replay
- [ ] Clustering support for horizontal scaling
- [ ] Dead letter queue implementation
- [ ] Message compression options
- [ ] GraphQL subscription support

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed version history.

---

**Note**: This library requires a compatible PubSub server running.