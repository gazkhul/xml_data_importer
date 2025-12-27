from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TypeAlias
from xml.etree.ElementTree import ParseError

from importer.config import FILE_WAREHOUSES, SQL_CONFIG
from importer.logger import logger
from importer.report import ImportReport
from importer.sync import sync_data
from importer.xml_utils import iter_lines, parse_bool, parse_date, read_delete_flag


WarehouseKey: TypeAlias = tuple[str, str]
WarehouseRow: TypeAlias = tuple[
    str,          # product_id_1c
    str,          # stock_id_1c
    date | None,  # edit_date
    Decimal,      # price
    int,          # it_rrc
    date | None,  # change_price_date
    date | None,  # load_price_date
    int,          # arch
]

def _parse_warehouses(xml_path: Path, report: ImportReport) -> tuple[list[WarehouseRow], set[WarehouseKey]]:
    """
    Парсит XML-файл построчно, извлекает цены, даты и служебные флаги.
    Возвращает список подготовленных строк для БД и множество ключей (product_id, stock_id) для синхронизации.
    """
    rows: list[WarehouseRow] = []
    keys_in_file: set[WarehouseKey] = set()
    total_lines = 4 # Смещение на заголовок

    for line in iter_lines(xml_path):
        total_lines += 1

        try:
            product_id_1c = line.attrib.get("product_id_1c")
            stock_id_1c = line.attrib.get("stock_id_1c")

            if not product_id_1c:
                raise ValueError(f"Отсутствует обязательный атрибут 'product_id_1c' в строке #{total_lines}.")
            if not stock_id_1c:
                raise ValueError(f"Отсутствует обязательный атрибут 'stock_id_1c' в строке #{total_lines}.")

            raw_price = line.findtext("price") or "0.00"

            try:
                price = Decimal(raw_price)
            except InvalidOperation as e:
                raise ValueError(f"Некорректный формат цены: '{raw_price}'") from e

            edit_date = parse_date(line.findtext("edit_date"), total_lines, field_name="edit_date")
            load_price_date = parse_date(line.findtext("load_price_date"), total_lines, field_name="load_price_date")
            change_price_date = parse_date(line.findtext(
                "change_price_date"), total_lines, field_name="change_price_date"
            )

            it_rrc = parse_bool(line.findtext("it_rrc"), total_lines, field_name="it_rrc")
            arch = parse_bool(line.findtext("arch"), total_lines, field_name="arch")

            rows.append((
                product_id_1c,
                stock_id_1c,
                edit_date,
                price,
                it_rrc,
                change_price_date,
                load_price_date,
                arch,
            ))
            keys_in_file.add((product_id_1c, stock_id_1c))

        except ParseError as e:
            raise ValueError (f"Критическая ошибка структуры XML: {e}") from e
        except ValueError as e:
            report.add_row_error(total_lines, str(e))
            continue
        except Exception as e:
            report.add_row_error(total_lines, f"Неизвестная ошибка: {e}")
            continue

    report.set_rows_parsed(len(rows))
    return rows, keys_in_file

def import_warehouses(xml_path: Path, report: ImportReport) -> None:
    """
    Модуль для импорта данных из warehouses.xml.
    Обрабатывает файл со складскими остатками, ценами и флагами,
    выполняя вставку/обновление и удаление отсутствующих записей.
    """
    logger.info(f"Импорт {FILE_WAREHOUSES}: {xml_path}")

    delete_flag = read_delete_flag(xml_path)
    logger.info(f"Флаг 'delete': {delete_flag}")

    rows, keys_in_file = _parse_warehouses(xml_path, report)

    if not rows:
        logger.warning(f"В файле {xml_path.name} не найдено валидных данных для импорта.")
        return

    row_count = len(rows)
    logger.info(f"Готово к загрузке строк: {row_count}")

    conf = SQL_CONFIG["warehouses"]

    sync_data(
        rows=rows,
        keys=keys_in_file,
        upsert_sql_path=conf["upsert"],
        delete_flag=delete_flag,
        tmp_table_sql_path=conf["tmp_table"],
        delete_sql_path=conf["delete"],
        insert_tmp_key_sql=conf["insert_keys_stmt"]
    )

    logger.success(f"Импорт {FILE_WAREHOUSES} завершён.")
