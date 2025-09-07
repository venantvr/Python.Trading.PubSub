"""Database manager for trading positions."""

import json
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4  # Import uuid4 for generating unique message IDs

from business.enums.operation import Operation
from business.tools.logger import runtime
from core.events import EventType
from core.pubsub_client import PubSubClient

# NO MORE DIRECT IMPORTS of Position, Pool, Price, Token for internal logic


# from core.pubsub_message import PubSubMessage # Not needed to import here


# noinspection PyUnusedLocal
class DatabaseManager(threading.Thread, PubSubClient):
    """Manager for trading position database operations."""

    DB_SUBSCRIPTION_TOPICS = [
        EventType.ADD_POSITION_REQUEST.value,
        EventType.SELL_POSITION_REQUEST.value,
        EventType.REQUEST_LAST_PURCHASE_PRICE.value,
        EventType.REQUEST_OPENED_POSITIONS.value,
        EventType.REQUEST_COUNT_OPENED_POSITIONS.value,
        EventType.REQUEST_MAX_SALE_PRICE.value,
        EventType.REQUEST_ALL_POSITIONS_DATA.value,
        EventType.REQUEST_PURCHASE_PRICE_FOR_SELL_UPDATE.value,
        EventType.SELL_PRICE_UPDATE_IN_DB_REQUESTED.value,
        EventType.CANCEL_EVENTS_REQUEST.value,
        EventType.CANCEL_POSITIONS_REQUEST.value,
    ]

    def __init__(self, db_path: str, pubsub_url: str, consumer_name: str = "DatabaseManager"):
        """Initialize database manager."""
        threading.Thread.__init__(self)
        PubSubClient.__init__(self, url=pubsub_url, consumer=consumer_name, topics=self.DB_SUBSCRIPTION_TOPICS)

        self.db_path: str = db_path
        self.name = consumer_name
        self._stop_event = threading.Event()

        self.__initialize_schema()

        runtime.info(f"[{self.name}] Initialized for DB: {db_path}")

        self._register_event_handlers()

    def __initialize_schema(self):
        """Initializes the database schema."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    id TEXT PRIMARY KEY,
                    purchase_price REAL NOT NULL,
                    number_of_tokens REAL NOT NULL,
                    expected_sale_price REAL NOT NULL,
                    next_purchase_price REAL NOT NULL,
                    variations TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    pair TEXT NOT NULL,
                    pool_name TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS position_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (position_id) REFERENCES positions(id)
                )
            """
            )
            cursor.execute(""" CREATE INDEX IF NOT EXISTS idx_positions_timestamp ON positions (timestamp DESC); """)
            cursor.execute(""" CREATE INDEX IF NOT EXISTS idx_positions_status ON positions (status); """)

            cursor.execute("PRAGMA table_info(positions);")
            columns = [col[1] for col in cursor.fetchall()]
            if "use_case" in columns:
                runtime.info(f"[{self.name}] Migrating 'use_case' column to 'pool_name'.")
                cursor.execute("ALTER TABLE positions RENAME COLUMN use_case TO pool_name;")
                cursor.execute("DROP INDEX IF EXISTS idx_positions_use_case;")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_pool_name ON positions (pool_name);")

            conn.commit()
            runtime.info(f"[{self.name}] Database schema initialized/migrated.")
        except sqlite3.OperationalError as e:
            runtime.warning(
                f"[{self.name}] Schema initialization/migration skipped or failed: {e}. "
                f"This might be expected if schema is already up-to-date."
            )
            conn.rollback()
        finally:
            conn.close()

    def _get_db_connection(self) -> sqlite3.Connection:
        """
        Provides a new thread-safe SQLite connection for each call.
        """
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _register_event_handlers(self):
        """
        Registers the handler methods for each subscribed topic.
        """
        self.register_handler(EventType.ADD_POSITION_REQUEST.value, self._handle_add_position_request)
        self.register_handler(EventType.SELL_POSITION_REQUEST.value, self._handle_sell_position_request)
        self.register_handler(EventType.REQUEST_LAST_PURCHASE_PRICE.value, self._handle_request_last_purchase_price)
        self.register_handler(EventType.REQUEST_OPENED_POSITIONS.value, self._handle_request_opened_positions)
        self.register_handler(
            EventType.REQUEST_COUNT_OPENED_POSITIONS.value, self._handle_request_count_opened_positions
        )
        self.register_handler(EventType.REQUEST_MAX_SALE_PRICE.value, self._handle_request_max_sale_price)
        self.register_handler(EventType.REQUEST_ALL_POSITIONS_DATA.value, self._handle_request_all_positions_data)
        self.register_handler(
            EventType.REQUEST_PURCHASE_PRICE_FOR_SELL_UPDATE.value, self._handle_request_purchase_price_for_sell_update
        )
        self.register_handler(EventType.SELL_PRICE_UPDATE_IN_DB_REQUESTED.value, self._handle_update_sell_price_request)
        self.register_handler(EventType.CANCEL_EVENTS_REQUEST.value, self._handle_cancel_events_request)
        self.register_handler(EventType.CANCEL_POSITIONS_REQUEST.value, self._handle_cancel_positions_request)

        runtime.info(f"[{self.name}] Event handlers registered.")

    def run(self):
        """
        The main loop for the DatabaseManager thread.
        This method will start the PubSubClient's connection and message processing.
        """
        runtime.info(f"[{self.name}] Thread starting PubSubClient connection.")
        self.start()  # Call the start method inherited from PubSubClient
        runtime.info(f"[{self.name}] Thread stopped PubSubClient connection.")

    def stop(self):
        """Signals the DatabaseManager thread to stop by disconnecting the Socket.IO client."""
        runtime.info(f"[{self.name}] Disconnecting PubSubClient to stop thread.")
        self.sio.disconnect()
        self._stop_event.set()

    # --- Event Handlers (working purely with primitive types/dicts) ---

    def _handle_add_position_request(self, position_data_dict: Dict[str, Any]):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            timestamp_now = datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO positions (id, purchase_price, number_of_tokens, expected_sale_price,
                                     next_purchase_price, variations, timestamp, status, pair, pool_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    position_data_dict["id"],
                    position_data_dict["purchase_price"],
                    position_data_dict["number_of_tokens"],
                    position_data_dict["expected_sale_price"],
                    position_data_dict["next_purchase_price"],
                    position_data_dict["variations"],  # Already a JSON string from PositionMapper
                    position_data_dict["timestamp"],
                    "open",
                    position_data_dict["pair"],
                    position_data_dict["pool_name"],
                ),
            )
            cursor.execute(
                """
                INSERT INTO position_events (position_id, event_type, timestamp)
                VALUES (?, ?, ?)
            """,
                (position_data_dict["id"], Operation.BUY.value, timestamp_now),
            )
            conn.commit()
            # Pass message_id as an auto-generated UUID
            self.publish(
                EventType.POSITION_OPENED.value, json.dumps(position_data_dict), self.consumer, message_id=str(uuid4())
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error adding position: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _handle_sell_position_request(self, position_id: str):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            timestamp_now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE positions SET status = 'closed' WHERE id = ?
            """,
                (position_id,),
            )
            cursor.execute(
                """
                INSERT INTO position_events (position_id, event_type, timestamp)
                VALUES (?, ?, ?)
            """,
                (position_id, Operation.SELL.value, timestamp_now),
            )
            conn.commit()
            self.publish(EventType.POSITION_SOLD.value, json.dumps(position_id), self.consumer, message_id=str(uuid4()))
        except Exception as e:
            runtime.exception(f"[{self.name}] Error selling position {position_id}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _handle_cancel_events_request(self, db_path: str):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO position_events (position_id, event_type, timestamp)
                SELECT position_id, ? AS event_type, CURRENT_TIMESTAMP AS timestamp
                FROM position_events
                WHERE event_type = ?;
            """,
                (Operation.SELL.value, Operation.BUY.value),
            )
            conn.commit()
            self.publish(EventType.EVENTS_CANCELLED.value, json.dumps(True), self.consumer, message_id=str(uuid4()))
        except Exception as e:
            runtime.exception(f"[{self.name}] Error cancelling events: {e}")
            conn.rollback()
            self.publish(EventType.EVENTS_CANCELLED.value, json.dumps(False), self.consumer, message_id=str(uuid4()))
        finally:
            conn.close()

    def _handle_cancel_positions_request(self, db_path: str):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE positions
                SET status = 'closed'
                WHERE status = 'open';
            """
            )
            conn.commit()
            self.publish(EventType.POSITIONS_CLOSED.value, json.dumps(True), self.consumer, message_id=str(uuid4()))
        except Exception as e:
            runtime.exception(f"[{self.name}] Error cancelling positions: {e}")
            conn.rollback()
            self.publish(EventType.POSITIONS_CLOSED.value, json.dumps(False), self.consumer, message_id=str(uuid4()))
        finally:
            conn.close()

    def _handle_request_last_purchase_price(self, pools_names: Optional[List[str]] = None):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            if pools_names:
                placeholders = ", ".join("?" for _ in pools_names)
                # nosec B608 - Safe parameterized query with validated placeholders
                query = f"""
                    SELECT purchase_price
                    FROM positions
                    WHERE status = 'open' AND pool_name IN ({placeholders})
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                cursor.execute(query, pools_names)
            else:
                query = """
                    SELECT purchase_price
                    FROM positions
                    WHERE status = 'open'
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                cursor.execute(query)
            row = cursor.fetchone()
            output_price_float = row[0] if row else 0.0
            self.publish(
                EventType.LAST_PURCHASE_PRICE_RETRIEVED.value,
                json.dumps(output_price_float),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error retrieving last purchase price: {e}")
            self.publish(
                EventType.LAST_PURCHASE_PRICE_RETRIEVED.value, json.dumps(0.0), self.consumer, message_id=str(uuid4())
            )
        finally:
            conn.close()

    def _handle_request_opened_positions(self, pools_names: Optional[List[str]] = None):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            if pools_names:
                placeholders = ", ".join("?" for _ in pools_names)
                # nosec B608 - Safe parameterized query with validated placeholders
                query = f"""
                    SELECT id, purchase_price, number_of_tokens, expected_sale_price, next_purchase_price,
                           variations, timestamp, pair, pool_name, status
                    FROM positions
                    WHERE status = 'open' AND pool_name IN ({placeholders})
                    ORDER BY timestamp ASC
                """
                cursor.execute(query, pools_names)
            else:
                query = """
                    SELECT id, purchase_price, number_of_tokens, expected_sale_price, next_purchase_price,
                           variations, timestamp, pair, pool_name, status
                    FROM positions
                    WHERE status = 'open'
                    ORDER BY timestamp ASC
                """
                cursor.execute(query)
            rows = cursor.fetchall()
            headers = [description[0] for description in cursor.description]

            raw_position_dicts = []
            for row_data in rows:
                raw_position_dicts.append(dict(zip(headers, row_data)))

            self.publish(
                EventType.OPENED_POSITIONS_RETRIEVED.value,
                json.dumps(raw_position_dicts),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error retrieving opened positions: {e}")
            self.publish(
                EventType.OPENED_POSITIONS_RETRIEVED.value, json.dumps([]), self.consumer, message_id=str(uuid4())
            )
        finally:
            conn.close()

    def _handle_request_count_opened_positions(self, pools_names: Optional[List[str]] = None):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            if pools_names:
                placeholders = ", ".join("?" for _ in pools_names)
                # nosec B608 - Safe parameterized query with validated placeholders
                query = f"""
                    SELECT COUNT(*)
                    FROM positions
                    WHERE status = 'open' AND pool_name IN ({placeholders})
                """
                cursor.execute(query, pools_names)
            else:
                query = """
                    SELECT COUNT(*)
                    FROM positions
                    WHERE status = 'open'
                """
                cursor.execute(query)
            count = cursor.fetchone()[0]
            self.publish(
                EventType.OPENED_POSITIONS_COUNT_RETRIEVED.value,
                json.dumps(count),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error counting opened positions: {e}")
            self.publish(
                EventType.OPENED_POSITIONS_COUNT_RETRIEVED.value, json.dumps(0), self.consumer, message_id=str(uuid4())
            )
        finally:
            conn.close()

    def _handle_request_max_sale_price(self, pools_names: Optional[List[str]] = None):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            if pools_names:
                placeholders = ", ".join("?" for _ in pools_names)
                # nosec B608 - Safe parameterized query with validated placeholders
                query = f"""
                    SELECT MAX(expected_sale_price)
                    FROM positions
                    WHERE status = 'open' AND pool_name IN ({placeholders})
                """
                cursor.execute(query, pools_names)
            else:
                query = """
                    SELECT MAX(expected_sale_price)
                    FROM positions
                    WHERE status = 'open'
                """
                cursor.execute(query)
            result = cursor.fetchone()
            max_sale_price_float = result[0] if result and result[0] is not None else 0.0
            self.publish(
                EventType.MAX_SALE_PRICE_RETRIEVED.value,
                json.dumps(max_sale_price_float),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error retrieving max sale price: {e}")
            self.publish(
                EventType.MAX_SALE_PRICE_RETRIEVED.value, json.dumps(0.0), self.consumer, message_id=str(uuid4())
            )
        finally:
            conn.close()

    def _handle_request_all_positions_data(self, message_payload: Any):
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT id, number_of_tokens, expected_sale_price, next_purchase_price,
                       purchase_price, timestamp, status, pool_name, variations
                FROM positions
                ORDER BY timestamp ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            headers = [description[0] for description in cursor.description]
            raw_position_dicts = []
            for row_data in rows:
                raw_position_dicts.append(dict(zip(headers, row_data)))
            self.publish(
                EventType.ALL_POSITIONS_RETRIEVED.value,
                json.dumps(raw_position_dicts),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error retrieving all positions data: {e}")
            self.publish(
                EventType.ALL_POSITIONS_RETRIEVED.value, json.dumps([]), self.consumer, message_id=str(uuid4())
            )
        finally:
            conn.close()

    def _handle_request_purchase_price_for_sell_update(
        self, message_payload: Dict[str, Any]
    ):  # Accepts message_payload
        """
        Handles the request to retrieve purchase price for sell update.
        message_payload is expected to be a dict containing 'position_id' and 'percentage_change'.
        """
        # Parse the message_payload (which is currently a JSON string, so load it)
        # Note: Your PubSubClient.on_message passes `message` as already processed (data["message"])
        # If data["message"] is still a JSON string, you'll need to json.loads it here.
        # Based on previous payloads, it should be the raw dict/value, not the JSON string itself.
        # Let's assume PubSubClient handles json.loads for incoming messages.

        # If your PubSubClient.on_message passes the 'message' key as the raw (unparsed) JSON string:
        # payload = json.loads(message_payload) if isinstance(message_payload, str) else message_payload
        # Else, if it passes the already parsed Python object:
        payload = message_payload

        position_id = payload.get("position_id")
        percentage_change = payload.get("percentage_change")

        if position_id is None or percentage_change is None:
            runtime.warning(
                f"[{self.name}] Received malformed REQUEST_PURCHASE_PRICE_FOR_SELL_UPDATE payload: {payload}"
            )
            return  # Or publish an error event

        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT purchase_price FROM positions WHERE id = ?
            """,
                (position_id,),
            )
            row = cursor.fetchone()

            if not row:
                self.publish(
                    EventType.POSITION_NOT_FOUND_FOR_SELL_UPDATE.value,
                    json.dumps(position_id),
                    self.consumer,
                    message_id=str(uuid4()),
                )
                return

            current_purchase_price = row[0]
            new_sell_price = current_purchase_price * (1 + (percentage_change / 100))
            self.publish(
                EventType.SELL_PRICE_UPDATE_IN_DB_REQUESTED.value,
                json.dumps({"position_id": position_id, "new_sell_price": new_sell_price}),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error requesting purchase price for sell update: {e}")
        finally:
            conn.close()

    def _handle_update_sell_price_request(self, message_payload: Dict[str, Any]):  # Accepts message_payload
        """
        Handles the request to update the sell price of a position.
        message_payload is expected to be a dict containing 'position_id' and 'new_sell_price'.
        """
        # Parse the message_payload if necessary (see comment above)
        # payload = json.loads(message_payload) if isinstance(message_payload, str) else message_payload
        payload = message_payload

        position_id = payload.get("position_id")
        new_sell_price = payload.get("new_sell_price")

        if position_id is None or new_sell_price is None:
            runtime.warning(f"[{self.name}] Received malformed SELL_PRICE_UPDATE_IN_DB_REQUESTED payload: {payload}")
            return  # Or publish an error event

        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE positions
                SET expected_sale_price = ?
                WHERE id = ?
            """,
                (new_sell_price, position_id),
            )
            conn.commit()
            self.publish(
                EventType.SELL_PRICE_UPDATED.value,
                json.dumps({"position_id": position_id, "new_sell_price": new_sell_price}),
                self.consumer,
                message_id=str(uuid4()),
            )
        except Exception as e:
            runtime.exception(f"[{self.name}] Error updating sell price for position {position_id}: {e}")
            conn.rollback()
        finally:
            conn.close()
