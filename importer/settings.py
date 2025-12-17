from pathlib import Path

from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = dotenv_values(BASE_DIR / ".env")

TEST_DIR = BASE_DIR / "test_dir"
WATCH_DIR = CONFIG.get("WATCH_DIR") or TEST_DIR

SQL_DIR = Path(__file__).resolve().parent / "sql"

DB_CONFIG = {
    "host": CONFIG.get("HOST"),
    "port": int(CONFIG.get("PORT") or 3306),
    "user": CONFIG.get("ADMIN_USER"),
    "password": CONFIG.get("ADMIN_PASSWORD"),
    "database": CONFIG.get("DATABASE"),
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
