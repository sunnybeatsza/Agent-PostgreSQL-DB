from functools import lru_cache
from pathlib import Path
import shlex
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


class Settings(BaseSettings):
    app_name: str = Field(default="Agent PostgreSQL API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    postgres_conninfo: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "POSTGRES_CONNINFO",
            "PGCONNECT_STRING",
            "AZURE_POSTGRESQL_CONNECTIONSTRING",
        ),
    )
    postgres_host: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_HOST", "PGHOST"),
    )
    postgres_port: int = Field(
        default=5432,
        validation_alias=AliasChoices("POSTGRES_PORT", "PGPORT"),
    )
    postgres_db: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_DB", "PGDATABASE"),
    )
    postgres_user: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_USER", "PGUSER"),
    )
    postgres_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_PASSWORD", "PGPASSWORD"),
    )
    postgres_sslmode: str = Field(default="require", alias="POSTGRES_SSLMODE")

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.postgres_conninfo:
            return self._sqlalchemy_url_from_conninfo(self.postgres_conninfo)

        required = {
            "POSTGRES_HOST or PGHOST": self.postgres_host,
            "POSTGRES_DB or PGDATABASE": self.postgres_db,
            "POSTGRES_USER or PGUSER": self.postgres_user,
            "POSTGRES_PASSWORD or PGPASSWORD": self.postgres_password,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            missing_text = ", ".join(missing)
            raise ValueError(f"Missing database configuration: {missing_text} or DATABASE_URL")

        user = quote_plus(self.postgres_user or "")
        password = quote_plus(self.postgres_password or "")
        host = self.postgres_host
        db_name = quote_plus(self.postgres_db or "")
        return (
            f"postgresql+psycopg://{user}:{password}@{host}:{self.postgres_port}/{db_name}"
            f"?sslmode={self.postgres_sslmode}"
        )

    def _sqlalchemy_url_from_conninfo(self, conninfo: str) -> str:
        values = parse_pg_conninfo(conninfo)
        required = {
            "host": values.get("host"),
            "dbname": values.get("dbname"),
            "user": values.get("user"),
            "password": values.get("password"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            missing_text = ", ".join(missing)
            raise ValueError(f"Missing connector fields: {missing_text}")

        return URL.create(
            drivername="postgresql+psycopg",
            username=values["user"],
            password=values["password"],
            host=values["host"],
            port=int(values.get("port", self.postgres_port)),
            database=values["dbname"],
            query={"sslmode": values.get("sslmode", self.postgres_sslmode)},
        ).render_as_string(hide_password=False)


def parse_pg_conninfo(conninfo: str) -> dict[str, str]:
    cleaned = conninfo.strip().rstrip(";")
    if cleaned.startswith("pg_connect(") and cleaned.endswith(")"):
        cleaned = cleaned[len("pg_connect(") : -1].strip()
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        cleaned = cleaned[1:-1]

    values: dict[str, str] = {}
    for token in shlex.split(cleaned):
        key, separator, value = token.partition("=")
        if separator:
            values[key] = value
    return values


@lru_cache
def get_settings() -> Settings:
    return Settings()
