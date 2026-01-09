from dataclasses import asdict

import mariadb

from importer.config import DBConfig, app_db_config
from importer.logger import logger


def connect_db(config: DBConfig = app_db_config):
    """
    Устанавливает соединение с MariaDB/MySQL, используя настройки из DB_CONFIG.
    Завершает работу приложения в случае критической ошибки подключения.
    """
    try:
        conn = mariadb.connect(**asdict(config))
        logger.info(
            f"Подключение к БД установлено: db={config.database}, user={config.user}."
        )
        return conn
    except mariadb.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}.")
        raise

def close_db(conn) -> None:
    """Закрывает соединение с базой данных."""
    try:
        conn.close()
        logger.info("Соединение с БД закрыто.")
    except mariadb.Error as e:
        logger.error(f"Ошибка при закрытии соединения с базой данных: {e}")

def check_db_connection() -> bool:
    """
    Проверяет доступность базы данных (использует дефолтный конфиг).
    """
    try:
        conn = connect_db()
        close_db(conn)
        return True
    except Exception:
        return False
