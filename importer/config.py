from pathlib import Path

from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = dotenv_values(BASE_DIR / ".env")

TEST_DIR = BASE_DIR / "test_dir"
WATCH_DIR = ENV_FILE.get("WATCH_DIR") or TEST_DIR
SQL_DIR = Path(__file__).resolve().parent / "sql"

REPORT_DIR = BASE_DIR / "reports"
FAILED_DIR = REPORT_DIR / "failed"
UNKNOWN_DIR = REPORT_DIR / "unknown"
LOG_DIR = BASE_DIR / "log"

FILE_PROD_DOP = "prod_dop.xml"
FILE_WAREHOUSES = "warehouses.xml"
REPORT_FILE_NAME = "report.json"
LOG_FILE_NAME = "xml_importer.log"

DB_CONFIG = {
    "host": ENV_FILE.get("HOST"),
    "port": int(ENV_FILE.get("PORT") or 3306),
    "user": ENV_FILE.get("ADMIN_USER"),
    "password": ENV_FILE.get("ADMIN_PASSWORD"),
    "database": ENV_FILE.get("DATABASE"),
    "autocommit": False,
}

SQL_CONFIG = {
    "prod_dop": {
        "upsert": "prod_dop/upsert.sql",
        "tmp_table": "prod_dop/tmp_table.sql",
        "delete": "prod_dop/delete_missing.sql",
        "insert_keys_stmt": "INSERT INTO tmp_prod_dop_ids (id_1c) VALUES (%s)"
    },
    "warehouses": {
        "upsert": "warehouses/upsert.sql",
        "tmp_table": "warehouses/tmp_table.sql",
        "delete": "warehouses/delete_missing.sql",
        "insert_keys_stmt": "INSERT INTO tmp_warehouses_keys (product_id_1c, stock_id_1c) VALUES (%s, %s)"
    }
}

LOGGER_CONFIG = {
    "file_path": LOG_DIR / LOG_FILE_NAME,
    "rotation": "10 MB",
    "retention": "1 week",
    "compression": "gz",
    "level": "INFO",
}

DATE_FORMAT_XML = "%Y-%m-%d"
DATE_FORMAT_LOG = "%Y%m%d_%H%M%S"
DATE_FORMAT_REPORT = "%Y-%m-%d %H:%M:%S"

XML_ENCODING = "utf-8"

for directory in [REPORT_DIR, FAILED_DIR, UNKNOWN_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
