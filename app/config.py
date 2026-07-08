from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Agent PostgreSQL API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    postgres_host: str | None = Field(default=None, alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str | None = Field(default=None, alias="POSTGRES_DB")
    postgres_user: str | None = Field(default=None, alias="POSTGRES_USER")
    postgres_password: str | None = Field(default=None, alias="POSTGRES_PASSWORD")
    postgres_sslmode: str = Field(default="require", alias="POSTGRES_SSLMODE")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        required = {
            "POSTGRES_HOST": self.postgres_host,
            "POSTGRES_DB": self.postgres_db,
            "POSTGRES_USER": self.postgres_user,
            "POSTGRES_PASSWORD": self.postgres_password,
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
