from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager
from src.components.sidebar import render_connection_settings, render_log_filters
from src.components.tables import show_dataframe_with_export
from src.data.mongo_client import MongoConnectionFactory
from src.services.log_service import LogService

st.title("Raw Log Explorer")
st.caption("Power BI–style table view with flexible filters and CSV export.")

AuthManager().render_placeholder_banner()
connection = render_connection_settings()

ok, message = MongoConnectionFactory.ping(connection)
if ok:
    st.sidebar.success(message)
else:
    st.sidebar.error(message)
    st.stop()

service = LogService(connection)
time_bounds = service.get_time_bounds()
options = service.get_filter_options()
filters = render_log_filters(options, time_bounds["min_timestamp"], time_bounds["max_timestamp"])
df = service.load_logs(filters)

show_dataframe_with_export(
    service.raw_grid(df),
    filename="raw_log_explorer.csv",
    title="Filtered logs",
)
