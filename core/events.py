"""Event type definitions for the trading system."""

from enum import Enum


class EventType(Enum):
    """Enumeration of event types used in the trading system."""

    # Command Events (generally published by Orchestrator or services)
    COMMAND_ACTIONS_REGISTERED = "command_actions_registered"

    # Database Events (published by DatabaseManager)
    ADD_POSITION_REQUEST = "add_position_request"  # Received by DatabaseManager
    SELL_POSITION_REQUEST = "sell_position_request"  # Received by DatabaseManager
    REQUEST_LAST_PURCHASE_PRICE = "request_last_purchase_price"  # Received by DatabaseManager
    REQUEST_OPENED_POSITIONS = "request_opened_positions"  # Received by DatabaseManager
    REQUEST_COUNT_OPENED_POSITIONS = "request_count_opened_positions"  # Received by DatabaseManager
    REQUEST_MAX_SALE_PRICE = "request_max_sale_price"  # Received by DatabaseManager
    REQUEST_ALL_POSITIONS_DATA = "request_all_positions_data"  # Received by DatabaseManager
    REQUEST_PURCHASE_PRICE_FOR_SELL_UPDATE = "request_purchase_price_for_sell_update"  # Received by DatabaseManager
    SELL_PRICE_UPDATE_IN_DB_REQUESTED = "sell_price_update_in_db_requested"  # Received by DatabaseManager (renamed)
    CANCEL_EVENTS_REQUEST = "cancel_events_request"  # Received by DatabaseManager
    CANCEL_POSITIONS_REQUEST = "cancel_positions_request"  # Received by DatabaseManager

    # Database Response Events (published by DatabaseManager)
    POSITION_OPENED = "position_opened"
    POSITION_SOLD = "position_sold"
    EVENTS_CANCELLED = "events_cancelled"
    POSITIONS_CLOSED = "positions_closed"  # Renamed
    LAST_PURCHASE_PRICE_RETRIEVED = "last_purchase_price_retrieved"
    OPENED_POSITIONS_RETRIEVED = "opened_positions_retrieved"
    OPENED_POSITIONS_COUNT_RETRIEVED = "opened_positions_count_retrieved"  # Renamed
    MAX_SALE_PRICE_RETRIEVED = "max_sale_price_retrieved"
    ALL_POSITIONS_RETRIEVED = "all_positions_retrieved"  # Renamed
    POSITION_NOT_FOUND_FOR_SELL_UPDATE = "position_not_found_for_sell_update"
    SELL_PRICE_UPDATED = "sell_price_updated"

    # Note: Other EventTypes (related to exchange, trading bot, indicators, Telegram, etc.)
    # are not included here as they are not directly used/published by DatabaseManager.
