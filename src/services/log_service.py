"""
Business/service layer.

This class contains application logic:
- load raw logs
- build overview KPIs
- compute system health
- compute security views
- compute performance views
- isolate DB errors

Repository = Mongo access
Service = business meaning
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Tuple

import pandas as pd

from src.config.constants import (
    APP_NAME_FIELD,
    DEFAULT_COLUMNS,
    DURATION_FIELD,
    ENVIRONMENT_FIELD,
    ERROR_MESSAGE_FIELD,
    ERROR_NAME_FIELD,
    EVENT_TYPE_FIELD,
    IP_FIELD,
    LEVEL_FIELD,
    MESSAGE_FIELD,
    REQUEST_METHOD_FIELD,
    REQUEST_URL_FIELD,
    STACK_FIELD,
    STATUS_CODE_FIELD,
    TIMESTAMP_FIELD,
    USER_FIELD,
)
from src.data.log_repository import LogRepository
from src.models.config_models import ConnectionConfig, LogFilters
from src.utils.dataframe import normalize_documents, safe_column
from src.utils.query_builder import QueryBuilder


class LogService:
    def __init__(self, connection_config: ConnectionConfig) -> None:
        self.connection_config = connection_config
        self.repository = LogRepository(connection_config)

    def get_filter_options(self) -> Dict[str, List]:
        return {
            "levels": self.repository.get_distinct_values(LEVEL_FIELD),
            "event_types": self.repository.get_distinct_values(EVENT_TYPE_FIELD),
            "methods": self.repository.get_distinct_values(REQUEST_METHOD_FIELD),
            "environments": self.repository.get_distinct_values(ENVIRONMENT_FIELD),
            "status_codes": self.repository.get_distinct_values(STATUS_CODE_FIELD),
        }

    def get_time_bounds(self) -> Dict[str, pd.Timestamp]:
        raw = self.repository.get_min_max_timestamp()
        return {
            "min_timestamp": pd.to_datetime(raw["min_timestamp"], errors="coerce"),
            "max_timestamp": pd.to_datetime(raw["max_timestamp"], errors="coerce"),
        }

    def load_logs(self, filters: LogFilters) -> pd.DataFrame:
        query = QueryBuilder.build_log_query(filters)
        docs = self.repository.find_logs(query=query, limit=self.connection_config.fetch_limit)
        df = normalize_documents(docs)

        # Make sure expected fields exist even when some logs are missing them.
        for field in [
            TIMESTAMP_FIELD,
            LEVEL_FIELD,
            MESSAGE_FIELD,
            EVENT_TYPE_FIELD,
            REQUEST_METHOD_FIELD,
            REQUEST_URL_FIELD,
            STATUS_CODE_FIELD,
            DURATION_FIELD,
            USER_FIELD,
            IP_FIELD,
            ERROR_NAME_FIELD,
            ERROR_MESSAGE_FIELD,
            STACK_FIELD,
            ENVIRONMENT_FIELD,
            APP_NAME_FIELD,
        ]:
            if field not in df.columns:
                df[field] = None

        return df

    def get_home_overview(self, df: pd.DataFrame) -> Dict[str, float]:
        if df.empty:
            return {
                "total_requests": 0,
                "error_requests": 0,
                "error_rate_pct": 0.0,
                "avg_latency_ms": 0.0,
                "unique_users": 0,
                "unique_ips": 0,
            }

        status_series = pd.to_numeric(df[STATUS_CODE_FIELD], errors="coerce")
        duration_series = pd.to_numeric(df[DURATION_FIELD], errors="coerce")

        total_requests = len(df)
        error_requests = int((status_series >= 400).fillna(False).sum())
        error_rate_pct = round((error_requests / total_requests) * 100, 2) if total_requests else 0.0
        avg_latency_ms = round(duration_series.dropna().mean(), 2) if not duration_series.dropna().empty else 0.0

        return {
            "total_requests": total_requests,
            "error_requests": error_requests,
            "error_rate_pct": error_rate_pct,
            "avg_latency_ms": avg_latency_ms,
            "unique_users": int(df[USER_FIELD].dropna().nunique()),
            "unique_ips": int(df[IP_FIELD].dropna().nunique()),
        }

    def requests_per_minute(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["minute", "requests"])

        temp = df.copy()
        temp["minute"] = temp[TIMESTAMP_FIELD].dt.floor("min")
        result = temp.groupby("minute").size().reset_index(name="requests")
        return result.sort_values("minute")

    def error_rate_over_time(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["minute", "requests", "errors", "error_rate_pct"])

        temp = df.copy()
        temp["minute"] = temp[TIMESTAMP_FIELD].dt.floor("min")
        temp["is_error"] = pd.to_numeric(temp[STATUS_CODE_FIELD], errors="coerce") >= 400
        result = (
            temp.groupby("minute")
            .agg(requests=(STATUS_CODE_FIELD, "size"), errors=("is_error", "sum"))
            .reset_index()
        )
        result["error_rate_pct"] = (result["errors"] / result["requests"] * 100).round(2)
        return result.sort_values("minute")

    def latency_over_time(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["minute", "avg_latency_ms"])

        temp = df.copy()
        temp["minute"] = temp[TIMESTAMP_FIELD].dt.floor("min")
        temp[DURATION_FIELD] = pd.to_numeric(temp[DURATION_FIELD], errors="coerce")
        result = temp.groupby("minute")[DURATION_FIELD].mean().reset_index(name="avg_latency_ms")
        result["avg_latency_ms"] = result["avg_latency_ms"].round(2)
        return result.sort_values("minute")

    def requests_by_ip(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=[IP_FIELD, "requests"])
        result = (
            df.groupby(IP_FIELD)
            .size()
            .reset_index(name="requests")
            .sort_values("requests", ascending=False)
        )
        return result

    def requests_by_user(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=[USER_FIELD, "requests"])
        result = (
            df.groupby(USER_FIELD)
            .size()
            .reset_index(name="requests")
            .sort_values("requests", ascending=False)
        )
        return result

    def suspicious_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        A simple, explainable heuristic.

        We mark an IP or user as suspicious when there are:
        - many requests
        - many error responses
        - many distinct endpoints

        This is not a security product. It is just a helpful debug signal.
        """
        if df.empty:
            return pd.DataFrame(columns=["actor_type", "actor", "requests", "errors", "distinct_endpoints", "suspicion_score"])

        temp = df.copy()
        temp["is_error"] = pd.to_numeric(temp[STATUS_CODE_FIELD], errors="coerce") >= 400

        actor_frames = []

        if IP_FIELD in temp.columns:
            by_ip = (
                temp.groupby(IP_FIELD)
                .agg(
                    requests=(MESSAGE_FIELD, "size"),
                    errors=("is_error", "sum"),
                    distinct_endpoints=(REQUEST_URL_FIELD, "nunique"),
                )
                .reset_index()
                .rename(columns={IP_FIELD: "actor"})
            )
            by_ip["actor_type"] = "IP"
            actor_frames.append(by_ip)

        if USER_FIELD in temp.columns:
            by_user = (
                temp.groupby(USER_FIELD)
                .agg(
                    requests=(MESSAGE_FIELD, "size"),
                    errors=("is_error", "sum"),
                    distinct_endpoints=(REQUEST_URL_FIELD, "nunique"),
                )
                .reset_index()
                .rename(columns={USER_FIELD: "actor"})
            )
            by_user["actor_type"] = "User"
            actor_frames.append(by_user)

        if not actor_frames:
            return pd.DataFrame(columns=["actor_type", "actor", "requests", "errors", "distinct_endpoints", "suspicion_score"])

        result = pd.concat(actor_frames, ignore_index=True)
        result["suspicion_score"] = (
            result["requests"] * 0.4 +
            result["errors"] * 2.0 +
            result["distinct_endpoints"] * 0.8
        ).round(2)
        return result.sort_values("suspicion_score", ascending=False)

    def slow_endpoints(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=[REQUEST_URL_FIELD, "requests", "avg_latency_ms", "p95_latency_ms"])

        temp = df.copy()
        temp[DURATION_FIELD] = pd.to_numeric(temp[DURATION_FIELD], errors="coerce")
        grouped = temp.groupby(REQUEST_URL_FIELD)[DURATION_FIELD]
        result = grouped.agg(["count", "mean"]).reset_index()
        result.columns = [REQUEST_URL_FIELD, "requests", "avg_latency_ms"]

        p95 = grouped.quantile(0.95).reset_index(name="p95_latency_ms")
        result = result.merge(p95, on=REQUEST_URL_FIELD, how="left")
        result["avg_latency_ms"] = result["avg_latency_ms"].round(2)
        result["p95_latency_ms"] = result["p95_latency_ms"].round(2)
        return result.sort_values(["avg_latency_ms", "p95_latency_ms"], ascending=False)

    def error_endpoints(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=[REQUEST_URL_FIELD, "requests", "errors", "error_rate_pct"])

        temp = df.copy()
        temp["is_error"] = pd.to_numeric(temp[STATUS_CODE_FIELD], errors="coerce") >= 400
        result = (
            temp.groupby(REQUEST_URL_FIELD)
            .agg(requests=(MESSAGE_FIELD, "size"), errors=("is_error", "sum"))
            .reset_index()
        )
        result["error_rate_pct"] = (result["errors"] / result["requests"] * 100).round(2)
        return result.sort_values(["errors", "error_rate_pct"], ascending=False)

    def db_errors(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=[])

        temp = df.copy()
        mask = (
            temp[MESSAGE_FIELD].fillna("").str.contains("database|sequelize|mongo|sql", case=False, regex=True)
            | temp[ERROR_MESSAGE_FIELD].fillna("").str.contains("database|sequelize|mongo|sql|column|relation|constraint|query", case=False, regex=True)
            | temp[STACK_FIELD].fillna("").str.contains("sequelize|mongo|sql", case=False, regex=True)
        )
        result = temp[mask].copy()
        return result.sort_values(TIMESTAMP_FIELD, ascending=False)

    def raw_grid(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        # Prefer important columns first, then append the rest.
        leading = [col for col in DEFAULT_COLUMNS if col in df.columns]
        trailing = [col for col in df.columns if col not in leading]
        return df[leading + trailing]
