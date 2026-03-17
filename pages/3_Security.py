from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager
from src.components.charts import bar_chart
from src.components.sidebar import render_connection_settings, render_log_filters
from src.components.tables import show_dataframe_with_export
from src.data.mongo_client import MongoConnectionFactory
from src.services.log_service import LogService

st.title("Security")
st.caption("Requests by IP/user and simple suspicious activity heuristics.")

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

by_ip = service.requests_by_ip(df).head(20)
by_user = service.requests_by_user(df).head(20)
suspicious = service.suspicious_activity(df).head(50)

bar_chart(by_ip, x="metadata.ip", y="requests", title="Top IPs by request count")
bar_chart(by_user, x="metadata.user_id", y="requests", title="Top users by request count")
show_dataframe_with_export(suspicious, "suspicious_activity.csv", "Suspicious Activity Heuristics")

with st.expander("How suspicious activity is calculated"):
    st.write(
        """
This page uses a simple explainable score, not machine learning.

Suspicion score =
- request count × 0.4
- error count × 2.0
- distinct endpoints × 0.8

This helps surface unusual actors for investigation.
"""
    )

show_dataframe_with_export(by_ip, "requests_by_ip.csv", "Requests by IP")
show_dataframe_with_export(by_user, "requests_by_user.csv", "Requests by user")
