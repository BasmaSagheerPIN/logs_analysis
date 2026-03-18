"""
Authentication placeholder.

You mentioned that later you want to add Microsoft Entra ID.
This class is intentionally simple right now, but it gives you one place to wire auth later.

Where to extend later:
- validate token / session
- map Entra roles/groups to app roles
- protect pages based on permission
"""
from __future__ import annotations

import streamlit as st


class AuthManager:
    def render_placeholder_banner(self) -> None:
        st.caption("Authentication: disabled for now. SSO Entra ID integration could be implemented later")
