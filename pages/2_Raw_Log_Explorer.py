from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager
from src.components.sidebar import render_connection_settings, render_log_filters
from src.components.tables import show_dataframe_with_export
from src.data.mongo_client import MongoConnectionFactory
from src.services.log_service import LogService
from src.config.constants import STACK_FIELD, ERROR_MESSAGE_FIELD, ERROR_NAME_FIELD, REQUEST_URL_FIELD, STATUS_CODE_FIELD, TIMESTAMP_FIELD

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
important_columns = [
TIMESTAMP_FIELD,
STATUS_CODE_FIELD,
REQUEST_URL_FIELD,
ERROR_NAME_FIELD,
    
STACK_FIELD,
]

show_dataframe_with_export(
    service.raw_grid(df),
    filename="raw_log_explorer.csv",
    title="Filtered logs",
)



if not df.empty:
    st.subheader("Stack trace viewer")
    selected_index = st.number_input(
        "Select row index",
        min_value=0,
        max_value=len(df) - 1,
        value=0,
        step=1,
    )

    selected_row =df.iloc[int(selected_index)]
    st.write("Endpoint:", selected_row.get(REQUEST_URL_FIELD))
    st.write("Error:", selected_row.get(ERROR_MESSAGE_FIELD))
    st.code(str(selected_row.get(STACK_FIELD, "")), language="text")
