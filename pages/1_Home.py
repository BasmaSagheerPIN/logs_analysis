from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager
from src.components.sidebar import render_connection_settings, render_log_filters
from src.components.tables import show_dataframe_with_export
from src.data.mongo_client import MongoConnectionFactory
from src.services.log_service import LogService

st.title("Home")
st.caption("Overview page with quick KPIs and latest logs.")

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
kpis = service.get_home_overview(df)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total system/user transactions", kpis["total_requests"])
with c2:
    st.metric("Error rate", f'{kpis["error_rate_pct"]}%')
with c3:
    st.metric("Avg latency", f'{kpis["avg_latency_ms"]} ms')

c4, c5, c6 = st.columns(3)
with c4:
    st.metric("Error requests", kpis["error_requests"])
with c5:
    st.metric("Unique users", kpis["unique_users"])
with c6:
    st.metric("Unique IPs", kpis["unique_ips"])

show_dataframe_with_export(
    service.raw_grid(df).head(200),
    filename="home_latest_logs.csv",
    title="Latest Logs (first 200 rows)",
)
