"""Event type definitions for the trading system."""

from enum import Enum


class EventType(Enum):
    """Enumeration of event types used in the trading system."""

    # Événements de Commandes (généralement publiés par l'Orchestrator ou des services)
    COMMAND_ACTIONS_REGISTERED = "command_actions_registered"

    # Événements de la Base de Données (publiés par DatabaseManager)
    ADD_POSITION_REQUEST = "add_position_request"  # Reçu par DatabaseManager
    SELL_POSITION_REQUEST = "sell_position_request"  # Reçu par DatabaseManager
    REQUEST_LAST_PURCHASE_PRICE = "request_last_purchase_price"  # Reçu par DatabaseManager
    REQUEST_OPENED_POSITIONS = "request_opened_positions"  # Reçu par DatabaseManager
    REQUEST_COUNT_OPENED_POSITIONS = "request_count_opened_positions"  # Reçu par DatabaseManager
    REQUEST_MAX_SALE_PRICE = "request_max_sale_price"  # Reçu par DatabaseManager
    REQUEST_ALL_POSITIONS_DATA = "request_all_positions_data"  # Reçu par DatabaseManager
    REQUEST_PURCHASE_PRICE_FOR_SELL_UPDATE = "request_purchase_price_for_sell_update"  # Reçu par DatabaseManager
    SELL_PRICE_UPDATE_IN_DB_REQUESTED = "sell_price_update_in_db_requested"  # Reçu par DatabaseManager (renommé)
    CANCEL_EVENTS_REQUEST = "cancel_events_request"  # Reçu par DatabaseManager
    CANCEL_POSITIONS_REQUEST = "cancel_positions_request"  # Reçu par DatabaseManager

    # Événements de Réponse de la Base de Données (publiés par DatabaseManager)
    POSITION_OPENED = "position_opened"
    POSITION_SOLD = "position_sold"
    EVENTS_CANCELLED = "events_cancelled"
    POSITIONS_CLOSED = "positions_closed"  # Renommé
    LAST_PURCHASE_PRICE_RETRIEVED = "last_purchase_price_retrieved"
    OPENED_POSITIONS_RETRIEVED = "opened_positions_retrieved"
    OPENED_POSITIONS_COUNT_RETRIEVED = "opened_positions_count_retrieved"  # Renommé
    MAX_SALE_PRICE_RETRIEVED = "max_sale_price_retrieved"
    ALL_POSITIONS_RETRIEVED = "all_positions_retrieved"  # Renommé
    POSITION_NOT_FOUND_FOR_SELL_UPDATE = "position_not_found_for_sell_update"
    SELL_PRICE_UPDATED = "sell_price_updated"

    # Note : Les autres EventType (liés à l'échange, au bot de trading, aux indicateurs, à Telegram, etc.)
    # ne sont pas inclus ici car ils ne sont pas directement utilisés/publiés par DatabaseManager.
