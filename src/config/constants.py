"""
Central field-name constants.

Keeping all Mongo / flattened field names here makes schema changes easier.
If your logging schema changes later, update these constants first.
"""
from __future__ import annotations

TIMESTAMP_FIELD = "timestamp"
LEVEL_FIELD = "level"
MESSAGE_FIELD = "message"

# Flattened metadata.* fields after pandas.json_normalize(...)
ENVIRONMENT_FIELD = "metadata.environment"
EVENT_SOURCE_FIELD = "metadata.event_source"
APP_NAME_FIELD = "metadata.app_name"
DEPLOYMENT_VERSION_FIELD = "metadata.deployment_version"
EVENT_TYPE_FIELD = "metadata.event_type"
REQUEST_METHOD_FIELD = "metadata.method"
REQUEST_URL_FIELD = "metadata.endpoint"
STATUS_CODE_FIELD = "metadata.status_code"
DURATION_FIELD = "metadata.duration_ms"
USER_FIELD = "metadata.user_id"
IP_FIELD = "metadata.ip"
ERROR_NAME_FIELD = "metadata.error_name"
ERROR_MESSAGE_FIELD = "metadata.error_message"
STACK_FIELD = "metadata.stack"

DEFAULT_COLUMNS = [
    TIMESTAMP_FIELD,
    LEVEL_FIELD,
    EVENT_TYPE_FIELD,
    REQUEST_METHOD_FIELD,
    REQUEST_URL_FIELD,
    STATUS_CODE_FIELD,
    DURATION_FIELD,
    USER_FIELD,
    IP_FIELD,
    MESSAGE_FIELD,
    ERROR_MESSAGE_FIELD,
]
