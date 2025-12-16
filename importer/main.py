
from importer.database import close_db, connect_db
from importer.logger import logger
from importer.settings import WATCH_DIR
from importer.xml_utils import get_xml_files


def main():
    logger.info("Запуск обработчика XML-файлов.")

    if not WATCH_DIR:
        logger.error("Ошибка конфигурации: не задана директория (WATCH_DIR).")
        return

    xml_files = get_xml_files(WATCH_DIR)

    if not xml_files:
        logger.warning(f"XML-файлы отсутствуют в директории {WATCH_DIR}.")
        return

    logger.info(f"Обнаружено XML-файлов: {len(xml_files)}")

    try:
        conn = connect_db()
        for xml_file in xml_files:
            logger.info(xml_file.name)
    except Exception as e:
        logger.error(f"Ошибка при обработке XML-файлов: {e}")
    finally:
        if conn:
            close_db(conn)

    logger.info("Работа обработчика завершена.")


if __name__ == "__main__":
    main()
