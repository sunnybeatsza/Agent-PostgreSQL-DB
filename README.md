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

4. Edit `.env` with your Azure PostgreSQL connection details.

   You can either set `DATABASE_URL` directly:

   ```env
   DATABASE_URL=postgresql+psycopg://db_user:db_password@your-server.postgres.database.azure.com:5432/your_database?sslmode=require
   ```

   Or leave `DATABASE_URL` empty and set `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

## Run

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API docs are available at `http://127.0.0.1:8000/docs`.

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
| `POSTGRES_HOST` | If no `DATABASE_URL` | Azure PostgreSQL host. |
| `POSTGRES_PORT` | No | PostgreSQL port, defaults to `5432`. |
| `POSTGRES_DB` | If no `DATABASE_URL` | Database name. |
| `POSTGRES_USER` | If no `DATABASE_URL` | Database username. |
| `POSTGRES_PASSWORD` | If no `DATABASE_URL` | Database password. |
| `POSTGRES_SSLMODE` | No | Defaults to `require`, which Azure PostgreSQL commonly needs. |
| `AUTO_CREATE_TABLES` | No | Defaults to `true`; creates the agent tables on app startup. |
