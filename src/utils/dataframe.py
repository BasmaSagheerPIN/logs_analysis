"""
Helpers for turning Mongo documents into clean pandas DataFrames.
"""
from __future__ import annotations

from typing import Iterable, List

import pandas as pd

from src.config.constants import TIMESTAMP_FIELD


def normalize_documents(docs: Iterable[dict]) -> pd.DataFrame:
    docs_list: List[dict] = list(docs)
    if not docs_list:
        return pd.DataFrame()

    # json_normalize flattens nested metadata.* fields into dot notation.
    df = pd.json_normalize(docs_list)

    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)

    if TIMESTAMP_FIELD in df.columns:
        df[TIMESTAMP_FIELD] = pd.to_datetime(df[TIMESTAMP_FIELD], errors="coerce", utc=True)
        # Convert to naive datetime so Streamlit charts/tables behave more naturally.
        try:
            df[TIMESTAMP_FIELD] = df[TIMESTAMP_FIELD].dt.tz_localize(None)
        except Exception:
            pass

    return df


def safe_column(df: pd.DataFrame, column_name: str, default_value=None) -> pd.Series:
    if column_name in df.columns:
        return df[column_name]
    return pd.Series([default_value] * len(df), index=df.index)
