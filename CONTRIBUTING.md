# Contributing to Python Trading PubSub

Thank you for your interest in contributing to Python Trading PubSub! We welcome contributions from the community and are grateful for any help you can provide.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and professional in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/venantvr/Python.Trading.PubSub.git
   cd Python.Trading.PubSub
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   make dev-install
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:

- `feature/add-message-compression`
- `fix/connection-timeout-issue`
- `docs/improve-api-reference`
- `refactor/simplify-client-logic`

### 2. Make Your Changes

- Write clean, readable code following PEP 8
- Add type hints to all function signatures
- Include docstrings for all public functions and classes
- Update tests to cover your changes
- Update documentation if needed

### 3. Run Quality Checks

Before committing, run all checks:

```bash
make check
```

This runs:

- Code formatting (black, isort)
- Linting (flake8, pylint)
- Type checking (mypy)
- Tests (pytest)

Individual commands:

```bash
make format      # Auto-format code
make lint        # Run linters
make typecheck   # Run type checking
make test        # Run tests
make coverage    # Run tests with coverage report
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add message compression support

- Implement gzip compression for large messages
- Add compression_enabled parameter to client
- Update tests for compression functionality"
```

Follow conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- Clear title describing the change
- Description of what changed and why
- Reference to any related issues
- Screenshots/examples if applicable

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies

Example test:

```python
def test_message_creation_with_auto_id():
   """Test creating a message with automatic ID generation."""
   # noinspection PyUnresolvedReferences
   msg = PubSubMessage.new(
      topic="test_topic",
      message={"data": "test"},
      producer="test_producer"
   )
   assert msg.topic == "test_topic"
   assert msg.message_id is not None
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

# Run only failed tests
pytest --lf
```

## Code Style Guide

### Python Style

- Follow PEP 8
- Use black for formatting (line length: 120)
- Use isort for import sorting
- Add type hints for function parameters and returns
- Write descriptive variable and function names

### Docstrings

Use Google-style docstrings:

```python
# noinspection PyUnresolvedReferences,PyIncorrectDocstring
def publish(self, topic: str, message: Any, producer: str, message_id: str) -> None:
   """
   Publish a message to a topic.
   
   Args:
       topic: The topic to publish to
       message: The message content
       producer: Name of the producer
       message_id: Unique message identifier
       
   Returns:
       None
       
   Raises:
       ConnectionError: If unable to connect to server
   """
```

## Project Structure

```
python-trading-pubsub/
├── core/               # Core library modules
│   ├── pubsub_client.py
│   └── pubsub_message.py
├── business/           # Business logic modules
├── tests/              # Test suite
├── docs/               # Documentation
├── examples/           # Usage examples
└── .github/            # GitHub configurations
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include usage examples for new features
- Update API reference documentation

## Reporting Issues

### Bug Reports

Include:

- Python version
- Library version
- Operating system
- Minimal code to reproduce
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Include:

- Use case description
- Proposed API/interface
- Example code showing usage
- Alternative solutions considered

## Release Process

1. Update version in `setup.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create release commit: `git commit -m "chore: release v0.2.0"`
4. Tag release: `git tag v0.2.0`
5. Push: `git push origin main --tags`

## Getting Help

- Check existing issues and discussions
- Read the documentation
- Ask in GitHub Discussions
- Contact maintainers

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Python Trading PubSub!