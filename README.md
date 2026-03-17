# Logbook Observability Dashboard

A professional Streamlit project for exploring backend logs stored in MongoDB.

## What this project includes

- Connection panel in the sidebar:
  - Mongo URI
  - DB name
  - Collection name
  - fetch limit
- Reusable filter panel:
  - level
  - event type
  - method
  - environment
  - status code
  - endpoint text
  - user text
  - IP text
  - free text
  - date + time range
  - only errors
- Pages:
  - Home
  - System Health
  - Security
  - Backend Performance
  - DB Errors
  - Raw Log Explorer
- CSV export on every main table
- Prepared structure for future Entra ID authentication

## Assumed MongoDB log schema

This project matches your current backend log schema, where many fields are stored inside `metadata`:

```json
{
  "timestamp": "2026-03-16T11:49:45.952Z",
  "level": "error",
  "message": "HTTP request failed",
  "metadata": {
    "environment": "development",
    "event_source": "backend",
    "app_name": "@logbook/backend",
    "deployment_version": "0.6.1",
    "event_type": "HTTP_REQUEST_FAILED",
    "method": "POST",
    "endpoint": "/api/costs",
    "status_code": 500,
    "duration_ms": 63,
    "user_id": "czedrv0190",
    "ip": "127.0.0.1",
    "error_name": "SequelizeDatabaseError",
    "error_message": "column \"vehicleNo\" does not exist",
    "stack": "Error ..."
  }
}
```

## Project structure

- `src/data/` -> Mongo access only
- `src/services/` -> business logic
- `src/components/` -> reusable UI
- `src/config/` -> constants and settings
- `src/auth/` -> future auth integration point
- `pages/` -> Streamlit pages

This separation is important because it keeps the app maintainable and scalable.

## How to run locally

1. Create and activate a virtual environment
2. Install packages:

```bash
pip install -r requirements.txt
```

3. Copy the example secrets file:

```bash
copy .streamlit\secrets.example.toml .streamlit\secrets.toml
```

4. Update `.streamlit/secrets.toml` with your real values if needed
5. Run:

```bash
streamlit run app.py
```

## Why the code uses classes

Classes are used where they add structure:

- `MongoConnectionFactory` -> connection and ping
- `LogRepository` -> raw Mongo queries
- `LogService` -> metrics and dashboard logic
- `AuthManager` -> future authentication extension

This makes it easier to:
- add new pages
- swap data sources later
- add authentication/authorization
- test logic independently

## Security notes

- No Mongo credentials are hardcoded in the source code
- Secrets can come from Streamlit secrets or environment variables
- The sidebar lets developers override connection settings for debugging
- This app does not implement auth yet; keep it internal until Entra ID is added

## Future Entra ID integration

Later, you can extend `src/auth/auth_manager.py` to:
- read the signed-in user
- validate access tokens
- map Entra groups/roles
- hide pages based on permission

## Important performance note

For very large log volumes, consider:
- adding indexes on:
  - `timestamp`
  - `metadata.status_code`
  - `metadata.endpoint`
  - `metadata.user_id`
  - `metadata.ip`
- lowering `Rows to load`
- pushing more aggregation logic into MongoDB

## Suggested MongoDB indexes

```javascript
db["backend-logs"].createIndex({ timestamp: -1 })
db["backend-logs"].createIndex({ "metadata.status_code": 1 })
db["backend-logs"].createIndex({ "metadata.endpoint": 1 })
db["backend-logs"].createIndex({ "metadata.user_id": 1 })
db["backend-logs"].createIndex({ "metadata.ip": 1 })
```
