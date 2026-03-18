"""
Main entry point for the Streamlit application.

This page is intentionally small:
- sets app-wide layout/title
- explains the available pages
- leaves all data logic to the service/repository layer

Streamlit automatically shows pages from the /pages directory in the sidebar.
"""
from __future__ import annotations

import streamlit as st

from src.auth.auth_manager import AuthManager

st.set_page_config(
    page_title="Logs analysis Dashboard",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/7/77/Logo_of_People_in_Need.png",
    layout="wide",
)

# Authentication is not enabled yet, but the placeholder class is ready.
auth_manager = AuthManager()
auth_manager.render_placeholder_banner()

st.title(" Logs analysis Dashboard")
st.write(
    """
This dashboard is designed for debugging and analyzing user transition logs stored in MongoDB.

Use the pages in the sidebar:
- **Home**: quick overview
- **Raw Log Explorer**: filtering and export logs
- **System Health**: requests/minute, error rate, avg latency
- **Backend Performance**: slow endpoints and error endpoints
- **DB Errors**: database-related errors with stack traces and export
- **Security**: requests by IP/user

"""
)

st.info(
    """
**For experiments**
"""
)
