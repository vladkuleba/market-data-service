import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int


def _require(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    return Settings(
        postgres_user=_require("POSTGRES_USER"),
        postgres_password=_require("POSTGRES_PASSWORD"),
        postgres_db=_require("POSTGRES_DB"),
        postgres_host=_require("POSTGRES_HOST"),
        postgres_port=int(_require("POSTGRES_PORT")),
    )
