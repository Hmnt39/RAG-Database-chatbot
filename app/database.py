"""MongoDB client"""

from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client for managing conversations and documents."""

    def __init__(self, uri: str, db_name: str):
        """
        Initialize MongoDB client.

        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self) -> bool:
        """
        Establish connection to MongoDB.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            logger.info(f"Successfully connected to MongoDB: {self.db_name}")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

