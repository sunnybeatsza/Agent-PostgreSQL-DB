try:
    from _path import add_project_root_to_path
except ModuleNotFoundError:
    from scripts._path import add_project_root_to_path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

add_project_root_to_path()

from app.config import get_settings, parse_pg_conninfo
from app.database import engine


def main() -> int:
    settings = get_settings()
    if settings.postgres_conninfo:
        conninfo = parse_pg_conninfo(settings.postgres_conninfo)
        print(f"Testing database: {conninfo.get('host')}:{conninfo.get('port', settings.postgres_port)}/{conninfo.get('dbname')}")
        print(f"User: {conninfo.get('user')}")
    else:
        print(f"Testing database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
        print(f"User: {settings.postgres_user}")

    try:
        with engine.connect() as connection:
            version = connection.execute(text("SELECT version()")).scalar_one()
            current_database = connection.execute(text("SELECT current_database()")).scalar_one()
            current_user = connection.execute(text("SELECT current_user")).scalar_one()
    except (SQLAlchemyError, ValueError) as exc:
        print("Database connection failed.")
        print(f"Reason: {exc}")
        return 1

    print("Database connection successful.")
    print(f"Database: {current_database}")
    print(f"Connected user: {current_user}")
    print(f"PostgreSQL version: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
