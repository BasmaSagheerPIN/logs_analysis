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
    page_title="Logbook Observability Dashboard",
    page_icon="📊",
    layout="wide",
)

# Authentication is not enabled yet, but the placeholder class is ready.
auth_manager = AuthManager()
auth_manager.render_placeholder_banner()

st.title("📊 Logbook Observability Dashboard")
st.write(
    """
This dashboard is designed for debugging and analyzing backend logs stored in MongoDB.

Use the pages in the sidebar:
- **Home**: quick overview and raw sample
- **System Health**: requests/minute, error rate, avg latency
- **Security**: requests by IP/user and simple suspicious-activity heuristics
- **Backend Performance**: slow endpoints and error endpoints
- **DB Errors**: database-related errors with stack traces and export
- **Raw Log Explorer**: Power BI–style filtering and export
"""
)

st.info(
    """
**Connection settings live in the sidebar on every page.**
That lets developers point the dashboard to a local, dev, staging, or production MongoDB instance
without editing code.
"""
)
