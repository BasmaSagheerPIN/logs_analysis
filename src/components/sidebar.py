"""
Reusable sidebar components.

This is where connection inputs and Power BI–style filters are rendered.
Keeping these in one place avoids repeating the same UI on every page.
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import streamlit as st

from src.config.settings import (
    get_default_collection_name,
    get_default_db_name,
    get_default_fetch_limit,
    get_default_mongo_uri,
)
from src.models.config_models import ConnectionConfig, LogFilters


def render_connection_settings() -> ConnectionConfig:
    st.sidebar.header("Connection")

    mongo_uri = st.sidebar.text_input(
        "Mongo URI",
        value=get_default_mongo_uri(),
        type="password",
        help="Use a dev, staging, or production MongoDB URI.",
        key="mongo_uri",
    )
    db_name = st.sidebar.text_input("Mongo DB", value=get_default_db_name(), key="db_name")
    collection_name = st.sidebar.text_input("Collection", value=get_default_collection_name(), key="collection_name")
    fetch_limit = st.sidebar.number_input(
        "Rows to load",
        min_value=100,
        max_value=50000,
        value=get_default_fetch_limit(),
        step=100,
        key="fetch_limit",
    )

    if st.sidebar.button("Clear caches"):
        st.cache_data.clear()
        st.cache_resource.clear()

    return ConnectionConfig(
        mongo_uri=mongo_uri,
        db_name=db_name,
        collection_name=collection_name,
        fetch_limit=int(fetch_limit),
    )


def render_log_filters(
    options: dict,
    min_timestamp: pd.Timestamp | None = None,
    max_timestamp: pd.Timestamp | None = None,
) -> LogFilters:
    st.sidebar.header("Filters")

    levels = st.sidebar.multiselect("Level", options.get("levels", []), default=options.get("levels", []))
    event_types = st.sidebar.multiselect("Event type", options.get("event_types", []), default=options.get("event_types", []))
    methods = st.sidebar.multiselect("Method", options.get("methods", []), default=options.get("methods", []))
    environments = st.sidebar.multiselect("Environment", options.get("environments", []), default=options.get("environments", []))
    status_codes = st.sidebar.multiselect("Status code", options.get("status_codes", []), default=[])

    endpoint_text = st.sidebar.text_input("Endpoint contains")
    user_text = st.sidebar.text_input("User ID contains")
    ip_text = st.sidebar.text_input("IP contains")
    free_text = st.sidebar.text_input("Search message / error / SQL / stack")
    only_errors = st.sidebar.checkbox("Only errors", value=False)

    # Date/time defaults: last 7 days when data exists.
    default_start_date = None
    default_end_date = None
    default_start_time = None
    default_end_time = None

    if pd.notna(max_timestamp):
        default_end_date = max_timestamp.date()
        default_end_time = max_timestamp.time().replace(microsecond=0)

        if pd.notna(min_timestamp):
            suggested_start = max(min_timestamp, max_timestamp - timedelta(days=7))
        else:
            suggested_start = max_timestamp - timedelta(days=7)

        default_start_date = suggested_start.date()
        default_start_time = suggested_start.time().replace(microsecond=0)

    start_date = st.sidebar.date_input("Start date", value=default_start_date)
    start_time = st.sidebar.time_input("Start time", value=default_start_time or pd.Timestamp("00:00:00").time())
    end_date = st.sidebar.date_input("End date", value=default_end_date)
    end_time = st.sidebar.time_input("End time", value=default_end_time or pd.Timestamp("23:59:59").time())

    return LogFilters(
        levels=levels,
        event_types=event_types,
        methods=methods,
        environments=environments,
        status_codes=status_codes,
        endpoint_text=endpoint_text,
        user_text=user_text,
        ip_text=ip_text,
        free_text=free_text,
        only_errors=only_errors,
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
    )
