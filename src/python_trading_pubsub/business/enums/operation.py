"""Operation type definitions."""

from enum import Enum


class Operation(Enum):
    """Enumeration of trading operations."""

    BUY = "BUY"
    SELL = "SELL"
