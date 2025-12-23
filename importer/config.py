from pathlib import Path

from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = dotenv_values(BASE_DIR / ".env")

TEST_DIR = BASE_DIR / "test_dir"
WATCH_DIR = ENV_FILE.get("WATCH_DIR") or TEST_DIR

SQL_DIR = Path(__file__).resolve().parent / "sql"

DB_CONFIG = {
    "host": ENV_FILE.get("HOST"),
    "port": int(ENV_FILE.get("PORT") or 3306),
    "user": ENV_FILE.get("ADMIN_USER"),
    "password": ENV_FILE.get("ADMIN_PASSWORD"),
    "database": ENV_FILE.get("DATABASE"),
    "autocommit": False,
}

LOG_DIR = BASE_DIR / "log"
LOG_FILE_NAME = "xml_importer.log"
LOGGER_CONFIG = {
    "file_path": LOG_DIR / LOG_FILE_NAME,
    "rotation": "10 MB",
    "retention": "1 week",
    "compression": "gz",
    "level": "INFO",
}
