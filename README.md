# Agent-PostgreSQL-DB

Python FastAPI webserver for CRUD operations against an Azure PostgreSQL database used by home energy management AI agents.

The API supports:

- Consumer agent records: consumer profiles, smart meter data, consumer reports, and consumer alerts.
- Government agent records: regional meter data, government reports, and technician data.

## Setup

1. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create your environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Edit `.env` with your Azure PostgreSQL connection details. Leave only one connection style uncommented.

   You can either set `DATABASE_URL` directly:

   ```env
   DATABASE_URL=postgresql+psycopg://db_user:db_password@your-server.postgres.database.azure.com:5432/your_database?sslmode=require
   ```

   Or leave `DATABASE_URL` empty and set either:

   - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`
   - Azure/PostgreSQL CLI-style variables: `PGHOST`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`
   - Azure PostgreSQL connector/libpq format: `POSTGRES_CONNINFO` or `PGCONNECT_STRING`

## Run

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API docs are available at `http://127.0.0.1:8000/docs`.

## Tests

Run the unit tests locally:

```powershell
pytest
```

The tests use an in-memory SQLite database, so they do not connect to Azure PostgreSQL.

## Test Database Connection

After setting your environment variables, test the database connection directly from Python:

```powershell
python scripts/test_db_connection.py
```

Expected success output includes:

```text
Database connection successful.
Database: postgres
Connected user: ...
PostgreSQL version: ...
```

## Seed Demo Data

After the database connection works, insert pseudo data for local/API testing:

```powershell
python scripts/seed_db.py
```

The seed script creates demo consumer profiles, appliance-profiled smart meter readings, consumer reports, alerts, government meter data, government reports, and technician records. Meter readings include appliance breakdowns in `raw_payload.appliance_breakdown` plus seeded anomalies such as `geyser_stuck_on`, `cooking_load_spike`, `fridge_continuous_draw`, and `voltage_sag`. Seeded records use `SEED-` meter IDs and `seed.*@example.com` emails so they can be removed safely.

To remove only the seeded demo records:

```powershell
python scripts/cleanup_seed_data.py
```

## Endpoints

- `GET /health` - server health check
- `GET /health/db` - database connectivity check

Each resource supports:

- `POST /{resource}` - create a record
- `GET /{resource}` - list records with `limit` and `offset`
- `GET /{resource}/{record_id}` - get one record
- `PATCH /{resource}/{record_id}` - update one record
- `DELETE /{resource}/{record_id}` - delete one record

Consumer agent resources:

- `/consumer-profiles`
- `/consumer-meter-data`
- `/consumer-reports`
- `/consumer-alerts`

Government agent resources:

- `/gov-meter-data`
- `/government-reports`
- `/technicians-data`

## Tables

| Table | Purpose |
| --- | --- |
| `consumer_profiles` | Consumer identity, contact, household, and smart meter mapping. |
| `consumer_meter_data` | Consumer smart meter readings streamed into the system. |
| `consumer_reports` | AI-generated consumer energy insights and recommendations. |
| `consumer_alerts` | AI-generated alerts such as abnormal usage, outages, or safety concerns. |
| `gov_meter_data` | Government-level meter readings, regional grid health, and outage signals. |
| `government_reports` | AI-generated regional or municipal energy management reports. |
| `technicians_data` | Technician availability, region, specialty, and meter assignments. |

## Example requests

Create a consumer profile:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/consumer-profiles -ContentType "application/json" -Body '{"full_name":"Jane Doe","email":"jane@example.com","meter_id":"MTR-1001","household_size":4}'
```

Create consumer meter data:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/consumer-meter-data -ContentType "application/json" -Body '{"meter_id":"MTR-1001","reading_timestamp":"2026-07-08T19:30:00Z","energy_kwh":12.4,"voltage":230.1,"current_amp":18.2,"power_kw":4.1}'
```

Create a consumer alert:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/consumer-alerts -ContentType "application/json" -Body '{"meter_id":"MTR-1001","severity":"high","alert_type":"usage_spike","message":"Unusual consumption detected","detected_at":"2026-07-08T19:35:00Z"}'
```

Create government meter data:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/gov-meter-data -ContentType "application/json" -Body '{"meter_id":"MTR-1001","region":"Gauteng","municipality":"Johannesburg","reading_timestamp":"2026-07-08T19:30:00Z","energy_kwh":12.4,"outage_detected":false,"grid_health_score":88.5}'
```

List government reports:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/government-reports
```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Optional | Full SQLAlchemy PostgreSQL URL. If set, this takes priority. |
| `POSTGRES_CONNINFO` or `PGCONNECT_STRING` | Optional | Azure PostgreSQL connector/libpq string such as `host=... port=... dbname=... user=... password=...`. |
| `POSTGRES_HOST` or `PGHOST` | If no `DATABASE_URL` | Azure PostgreSQL host. |
| `POSTGRES_PORT` or `PGPORT` | No | PostgreSQL port, defaults to `5432`. |
| `POSTGRES_DB` or `PGDATABASE` | If no `DATABASE_URL` | Database name. |
| `POSTGRES_USER` or `PGUSER` | If no `DATABASE_URL` | Database username. |
| `POSTGRES_PASSWORD` or `PGPASSWORD` | If no `DATABASE_URL` | Database password or Azure AD access token. |
| `POSTGRES_SSLMODE` | No | Defaults to `require`, which Azure PostgreSQL commonly needs. |
| `AUTO_CREATE_TABLES` | No | Defaults to `true`; creates the agent tables on app startup. |

For Azure AD authentication, refresh `PGPASSWORD` before starting the server:

```powershell
$env:PGHOST="g13hackathon-postgredb.postgres.database.azure.com"
$env:PGUSER="makgerutumisho55@gmail.com"
$env:PGPORT="5432"
$env:PGDATABASE="postgres"
$env:PGPASSWORD=(az account get-access-token --resource https://ossrdbms-aad.database.windows.net --query accessToken --output tsv)
uvicorn app.main:app --reload
```

You can also use Azure's connector format directly:

```powershell
$env:POSTGRES_CONNINFO='host=g13hackathon-postgredb.postgres.database.azure.com port=5432 dbname=postgres user=makgerutumisho55@gmail.com password=your_password sslmode=require'
python scripts/test_db_connection.py
```

Or, if Azure gives you the full `pg_connect(...)` example:

```powershell
$env:PGCONNECT_STRING='pg_connect("host=g13hackathon-postgredb.postgres.database.azure.com port=5432 dbname=postgres user=makgerutumisho55@gmail.com password=your_password");'
python scripts/test_db_connection.py
```

## Deploy to Render

This repo includes `render.yaml` for Render Blueprint deployment and `.github/workflows/ci.yml` for GitHub Actions tests.

Recommended setup:

1. Push this repo to GitHub.
2. In Render, create a new Blueprint from the GitHub repo.
3. In the Render service environment variables, set `DATABASE_URL` as a secret value.
4. Let GitHub Actions run `pytest`.
5. Render will deploy automatically after CI checks pass.

For this app, the Render start command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If you use Azure PostgreSQL from Render, prefer a normal PostgreSQL password or long-lived connection string for `DATABASE_URL`. Azure AD access tokens expire and are not a good fit for a long-running hosted web service unless you add token refresh logic.
