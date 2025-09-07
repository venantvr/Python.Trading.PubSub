"""Stream redirection utilities."""

from typing import Any


class StreamToLogger:
    """Class to redirect stdout and stderr to a logger."""

    def __init__(self, logger: Any, log_level: int) -> None:
        """Initialize stream redirection."""
        self.logger = logger
        self.log_level = log_level
        self.in_write = False  # Prevent loops

    def write(self, message: str) -> int:
        """Write message to logger."""
        if message and not self.in_write:
            try:
                self.in_write = True  # Prevent recursion in write
                # Only log non-empty messages after stripping
                stripped = message.strip()
                if stripped:
                    self.logger.log(self.log_level, stripped)
            finally:
                self.in_write = False
        return len(message)

    def flush(self) -> None:
        """Flush method for compatibility."""
        pass

    def readable(self) -> bool:
        """Return False as this is write-only."""
        return False

    def writable(self) -> bool:
        """Return True as this is writable."""
        return True

    def seekable(self) -> bool:
        """Return False as this stream is not seekable."""
        return False

    def close(self) -> None:
        """Close the stream (no-op)."""
        pass

    def closed(self) -> bool:
        """Return False as this stream is never closed."""
        return False

    def fileno(self) -> int:
        """Return file descriptor (not supported)."""
        raise OSError("fileno not supported")

    def isatty(self) -> bool:
        """Return False as this is not a terminal."""
        return False
