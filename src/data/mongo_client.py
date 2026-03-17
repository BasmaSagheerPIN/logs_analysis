"""
MongoDB connection factory.

Important design choices:
- we cache the client so Streamlit reruns do not reconnect every time
- the cache key changes when URI changes, so the user can switch environments from the sidebar
- a ping method is provided so we can show connection health in the UI
"""
from __future__ import annotations

from typing import Tuple

import streamlit as st
from pymongo import MongoClient
from pymongo.collection import Collection

from src.models.config_models import ConnectionConfig


class MongoConnectionFactory:
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def get_client(mongo_uri: str) -> MongoClient:
        return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    @classmethod
    def get_collection(cls, config: ConnectionConfig) -> Collection:
        client = cls.get_client(config.mongo_uri)
        return client[config.db_name][config.collection_name]

    @classmethod
    def ping(cls, config: ConnectionConfig) -> Tuple[bool, str]:
        try:
            client = cls.get_client(config.mongo_uri)
            client.admin.command("ping")
            return True, "Connected"
        except Exception as exc:
            return False, str(exc)
