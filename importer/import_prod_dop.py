from pathlib import Path
from typing import TypeAlias

from importer.db import close_db, connect_db
from importer.logger import logger
from importer.sql_loader import load_sql
from importer.xml_utils import iter_lines, parse_bool, read_delete_flag


ProdDopRow: TypeAlias = tuple[str, int]

def _parse_prod_dop(xml_path: Path) -> tuple[list[ProdDopRow], set[str]]:
    """
    Разбирает prod_dop.xml и подготавливает данные для пакетной записи в БД.
    Возвращает кортеж (rows, ids_in_file), где:
    - rows: список кортежей (id_1c, it_ya) для executemany().
    - ids_in_file: множество всех id_1c, встретившихся в файле (для snapshot-удаления).
    """
    rows: list[ProdDopRow] = []
    ids_in_file: set[str] = set()

    for line in iter_lines(xml_path):
        id_1c = line.attrib.get("id_1c")
        if not id_1c:
            continue

        it_ya_elem = line.find("it_ya")
        it_ya = parse_bool(it_ya_elem.text if it_ya_elem is not None else None)

        rows.append((id_1c, it_ya))
        ids_in_file.add(id_1c)

    return rows, ids_in_file

def import_prod_dop(xml_path: Path) -> None:
    """
    Импорт данных из prod_dop.xml в таблицу tbl_prod_dop.

    Логика:
    - Пакетный UPSERT по уникальному ключу UNIQUE(id_1c).
    - Удаление отсутствующих записей при <delete>true</delete>.
    - Одна транзакция на один файл: при ошибке rollback.
    """
    logger.info(f"Импорт prod_dop.xml: {xml_path}")

    delete_flag: bool = read_delete_flag(xml_path)
    logger.info(f"Флаг 'delete': {delete_flag}")

    rows, ids_in_file = _parse_prod_dop(xml_path)

    if not rows:
        logger.warning(f"Данные в файле не найдены: {xml_path.name}")
        return

    logger.info(f"Разобрано строк: {len(rows)}")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # --- UPSERT ---
        upsert_sql = load_sql("prod_dop/upsert.sql")
        cursor.executemany(upsert_sql, rows)
        logger.info(f"Загружено записей в таблицу tbl_prod_dop (вставка/обновление): {cursor.rowcount}")

        # --- DELETE ---
        if delete_flag:
            tmp_table_sql = load_sql("prod_dop/tmp_table.sql")
            delete_sql = load_sql("prod_dop/delete_missing.sql")

            logger.info("Удаление записей, отсутствующих в XML-файле.")

            cursor.execute(tmp_table_sql)

            cursor.executemany(
                "INSERT INTO tmp_prod_dop_ids (id_1c) VALUES (%s)",
                [(i,) for i in ids_in_file],
            )

            cursor.execute(delete_sql)
            logger.info(f"Удалено строк: {cursor.rowcount}.")

        conn.commit()
        logger.success("Импорт prod_dop.xml завершён: транзакция зафиксирована.")

    except Exception:
        conn.rollback()
        logger.exception("Ошибка импорта prod_dop: выполнен откат транзакции (rollback).")
        raise

    finally:
        cursor.close()
        close_db(conn)
