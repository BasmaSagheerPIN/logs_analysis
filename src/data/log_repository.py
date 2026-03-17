"""
Repository layer.

This is the only layer that talks directly to MongoDB.
Pages should not contain raw Mongo queries.
Services call the repository, then pages call services.

That separation makes the code easier to:
- test
- change
- debug
- extend later
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import DESCENDING

from src.data.mongo_client import MongoConnectionFactory
from src.models.config_models import ConnectionConfig


class LogRepository:
    def __init__(self, connection_config: ConnectionConfig) -> None:
        self.connection_config = connection_config

    @property
    def collection(self):
        return MongoConnectionFactory.get_collection(self.connection_config)

    def find_logs(
        self,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None,
        sort_field: str = "timestamp",
        sort_direction: int = DESCENDING,
    ) -> List[Dict[str, Any]]:
        query = query or {}
        cursor = self.collection.find(query, projection).sort(sort_field, sort_direction)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def count_logs(self, query: Optional[Dict[str, Any]] = None) -> int:
        return self.collection.count_documents(query or {})

    def get_distinct_values(self, field_name: str, query: Optional[Dict[str, Any]] = None) -> List[Any]:
        values = self.collection.distinct(field_name, query or {})
        return sorted([value for value in values if value is not None])

    def get_min_max_timestamp(self) -> Dict[str, Optional[datetime]]:
        first = list(self.collection.find({}, {"timestamp": 1}).sort("timestamp", 1).limit(1))
        last = list(self.collection.find({}, {"timestamp": 1}).sort("timestamp", -1).limit(1))
        return {
            "min_timestamp": first[0].get("timestamp") if first else None,
            "max_timestamp": last[0].get("timestamp") if last else None,
        }
