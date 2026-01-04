from typing import Any

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
    delete_flag: bool,
    target_table: str,
    columns_list: str,
    tmp_table_sql_path: str,
    insert_sql_path: str,
    update_sql_path: str,
    delete_sql_path: str,
) -> dict[str, int]:
    """
    Синхронизирует данные с целевой таблицей через временную:
    UPDATE для изменённых строк, INSERT для новых и опциональный DELETE для отсутствующих.
    Возвращает количество новых, обновлённых и удалённых записей.
    """
    conn = connect_db()
    cursor = conn.cursor()

    inserted_count = 0
    updated_count = 0
    deleted_count = 0

    try:
        cursor.execute(_load_sql(tmp_table_sql_path))

        placeholders = ", ".join(["%s"] * len(rows[0]))
        insert_tmp_sql = f"""
            INSERT INTO tmp_{target_table}
            ({columns_list})
            VALUES ({placeholders})
        """
        cursor.executemany(insert_tmp_sql, rows)

        cursor.execute(_load_sql(update_sql_path))
        updated_count = max(cursor.rowcount, 0)

        cursor.execute(_load_sql(insert_sql_path))
        inserted_count = max(cursor.rowcount, 0)


        if delete_flag:
            cursor.execute(_load_sql(delete_sql_path))
            deleted_count = max(cursor.rowcount, 0)

        logger.info(
            f"Синхронизация '{target_table}': "
            f"inserted={inserted_count}, "
            f"updated={updated_count}, "
            f"deleted={deleted_count}."
        )

        conn.commit()
        logger.success("Транзакция зафиксирована.")

        return {
            "rows_inserted": inserted_count,
            "rows_updated": updated_count,
            "rows_deleted": deleted_count,
        }

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
