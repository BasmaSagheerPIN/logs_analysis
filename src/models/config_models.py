"""
Data models for connection settings and filters.

We use dataclasses because they are lightweight, readable, and easy to extend.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Sequence


@dataclass
class ConnectionConfig:
    mongo_uri: str
    db_name: str
    collection_name: str
    fetch_limit: int = 5000


@dataclass
class LogFilters:
    levels: Sequence[str]
    event_types: Sequence[str]
    methods: Sequence[str]
    environments: Sequence[str]
    status_codes: Sequence[int]

    endpoint_text: str = ""
    user_text: str = ""
    ip_text: str = ""
    free_text: str = ""
    only_errors: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
