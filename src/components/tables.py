"""
Table and export helpers.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.utils.exporters import dataframe_to_csv_bytes


def show_dataframe_with_export(df: pd.DataFrame, filename: str, title: str = "Data"):
    st.subheader(title)
    if df.empty:
        st.warning("No data found for the current filters.")
        return

    st.download_button(
        label="Download CSV",
        data=dataframe_to_csv_bytes(df),
        file_name=filename,
        mime="text/csv",
    )
    st.dataframe(df, use_container_width=True)
    st.caption(f"Rows: {len(df)}")
