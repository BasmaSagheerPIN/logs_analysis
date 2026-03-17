from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager
from src.components.charts import line_chart
from src.components.sidebar import render_connection_settings, render_log_filters
from src.components.tables import show_dataframe_with_export
from src.data.mongo_client import MongoConnectionFactory
from src.services.log_service import LogService

st.title("System Health")
st.caption("Requests per minute, error rate, and average latency over time.")

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

rpm = service.requests_per_minute(df)
error_rate = service.error_rate_over_time(df)
latency = service.latency_over_time(df)

line_chart(rpm, x="minute", y="requests", title="Requests per minute")
line_chart(error_rate, x="minute", y="error_rate_pct", title="Error rate over time (%)")
line_chart(latency, x="minute", y="avg_latency_ms", title="Average latency over time (ms)")

show_dataframe_with_export(rpm, "requests_per_minute.csv", "Requests per minute")
show_dataframe_with_export(error_rate, "error_rate_over_time.csv", "Error rate over time")
show_dataframe_with_export(latency, "avg_latency_over_time.csv", "Average latency over time")
