import sys

import mariadb

from importer.config import DB_CONFIG
from importer.logger import logger


def connect_db() -> mariadb.Connection:
    """
    Устанавливает соединение с MariaDB/MySQL, используя настройки из DB_CONFIG.
    Завершает работу приложения в случае критической ошибки подключения.
    """
    try:
        conn = mariadb.connect(**DB_CONFIG)
        logger.info("Подключение к базе данных выполнено успешно!")
        return conn
    except mariadb.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}.")
        sys.exit(1)

def close_db(conn: mariadb.Connection) -> None:
    """Закрывает соединение с базой данных."""
    try:
        conn.close()
        logger.info("Соединение с базой данных закрыто.")
    except mariadb.Error as e:
        logger.error(f"Ошибка при закрытии соединения с базой данных: {e}")
