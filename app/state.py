"""Shared application state - settings and database client."""

from app.config import Settings
from app.database import MongoDBClient

# Initialize shared settings and database client
settings = Settings()
db_client = MongoDBClient(uri=settings.mongodb_uri, db_name=settings.mongodb_db_name)

__all__ = ["settings", "db_client"]
