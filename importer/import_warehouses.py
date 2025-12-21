from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional, TypeAlias

from importer.db import close_db, connect_db
from importer.logger import logger
from importer.sql_loader import load_sql
from importer.xml_utils import iter_lines, parse_bool, parse_date, read_delete_flag


WarehouseKey: TypeAlias = tuple[str, str]
WarehouseRow: TypeAlias = tuple[
    str,           # product_id_1c
    str,           # stock_id_1c
    date | None,   # edit_date
    Decimal,       # price
    int,           # it_rrc
    date | None,   # change_price_date
    date | None,   # load_price_date
    int,           # arch
]


def _get_text(line, tag: str) -> Optional[str]:
    """
    Достаёт текст дочернего тега и чистит кавычки/пустые значения.
    """
    el = line.find(tag)
    if el is None or not el.text:
        return None
    return el.text.strip().strip('"')


def _parse_warehouses(xml_path: Path) -> tuple[list[WarehouseRow], set[WarehouseKey]]:
    """
    Разбирает warehouses.xml и возвращает (rows, keys_in_file) для UPSERT и snapshot-удаления.
    """
    rows: list[WarehouseRow] = []
    keys_in_file: set[WarehouseKey] = set()

    for line in iter_lines(xml_path):
        product_id_1c = line.attrib.get("product_id_1c")
        stock_id_1c = line.attrib.get("stock_id_1c")

        if not product_id_1c or not stock_id_1c:
            continue

        edit_date = parse_date(_get_text(line, "edit_date"))
        raw_price = _get_text(line, "price") or "0.00"

        try:
            price = Decimal(raw_price)
        except InvalidOperation:
            # Если цена битая — поставить 0.00.
            price = Decimal("0.00")

        it_rrc = parse_bool(_get_text(line, "it_rrc"))
        change_price_date = parse_date(_get_text(line, "change_price_date"))
        load_price_date = parse_date(_get_text(line, "load_price_date"))
        arch = parse_bool(_get_text(line, "arch"))

        rows.append(
            (
                product_id_1c,
                stock_id_1c,
                edit_date,
                price,
                it_rrc,
                change_price_date,
                load_price_date,
                arch,
            )
        )
        keys_in_file.add((product_id_1c, stock_id_1c))

    return rows, keys_in_file


def import_warehouses(xml_path: Path) -> None:
    """
    Импортирует данные из warehouses.xml в таблицу warehouses.

    Логика:
    - Пакетный UPSERT по UNIQUE(product_id_1c, stock_id_1c).
    - Удаление отсутствующих записей при <delete>true</delete>.
    - Одна транзакция на один файл: при ошибке rollback.
    """
    logger.info(f"Импорт warehouses.xml: {xml_path}")

    delete_flag = read_delete_flag(xml_path)
    logger.info(f"Флаг 'delete': {delete_flag}")

    rows, keys_in_file = _parse_warehouses(xml_path)

    if not rows:
        logger.warning(f"Данные в файле не найдены: {xml_path.name}")
        return

    logger.info("Разобрано строк: {}", len(rows))

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # --- UPSERT ---
        upsert_sql = load_sql("warehouses/upsert.sql")
        cursor.executemany(upsert_sql, rows)
        logger.info(f"Загружено записей в таблицу warehouses (вставка/обновление): {cursor.rowcount}")

        # --- DELETE ---
        if delete_flag:
            tmp_table_sql = load_sql("warehouses/tmp_table.sql")
            delete_sql = load_sql("warehouses/delete_missing.sql")
            insert_tmp_key_sql = (
                "INSERT INTO tmp_warehouses_keys (product_id_1c, stock_id_1c) VALUES (%s, %s)"
            )

            logger.info("Удаление записей, отсутствующих в XML-файле.")

            cursor.execute(tmp_table_sql)
            cursor.executemany(insert_tmp_key_sql, list(keys_in_file))

            cursor.execute(delete_sql)
            logger.info(f"Удалено строк: {cursor.rowcount}.")

        conn.commit()
        logger.success("Импорт warehouses.xml завершён: транзакция зафиксирована.")

    except Exception:
        conn.rollback()
        logger.exception("Ошибка импорта warehouses: выполнен откат транзакции (rollback).")
        raise

    finally:
        cursor.close()
        close_db(conn)
