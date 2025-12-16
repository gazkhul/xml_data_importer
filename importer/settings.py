from pathlib import Path

from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = dotenv_values(BASE_DIR / ".env")
LOGS_DIR = BASE_DIR / "logs"
WATCH_DIR = CONFIG.get("WATCH_DIR", f"{BASE_DIR}/test_dir")

DB_CONFIG = {
    "host": CONFIG.get("HOST", ""),
    "port": int(CONFIG.get("PORT") or 3306),
    "user": CONFIG.get("ADMIN_USER", ""),
    "password": CONFIG.get("ADMIN_PASSWORD", ""),
    "database": CONFIG.get("DATABASE", ""),
    "autocommit": False,
}
