import psycopg

from marketdata.config import Settings


def connect(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        dbname=settings.postgres_db,
    )


def check_connection(settings: Settings) -> bool:
    try:
        with connect(settings) as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return False
    return True
