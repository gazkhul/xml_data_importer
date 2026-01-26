from typing import Any, Dict, List

from mariadb import Error as mariadb_error

from importer.config import SQL_CONFIG, SQL_DIR, TABLE_STOCK_PRICES, app_db_config
from importer.db import close_db, connect_db
from importer.logger import logger


BATCH_SIZE = 10000

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
        is_delete: bool,
        target_table: str,
        columns_list: str,
        tmp_table_sql_path: str,
        insert_sql_path: str,
        update_sql_path: str,
        delete_sql_path: str,
    ) -> dict[str, int]:
    """
    Синхронизирует данные с целевой таблицей через временную:
    Возвращает статистику по операциям.
    """
    conn = connect_db(config=app_db_config)
    cursor = conn.cursor()

    stats = {
        "rows_inserted": 0,
        "rows_updated": 0,
        "rows_deleted": 0,
    }

    try:
        cursor.execute("START TRANSACTION")
        cursor.execute(_load_sql(tmp_table_sql_path))

        placeholders = ", ".join(["%s"] * len(rows[0]))
        insert_tmp_sql = f"""
            INSERT INTO tmp_{target_table}
            ({columns_list})
            VALUES ({placeholders})
        """

        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i + BATCH_SIZE]
            cursor.executemany(insert_tmp_sql, batch)

        cursor.execute(_load_sql(update_sql_path))
        stats["rows_updated"] += cursor.rowcount

        cursor.execute(_load_sql(insert_sql_path))
        stats["rows_inserted"] += cursor.rowcount


        if is_delete:
            cursor.execute(_load_sql(delete_sql_path))
            stats["rows_deleted"] += cursor.rowcount

        logger.info(
            f"Синхронизация '{target_table}': "
            f"inserted={stats['rows_inserted']}, "
            f"updated={stats['rows_updated']}, "
            f"deleted={stats['rows_deleted']}."
        )

        conn.commit()
        logger.success("Транзакция зафиксирована.")

        return stats

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

def sync_stock_prices(
        products_data: List,
        stocks_data: List,
        reset_flag: bool
    ) -> Dict[str, int]:
    cfg = SQL_CONFIG[TABLE_STOCK_PRICES]

    conn = connect_db(config=app_db_config)
    cursor = conn.cursor()

    stats = {}

    products_tuples = [(p.product_id_1c, p.price, p.total_quantity) for p in products_data]
    stocks_tuples = [(s.product_id_1c, s.stock_id_1c, s.quantity) for s in stocks_data]

    try:
        cursor.execute("START TRANSACTION")
        # Очистка дубликатов
        # cursor.execute(_load_sql("stock_prices/cleanup_duplicates.sql"))

        cursor.execute(_load_sql(cfg["tmp_products"]))
        cursor.execute(_load_sql(cfg["tmp_stocks"]))

        if products_tuples:
            for i in range(0, len(products_tuples), BATCH_SIZE):
                batch = products_tuples[i:i + BATCH_SIZE]
                cursor.executemany(_load_sql(cfg["insert_tmp_products"]), batch)

        if stocks_tuples:
            for i in range(0, len(stocks_tuples), BATCH_SIZE):
                batch = stocks_tuples[i:i + BATCH_SIZE]
                cursor.executemany(_load_sql(cfg["insert_tmp_stocks"]), batch)

        cursor.execute(_load_sql(cfg["update_products"]))
        # stats["updated_products"] = cursor.rowcount

        cursor.execute(_load_sql(cfg["update_skus"]))
        # stats["updated_skus"] = cursor.rowcount

        cursor.execute(_load_sql(cfg["upsert_stocks"]))
        # stats["upserted_stocks"] = cursor.rowcount

        cursor.execute(_load_sql(cfg["delete_missing_stocks_per_product"]))

        if reset_flag:
            cursor.execute(_load_sql(cfg["reset_products"]))
            # stats["reset_products"] = cursor.rowcount

            cursor.execute(_load_sql(cfg["reset_skus"]))
            # stats["reset_skus"] = cursor.rowcount

            cursor.execute(_load_sql(cfg["delete_stocks_for_missing_products"]))
            # stats["deleted_stocks"] = cursor.rowcount

        cursor.execute(_load_sql(cfg["clean_logs"]))

        conn.commit()
        logger.success("Синхронизация цен и остатков успешно завершена.")

        return stats

    except mariadb_error as e:
        conn.rollback()
        logger.error(f"Ошибка БД MariaDB (Code: {e.errno}): {e}")
        raise
    except Exception as e:
        conn.rollback()
        logger.exception(f"Ошибка синхронизации stock_prices: {e}")
        raise
    finally:
        cursor.close()
        close_db(conn)
