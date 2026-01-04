from datetime import date
from decimal import InvalidOperation
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import ParseError

from typing_extensions import TypeAlias

from importer.config import FILE_WAREHOUSES, SQL_CONFIG
from importer.logger import logger
from importer.report import ImportReport
from importer.sync import sync_data
from importer.xml_utils import (
    iter_lines,
    parse_bool,
    parse_datetime_to_date,
    read_delete_flag,
)


# WarehouseKey: TypeAlias = tuple[str, str]

WarehouseRow: TypeAlias = tuple[
    str,             # product_id_1c
    str,             # stock_id_1c
    Optional[date],  # edit_date
    int,             # price
    int,             # it_rrc
    Optional[date],  # change_price_date
    Optional[date],  # load_price_date
    int,             # arch
]


def _parse_warehouses(xml_path: Path, report: ImportReport) -> list[WarehouseRow]:
    """
    Парсит warehouses.xml.
    """
    rows: list[WarehouseRow] = []
    # keys_in_file: set[WarehouseKey] = set()
    total_lines = 4  # смещение на заголовок XML

    for line in iter_lines(xml_path):
        total_lines += 1

        try:
            product_id_1c = line.attrib.get("product_id_1c")
            stock_id_1c = line.attrib.get("stock_id_1c")

            if not product_id_1c:
                raise ValueError(f"Отсутствует обязательный атрибут 'product_id_1c' в строке #{total_lines}.")
            if not stock_id_1c:
                raise ValueError(f"Отсутствует обязательный атрибут 'stock_id_1c' в строке #{total_lines}.")

            raw_price = line.attrib.get("price")
            if raw_price is None:
                raise ValueError(f"Отсутствует атрибут 'price' в строке #{total_lines}.")

            try:
                price = int(raw_price)
            except InvalidOperation as e:
                raise ValueError(f"Некорректное значение 'price': '{raw_price}'.") from e

            edit_date = parse_datetime_to_date(
                line.attrib.get("edit_date"),
                total_lines,
                "edit_date",
            )

            load_price_date = parse_datetime_to_date(
                line.attrib.get("load_price_date"),
                total_lines,
                "load_price_date",
            )

            change_price_date = parse_datetime_to_date(
                line.attrib.get("change_price_date"),
                total_lines,
                "change_price_date",
            )

            it_rrc = parse_bool(
                line.attrib.get("it_rrc"),
                total_lines,
                "it_rrc",
            )

            arch = parse_bool(
                line.attrib.get("arch"),
                total_lines,
                "arch",
            )

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

            # keys_in_file.add((product_id_1c, stock_id_1c))

        except ParseError as e:
            raise ValueError(f"Критическая ошибка структуры XML: {e}") from e
        except ValueError as e:
            report.add_row_error(total_lines, str(e))
            continue
        except Exception as e:
            report.add_row_error(total_lines, f"Неизвестная ошибка: {e}")
            continue

    report.set_rows_parsed(len(rows))
    return rows


def import_warehouses(xml_path: Path, report: ImportReport) -> None:
    """
    Импорт данных из warehouses.xml.
    """
    logger.info(f"Импорт файла '{FILE_WAREHOUSES}': {xml_path}")

    delete_flag = read_delete_flag(xml_path)
    logger.info(f"Параметры импорта: delete={delete_flag}")

    rows = _parse_warehouses(xml_path, report)

    if not rows:
        logger.warning(f"В файле {xml_path.name} нет валидных строк для импорта.")
        return

    logger.info(f"Подготовлено строк к загрузке: count={len(rows)}")

    conf = SQL_CONFIG["warehouses"]

    sync_results = sync_data(
        rows=rows,
        delete_flag=delete_flag,
        target_table=conf["target_table"],
        columns_list=conf["columns_list"],
        tmp_table_sql_path=conf["tmp_table"],
        insert_sql_path=conf["insert"],
        update_sql_path=conf["update"],
        delete_sql_path=conf["delete"],
    )

    report.set_sync_results(
        rows_inserted=sync_results["rows_inserted"],
        rows_updated=sync_results["rows_updated"],
        rows_deleted=sync_results["rows_deleted"],
    )

    logger.success(f"Импорт {FILE_WAREHOUSES} завершён.")
