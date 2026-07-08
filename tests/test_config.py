from app.config import Settings, parse_pg_conninfo


def test_parse_pg_conninfo_accepts_raw_libpq_string():
    values = parse_pg_conninfo(
        "host=g13hackathon-postgredb.postgres.database.azure.com "
        "port=5432 dbname=postgres user=user@example.com password=secret sslmode=require"
    )

    assert values["host"] == "g13hackathon-postgredb.postgres.database.azure.com"
    assert values["port"] == "5432"
    assert values["dbname"] == "postgres"
    assert values["user"] == "user@example.com"
    assert values["password"] == "secret"
    assert values["sslmode"] == "require"


def test_parse_pg_conninfo_accepts_azure_pg_connect_wrapper():
    values = parse_pg_conninfo(
        'pg_connect("host=my-server.postgres.database.azure.com port=5432 '
        'dbname=postgres user=user@example.com password=secret");'
    )

    assert values == {
        "host": "my-server.postgres.database.azure.com",
        "port": "5432",
        "dbname": "postgres",
        "user": "user@example.com",
        "password": "secret",
    }


def test_settings_builds_sqlalchemy_url_from_pg_variables(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings(
        PGHOST="server.postgres.database.azure.com",
        PGPORT=5432,
        PGDATABASE="postgres",
        PGUSER="user@example.com",
        PGPASSWORD="secret",
    )

    assert settings.sqlalchemy_database_url == (
        "postgresql+psycopg://user%40example.com:secret@"
        "server.postgres.database.azure.com:5432/postgres?sslmode=require"
    )


def test_settings_prefers_connector_string_over_pg_variables(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings(
        POSTGRES_CONNINFO=(
            "host=server.postgres.database.azure.com port=5432 "
            "dbname=postgres user=user@example.com password=secret sslmode=require"
        ),
        PGHOST="ignored-host",
        PGDATABASE="ignored-db",
        PGUSER="ignored-user",
        PGPASSWORD="ignored-password",
    )

    assert settings.sqlalchemy_database_url == (
        "postgresql+psycopg://user%40example.com:secret@"
        "server.postgres.database.azure.com:5432/postgres?sslmode=require"
    )
