# Changelog

All notable changes to Python Trading PubSub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive test suite with unit and integration tests
- GitHub Actions CI/CD pipeline for automated testing and deployment
- Pre-commit hooks for code quality enforcement
- Modern Python packaging with pyproject.toml
- Professional documentation and README
- Makefile for common development tasks
- Contributing guidelines

### Changed

- Improved error handling and logging
- Enhanced reconnection logic for better reliability

### Security

- Added security scanning with bandit and safety

## [0.1.0] - 2024-01-20

### Features

- Initial release of Python Trading PubSub
- Core PubSubClient for real-time messaging
- PubSubMessage data structure
- Topic-based message routing
- Automatic reconnection support
- Message queue processing
- Custom handler registration
- HTTP/WebSocket hybrid communication
- Thread-safe operations
- Comprehensive logging

### Capabilities

- Connect to Socket.IO server
- Subscribe to multiple topics
- Publish messages via HTTP POST
- Consume messages via WebSocket
- Register custom handlers per topic
- Automatic message acknowledgment
- Sequential message processing

### Dependencies

- Flask 3.0.0
- flask-socketio 5.3.6
- eventlet
- python-socketio[client]
- requests

[Unreleased]:
  https://github.com/venantvr/python-trading-pubsub/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/venantvr/python-trading-pubsub/releases/tag/v0.1.0
