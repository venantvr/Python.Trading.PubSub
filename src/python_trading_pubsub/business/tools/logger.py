"""Logging utilities for the trading application."""

import logging
import os
from logging.handlers import WatchedFileHandler
from typing import Any, Type


def setup_logging(log_level=logging.INFO, name: str = "runtime"):
    """Set up logging configuration."""
    # Main logger configuration
    log = logging.getLogger(name)
    log.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    # Create StreamHandler for console output
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return log


# Function to get the formatter of a specific handler
def get_formatter(runtime_logger, handler_type):
    for handler in runtime_logger.handlers:
        if isinstance(handler, handler_type):
            return handler.formatter  # Return the formatter of the found handler
    return None  # Return None if no handler of the specified type is found


def configure_stream(runtime_logger, log_file: str):
    # Check that log_file is not empty
    if not log_file:
        raise ValueError("Log file path cannot be empty")

    # Create directory tree if it doesn't exist
    log_directory = os.path.dirname(log_file)
    os.makedirs(log_directory, exist_ok=True)

    watched_handler = WatchedFileHandler(log_file)
    watched_handler.setLevel(logging.INFO)
    formatter = get_formatter(runtime, logging.StreamHandler)
    watched_handler.setFormatter(formatter)

    # Remove old file handlers to avoid duplicates
    runtime_logger.handlers = [h for h in runtime_logger.handlers if not isinstance(h, WatchedFileHandler)]

    # Add the new file handler
    runtime_logger.addHandler(watched_handler)


def disable_logger(name: str):
    """
    Class decorator to disable the 'runtime' logger during instantiation.
    """

    def decorator(cls: Type[Any]) -> Type[Any]:
        class Wrapper(cls):
            def __init__(self, *args, **kwargs):
                # Disable the logger before class initialization
                logging.getLogger(name).setLevel(
                    logging.CRITICAL
                )  # Effectively disable the logger by setting it to CRITICAL
                super().__init__(*args, **kwargs)

        return Wrapper

    return decorator


runtime = setup_logging(logging.INFO, "runtime")
detail = setup_logging(logging.INFO, "detail")
