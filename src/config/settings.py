"""
App settings loader.

Order of precedence:
1. Streamlit session_state (what the user typed in sidebar)
2. Streamlit secrets (good for local or cloud deployment)
3. Environment variables
4. Safe defaults

This design keeps the app easy to debug while still being deployable later.
"""
from __future__ import annotations

import os
from typing import Any

import streamlit as st

DEFAULT_FETCH_LIMIT = 5000
DEFAULT_MONGO_DB = "logbook"
DEFAULT_LOG_COLLECTION = "backend-logs"


def _read_secret(key: str, default: Any = None) -> Any:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def get_default_mongo_uri() -> str:
    return (
        st.session_state.get("mongo_uri")
        or _read_secret("MONGO_URI")
        or os.getenv("MONGO_URI", "mongodb://localhost:27017")
    )


def get_default_db_name() -> str:
    return (
        st.session_state.get("db_name")
        or _read_secret("MONGO_DB")
        or os.getenv("MONGO_DB", DEFAULT_MONGO_DB)
    )


def get_default_collection_name() -> str:
    return (
        st.session_state.get("collection_name")
        or _read_secret("MONGO_COLLECTION")
        or os.getenv("MONGO_COLLECTION", DEFAULT_LOG_COLLECTION)
    )


def get_default_fetch_limit() -> int:
    value = (
        st.session_state.get("fetch_limit")
        or _read_secret("DEFAULT_FETCH_LIMIT")
        or os.getenv("DEFAULT_FETCH_LIMIT", DEFAULT_FETCH_LIMIT)
    )
    try:
        return int(value)
    except Exception:
        return DEFAULT_FETCH_LIMIT
