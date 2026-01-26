import json
import shutil
from datetime import datetime

from importer.config import (
    DATE_FORMAT_LOG,
    FAILED_DIR,
    FILE_PROD_DOP,
    FILE_STOCK_PRICES,
    FILE_WAREHOUSES,
    IMPORT_DIR,
    REPORT_DIR,
    REPORT_FILE_NAME,
    UNKNOWN_DIR,
)
from importer.db import check_db_connection
from importer.import_prod_dop import import_prod_dop
from importer.import_stock_prices import import_stock_prices
from importer.import_warehouses import import_warehouses
from importer.logger import logger
from importer.report import ImportReport, filter_reports_by_retention, load_existing_reports
from importer.xml_utils import get_info_update_date, get_xml_files


def main():
    """
    Точка входа обработчика XML-файлов.
    Использует ImportReport для генерации JSON-отчета.
    """
    logger.info("Запуск обработчика XML-файлов.")

    xml_files = get_xml_files(IMPORT_DIR)
    if not xml_files:
        logger.warning(f"XML-файлы отсутствуют в директории {IMPORT_DIR}.")
        return

    if not check_db_connection():
        logger.critical("Нет связи с БД. Синхронизация таблиц остановлена.")
        return

    # all_reports = []
    report_file_path = REPORT_DIR / REPORT_FILE_NAME
    history_reports = load_existing_reports(report_file_path)

    for file_path in xml_files:
        report = ImportReport(file_path.name)

        xml_date = get_info_update_date(file_path)
        if xml_date:
            report.set_info_update_date(xml_date)

        try:
            logger.info(f"Начат разбор файла: '{file_path.name}'")

            if file_path.name not in [FILE_PROD_DOP, FILE_WAREHOUSES, FILE_STOCK_PRICES]:
                logger.warning(f"Неизвестный XML-файл: '{file_path.name}'")
                dest_path = UNKNOWN_DIR / file_path.name
                shutil.move(str(file_path), str(dest_path))
                logger.warning(f"Файл перемещен в unknown: {dest_path}")
                continue

            if file_path.name == FILE_PROD_DOP:
                import_prod_dop(file_path, report)
            elif file_path.name == FILE_WAREHOUSES:
                import_warehouses(file_path, report)
            elif file_path.name == FILE_STOCK_PRICES:
                import_stock_prices(file_path, report)

            report.set_success()

            if report.status == "success":
                file_path.unlink()
                logger.info(f"Файл синхронизирован и удален: '{file_path.name}'")
            else:
                logger.warning(f"Файл синхронизирован с ошибками ({report.status}). Перемещение в failed.")
                raise RuntimeError(f"Импорт завершен со статусом: {report.status}")

        except Exception as e:
            logger.warning(f"Файл '{file_path.name}' требует проверки. Статус: {report.status}")
            if report.status == "pending":
                report.set_failed(e)

            try:
                timestamp = datetime.now().strftime(DATE_FORMAT_LOG)
                new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
                dest_path = FAILED_DIR / new_name
                shutil.move(str(file_path), str(dest_path))
                logger.warning(f"Файл перемещен в failed: {dest_path}")
            except OSError as move_err:
                logger.error(f"Не удалось переместить файл '{file_path.name}': {move_err}")

        # all_reports.append(report.to_dict())
        history_reports.append(report.to_dict())

    history_reports = filter_reports_by_retention(history_reports, hours=24)

    # if all_reports:
    #     try:
    #         with open(report_file_path, "w", encoding="utf-8") as f:
    #             json.dump(all_reports, f, ensure_ascii=False, indent=2)
    #         logger.info(f"Отчет обновлен: {report_file_path}")
    #     except Exception as e:
    #         logger.exception(f"Не удалось сохранить файл отчета. Ошибка: {e}")

    try:
        with open(report_file_path, "w", encoding="utf-8") as f:
            json.dump(history_reports, f, ensure_ascii=False, indent=2)
        logger.info(f"Отчет сохранен: {report_file_path}")
    except Exception as e:
        logger.exception(f"Ошибка при сохранении отчета: {e}")

    logger.info("Работа обработчика завершена.")


if __name__ == "__main__":
    main()
