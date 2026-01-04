
import mariadb

from importer.config import DB_CONFIG
from importer.logger import logger


def connect_db():
    """
    Устанавливает соединение с MariaDB/MySQL, используя настройки из DB_CONFIG.
    Завершает работу приложения в случае критической ошибки подключения.
    """
    try:
        conn = mariadb.connect(**DB_CONFIG)
        logger.info(
            f"Подключение к БД установлено: host={DB_CONFIG['host']}, db={DB_CONFIG['database']}"
        )
        return conn
    except mariadb.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}.")
        raise

def close_db(conn) -> None:
    """Закрывает соединение с базой данных."""
    try:
        conn.close()
        logger.info(f"Соединение с БД закрыто: host={DB_CONFIG['host']}, db={DB_CONFIG['database']}")
    except mariadb.Error as e:
        logger.error(f"Ошибка при закрытии соединения с базой данных: {e}")

def check_db_connection() -> bool:
    """
    Проверяет доступность базы данных.
    Возвращает True, если подключение успешно, иначе False.
    """
    try:
        conn = connect_db()
        close_db(conn)
        return True
    except Exception:
        return False
