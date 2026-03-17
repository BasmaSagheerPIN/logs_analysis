from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager
from src.components.charts import bar_chart
from src.components.sidebar import render_connection_settings, render_log_filters
from src.components.tables import show_dataframe_with_export
from src.data.mongo_client import MongoConnectionFactory
from src.services.log_service import LogService

st.title("Backend Performance")
st.caption("Slow endpoints and error endpoints.")

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

slow_endpoints = service.slow_endpoints(df).head(20)
error_endpoints = service.error_endpoints(df).head(20)

bar_chart(slow_endpoints, x="metadata.endpoint", y="avg_latency_ms", title="Slow endpoints by average latency")
bar_chart(error_endpoints, x="metadata.endpoint", y="errors", title="Endpoints with most errors")

show_dataframe_with_export(slow_endpoints, "slow_endpoints.csv", "Slow endpoints")
show_dataframe_with_export(error_endpoints, "error_endpoints.csv", "Error endpoints")
