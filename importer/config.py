from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = dotenv_values(BASE_DIR / ".env")

@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    autocommit: bool = False

def _require(var_name: str) -> str:
    value = ENV_FILE.get(var_name)
    if not value:
        raise ValueError(f"Отсутствует обязательная переменная окружения: {var_name}")
    return value

COMMON_DB_CONFIG = {
    "host": _require("DB_HOST"),
    "port": int(_require("DB_PORT")),
    "database": _require("DB_NAME"),
}

admin_db_config = DBConfig(
    **COMMON_DB_CONFIG,
    user=_require("DB_ADMIN_USERNAME"),
    password=_require("DB_ADMIN_PASSWORD"),
    autocommit=False,
)

app_db_config = DBConfig(
    **COMMON_DB_CONFIG,
    user=_require("DB_APP_USERNAME"),
    password=_require("DB_APP_PASSWORD"),
    autocommit=False,
)

DB_APP_ALLOWED_HOST = _require("DB_APP_ALLOWED_HOST")

TEST_DIR = BASE_DIR / "test_dir"
IMPORT_DIR = _require("IMPORT_DIR")
SQL_DIR = Path(__file__).resolve().parent / "sql"

REPORT_DIR = BASE_DIR / "reports"
FAILED_DIR = REPORT_DIR / "failed"
UNKNOWN_DIR = REPORT_DIR / "unknown"
LOG_DIR = BASE_DIR / "log"

FILE_PROD_DOP = "prod_dop.xml"
FILE_WAREHOUSES = "warehouses.xml"
REPORT_FILE_NAME = "report.json"
LOG_FILE_NAME = "xml_importer.log"

TABLE_PROD_DROP="tbl_prod_dop"
TABLE_WAREHOUSES="warehouses"

SQL_CONFIG = {
    TABLE_PROD_DROP: {
        "tmp_table": "prod_dop/tmp_table.sql",
        "insert": "prod_dop/insert.sql",
        "update": "prod_dop/update.sql",
        "delete": "prod_dop/delete_missing.sql",
        "target_table": TABLE_PROD_DROP,
        "columns_list": "id_1c, it_ya",
    },
    TABLE_WAREHOUSES: {
        "tmp_table": "warehouses/tmp_table.sql",
        "insert": "warehouses/insert.sql",
        "update": "warehouses/update.sql",
        "delete": "warehouses/delete_missing.sql",
        "target_table": TABLE_WAREHOUSES,
        "columns_list":
            "product_id_1c, stock_id_1c, edit_date, price, it_rrc, change_price_date, load_price_date, arch",
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

XML_ENCODING = "utf-8"

for directory in [REPORT_DIR, FAILED_DIR, UNKNOWN_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
