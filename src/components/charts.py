"""
Chart helpers.

Using helper functions keeps page code focused on meaning, not repetitive plotting code.
"""
from __future__ import annotations

import plotly.express as px
import streamlit as st
import pandas as pd


def line_chart(df: pd.DataFrame, x: str, y: str, title: str):
    if df.empty:
        st.info("No data available for this chart.")
        return
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, orientation: str = "v"):
    if df.empty:
        st.info("No data available for this chart.")
        return
    fig = px.bar(df, x=x, y=y, title=title, orientation=orientation)
    st.plotly_chart(fig, use_container_width=True)
