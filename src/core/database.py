from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.core.config import load_env_by_prefix


class Database:
    _engine: Optional[Engine] = None
    _config: Optional[Dict[str, Any]] = None

    def __init__(self, echo: bool = False):
        if Database._engine is None:
            Database._config = self._load_config()
            Database._engine = self._create_engine(echo)
            self._init_schema()

    def _load_config(self) -> Dict[str, Any]:
        cfg = load_env_by_prefix("MLAPP", [])
        return {
            "host": cfg["host"],
            "port": cfg["port"],
            "database": cfg["database"],
            "user": cfg["user"],
            "password": cfg["password"],
            "schema": cfg.get("schema", "mlapp"),
            "adapter": cfg.get("adapter", "postgresql+psycopg2"),
        }

    def _create_engine(self, cls, echo: bool) -> Engine:
        c = cls._config
        url = (
            f"{c['adapter']}://{c['user']}:{c['password']}"
            f"@{c['host']}:{c['port']}/{c['database']}"
        )
        return create_engine(
            url,
            echo=echo,
            future=True,
            pool_pre_ping=True,
        )

    def _init_schema(self, cls):
        schema = cls._config["schema"]
        with cls._engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.execute(text(f"SET search_path TO {schema}"))

    def engine(self, cls) -> Engine:
        if cls._engine is None:
            cls()
        return cls._engine

    def connect(self, cls):
        return cls.engine().connect()
