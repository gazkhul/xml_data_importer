from pathlib import Path
from xml.etree.ElementTree import ParseError

from typing_extensions import TypeAlias

from importer.config import FILE_PROD_DOP, SQL_CONFIG
from importer.logger import logger
from importer.report import ImportReport
from importer.sync import sync_data
from importer.xml_utils import iter_lines, parse_bool, read_delete_flag


ProdDopRow: TypeAlias = tuple[str, int]


def _parse_prod_dop(xml_path: Path, report: ImportReport) -> list[ProdDopRow]:
    """
    Парсит prod_dop.xml.
    Ожидается <line> с атрибутами id_1c и it_ya.
    """
    rows: list[ProdDopRow] = []
    total_lines = 4  # смещение на заголовок XML

    for line in iter_lines(xml_path):
        total_lines += 1

        try:
            id_1c = line.attrib.get("id_1c")
            if not id_1c:
                raise ValueError(f"Отсутствует id_1c в строке #{total_lines}.")

            it_ya = parse_bool(
                line.attrib.get("it_ya"),
                total_lines,
                "it_ya",
            )

            rows.append((id_1c, it_ya))

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


def import_prod_dop(xml_path: Path, report: ImportReport) -> None:
    """
    Импорт данных из prod_dop.xml.
    """
    logger.info(f"Импорт файла '{FILE_PROD_DOP}': {xml_path}")

    delete_flag = read_delete_flag(xml_path)
    logger.info(f"Параметры импорта: delete={delete_flag}")

    rows = _parse_prod_dop(xml_path, report)

    if not rows:
        logger.warning(f"В файле {xml_path.name} нет валидных строк для импорта.")
        return

    logger.info(f"Подготовлено строк к загрузке: count={len(rows)}")

    conf = SQL_CONFIG["tbl_prod_dop"]

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

    logger.success(f"Импорт '{FILE_PROD_DOP}' завершён.")
