
from importer.import_prod_dop import import_prod_dop
from importer.logger import logger
from importer.settings import WATCH_DIR
from importer.xml_utils import get_xml_files


def main():
    """
    Точка входа обработчика XML-файлов.

    Функция:
    - Проверяет, что задана директория для мониторинга (WATCH_DIR).
    - Получает список XML-файлов в директории.
    - Для известных файлов запускает соответствующий импорт.
    - После успешной обработки удаляет файл, чтобы не импортировать его повторно.
    - При ошибке логирует исключение и оставляет файл на месте для повторной попытки.

    """
    logger.info("Запуск обработчика XML-файлов.")

    if not WATCH_DIR:
        logger.error("Ошибка конфигурации: не задана директория (WATCH_DIR).")
        return

    xml_files = get_xml_files(WATCH_DIR)

    if not xml_files:
        logger.warning(f"XML-файлы отсутствуют в директории {WATCH_DIR}.")
        return

    for file_path in xml_files:
        try:
            logger.info(f"Обработка файла: {file_path.name}")

            if file_path.name == "prod_dop.xml":
                import_prod_dop(file_path)
            # elif file_path.name == "warehouses.xml":
            #     import_warehouses(file_path)
            else:
                logger.warning(f"Неизвестный XML-файл пропущен: {file_path.name}")
                continue

            file_path.unlink()
            logger.info(f"Файл обработан и удалён: {file_path.name}")

        except Exception:
            logger.exception(f"Не удалось обработать файл: {file_path.name}")
            # файл НЕ удаляем — останется для повторной попытки

    logger.info("Работа обработчика завершена.")


if __name__ == "__main__":
    main()
