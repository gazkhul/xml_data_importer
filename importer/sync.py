from typing import Any, Iterable

from mariadb import Error as mariadb_error

from importer.config import SQL_DIR
from importer.db import close_db, connect_db
from importer.logger import logger


def _load_sql(relative_path: str) -> str:
    """
    Загружает SQL из <PROJECT_ROOT>/importer/sql/**/*
    """
    path = SQL_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"SQL-файл не найден: {path}")
    return path.read_text(encoding="utf-8")

def sync_data(
    rows: list[Any],
    keys: Iterable[Any],
    delete_flag: bool,
    upsert_sql_path: str,
    tmp_table_sql_path: str,
    delete_sql_path: str,
    insert_tmp_key_sql: str,
) -> None:
    """
    Универсальная функция синхронизации данных (Upsert + Delete Missing).
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # --- UPSERT ---
        upsert_sql = _load_sql(upsert_sql_path)
        cursor.executemany(upsert_sql, rows)
        logger.info(f"Загружено записей (вставка/обновление): {cursor.rowcount}")

        # --- DELETE ---
        if delete_flag:
            logger.info("Удаление записей, отсутствующих в XML-файле.")

            tmp_table_sql = _load_sql(tmp_table_sql_path)
            cursor.execute(tmp_table_sql)

            cursor.executemany(insert_tmp_key_sql, list(keys))

            delete_sql = _load_sql(delete_sql_path)
            cursor.execute(delete_sql)
            logger.info(f"Удалено строк: {cursor.rowcount}.")

        conn.commit()
        logger.success("Транзакция зафиксирована.")

    except mariadb_error as e:
        conn.rollback()
        logger.error(f"Ошибка БД MariaDB (Code: {e.errno}): {e}")
        raise
    except Exception as e:
        conn.rollback()
        logger.exception(f"Ошибка синхронизации данных: {e}")
        raise
    finally:
        cursor.close()
        close_db(conn)
