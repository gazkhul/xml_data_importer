from datetime import date
from decimal import Decimal, InvalidOperation
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


WarehouseRow: TypeAlias = tuple[
    str,             # product_id_1c
    str,             # stock_id_1c
    Optional[date],  # edit_date
    Decimal,         # price
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
                price = Decimal(raw_price)
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

        except ParseError as e:
            raise ValueError(f"Критическая ошибка структуры XML: {e}") from e
        except ValueError as e:
            report.add_row_error(total_lines, str(e))
            continue
        except Exception as e:
            report.add_row_error(total_lines, f"Неизвестная ошибка парсинга: {e}")
            continue

    return rows


def import_warehouses(xml_path: Path, report: ImportReport) -> None:
    """
    Импорт данных из warehouses.xml.
    """
    logger.info(f"Импорт файла '{FILE_WAREHOUSES}': {xml_path}")

    is_delete = read_delete_flag(xml_path)
    logger.info(f"Параметры импорта: delete={is_delete}")

    rows = _parse_warehouses(xml_path, report)

    report.set_products_parsed(len(rows))

    if not rows:
        logger.warning(f"В файле {xml_path.name} нет валидных строк для импорта.")
        return

    logger.info(f"Подготовлено строк к загрузке: count={len(rows)}")

    conf = SQL_CONFIG["warehouses"]

    sync_results = sync_data(
        rows=rows,
        is_delete=is_delete,
        target_table=conf["target_table"],
        columns_list=conf["columns_list"],
        tmp_table_sql_path=conf["tmp_table"],
        insert_sql_path=conf["insert"],
        update_sql_path=conf["update"],
        delete_sql_path=conf["delete"],
    )

    report.set_metrics({
        "db_inserted": sync_results["db_inserted"],
        "db_updated": sync_results["db_updated"],
        "db_deleted": sync_results["db_deleted"]
    })

    logger.success(f"Импорт '{FILE_WAREHOUSES}' завершён.")
