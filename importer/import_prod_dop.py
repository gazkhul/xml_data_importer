from pathlib import Path
from xml.etree.ElementTree import ParseError

from typing_extensions import TypeAlias

from importer.config import FILE_PROD_DOP, SQL_CONFIG
from importer.logger import logger
from importer.report import ImportReport
from importer.sync import sync_data
from importer.xml_utils import iter_lines, parse_bool, read_delete_flag


ProdDopRow: TypeAlias = tuple[str, int]

def _parse_prod_dop(xml_path: Path, report: ImportReport) -> tuple[list[ProdDopRow], set[tuple[str]]]:
    """
    Парсит XML-файл построчно, валидирует данные и собирает статистику ошибок.
    Возвращает список подготовленных строк для БД и множество ключей (id_1c) для синхронизации.
    """
    rows: list[ProdDopRow] = []
    keys_in_file: set[tuple[str]] = set()
    total_lines = 4 # Смещение на заголовок

    for line in iter_lines(xml_path):
        total_lines += 1

        try:
            id_1c = line.attrib.get("id_1c")

            if not id_1c:
                raise ValueError(f"Отсутствует id_1c в строке #{total_lines}.")

            it_ya = parse_bool(line.findtext("it_ya"), total_lines, field_name="it_ya")
            rows.append((id_1c, it_ya))
            keys_in_file.add((id_1c,))

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

def import_prod_dop(xml_path: Path, report: ImportReport) -> None:
    """
    Модуль для импорта данных из prod_dop.xml.
    Обрабатывает файл, извлекает ID продукта и флаг (it_ya),
    после чего обновляет основную таблицу и удаляет устаревшие записи.
    """
    logger.info(f"Импорт {FILE_PROD_DOP}: {xml_path}")

    delete_flag: bool = read_delete_flag(xml_path)
    logger.info(f"Флаг 'delete': {delete_flag}")

    rows, keys_in_file = _parse_prod_dop(xml_path, report)

    if not rows:
        logger.warning(f"В файле {xml_path.name} не найдено валидных данных для импорта.")
        return

    row_count = len(rows)
    logger.info(f"Готово к загрузке строк: {row_count}")

    conf = SQL_CONFIG["prod_dop"]

    sync_data(
        rows=rows,
        keys=keys_in_file,
        upsert_sql_path=conf["upsert"],
        delete_flag=delete_flag,
        tmp_table_sql_path=conf["tmp_table"],
        delete_sql_path=conf["delete"],
        insert_tmp_key_sql=conf["insert_keys_stmt"]
    )

    logger.success(f"Импорт {FILE_PROD_DOP} завершён.")
