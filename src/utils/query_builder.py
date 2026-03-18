"""
Build MongoDB queries from user-selected filters.

Important note:
- exact-match filters are pushed down to MongoDB
- free-text search is also supported with case-insensitive regex
- date + time range is translated to a timestamp query
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from src.config.constants import (
    ENVIRONMENT_FIELD,
    EVENT_TYPE_FIELD,
    IP_FIELD,
    LEVEL_FIELD,
    MESSAGE_FIELD,
    REQUEST_METHOD_FIELD,
    REQUEST_URL_FIELD,
    STATUS_CODE_FIELD,
    TIMESTAMP_FIELD,
    USER_FIELD,
    ERROR_MESSAGE_FIELD,
    STACK_FIELD,
)
from src.models.config_models import LogFilters


class QueryBuilder:
    @staticmethod
    def build_log_query(filters: LogFilters) -> Dict[str, Any]:
        query: Dict[str, Any] = {}

        if filters.levels:
            query[LEVEL_FIELD] = {"$in": list(filters.levels)}

        if filters.event_types:
            query[EVENT_TYPE_FIELD] = {"$in": list(filters.event_types)}

        if filters.methods:
            query[REQUEST_METHOD_FIELD] = {"$in": list(filters.methods)}

        if filters.environments:
            query[ENVIRONMENT_FIELD] = {"$in": list(filters.environments)}

        if filters.status_codes:
            query[STATUS_CODE_FIELD] = {"$in": list(filters.status_codes)}

        if filters.only_errors:
            query[STATUS_CODE_FIELD] = {"$gte": 400}

        if filters.endpoint_text:
            query[REQUEST_URL_FIELD] = {"$regex": filters.endpoint_text, "$options": "i"}

        if filters.user_text:
            query[USER_FIELD] = {"$regex": filters.user_text, "$options": "i"}

        if filters.ip_text:
            query[IP_FIELD] = {"$regex": filters.ip_text, "$options": "i"}

        # Build datetime range from separate date and time inputs.
        range_query: Dict[str, Any] = {}
        if filters.start_date:
            start_dt = datetime.combine(filters.start_date, filters.start_time or datetime.min.time())
            range_query["$gte"] = start_dt
        if filters.end_date:
            end_dt = datetime.combine(filters.end_date, filters.end_time or datetime.max.time())
            range_query["$lte"] = end_dt
        if range_query:
            query[TIMESTAMP_FIELD] = range_query

        if filters.free_text:
            regex_clause = {"$regex": filters.free_text, "$options": "i"}
            query["$or"] = [
                {MESSAGE_FIELD: regex_clause},
                {ERROR_MESSAGE_FIELD: regex_clause},
                {STACK_FIELD: regex_clause},
                {REQUEST_URL_FIELD: regex_clause},
            ]

        return query
