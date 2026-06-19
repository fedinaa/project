import pandas as pd
import re
import logging
import psycopg2
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine

DATA_DIR = Path(__file__).parent.parent / "data"

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "etl_dwh",
    "user": "postgres",
    "password": "admin",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("etl.log"), logging.StreamHandler()],
)

log = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def log_dq_error(errors, source, record_id, etype, detail):
    errors.append(
        {
            "source_table": source,
            "record_id": str(record_id),
            "error_type": etype,
            "error_detail": detail,
            "logged_at": datetime.now(),
        }
    )
