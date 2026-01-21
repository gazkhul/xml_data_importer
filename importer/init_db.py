import sys

from mariadb import Error as mariadb_error

from importer.config import (
    DB_APP_ALLOWED_HOST,
    SQL_DIR,
    STOCK_PRICES_TABLES,
    TABLE_PROD_DROP,
    TABLE_WAREHOUSES,
    admin_db_config,
    app_db_config,
)
from importer.db import close_db, connect_db
from importer.logger import logger


def _table_exists(admin_cursor, table_name: str) -> bool:
    admin_cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        """, (admin_db_config.database, table_name))
    return admin_cursor.fetchone()[0] > 0

def backup_existing_tables(admin_cursor, tables_to_backup: list) -> None:
    """
    Создает резервные копии существующих таблиц путем переименования.
    Например: warehouses -> warehouses_backup
    """

    for table_name in tables_to_backup:
        if not _table_exists(admin_cursor, table_name):
            logger.info(f"Таблица '{table_name}' не найдена, бэкап не требуется.")
            continue

        backup_name = f"{table_name}_backup"

        if _table_exists(admin_cursor, backup_name):
            logger.warning(
                f"Невозможно создать бэкап для '{table_name}': "
                f"таблица '{backup_name}' уже существует. Пропускаем."
            )
            continue

        try:
            logger.info(f"Создание бэкапа: {table_name} -> {backup_name}")
            admin_cursor.execute(f"RENAME TABLE {table_name} TO {backup_name}")
            logger.info(f"Бэкап таблицы '{table_name}' успешно создан.")
        except mariadb_error as e:
            logger.error(f"Ошибка при переименовании таблицы '{table_name}': {e}")
            raise

def apply_schema_from_file(admin_cursor) -> None:
    """
    Применяет схему из файла 001_create_tables.sql для создания таблиц.
    """
    schema_path = SQL_DIR / "001_create_tables.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Файл схемы не найден: {schema_path}")

    logger.info(f"Применение схемы БД из файла: {schema_path.name}")

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            statements = [s.strip() for s in sql_script.split(";") if s.strip()]

        for statement in statements:
            admin_cursor.execute(statement)

        logger.info(f"Схема '{schema_path.name}' успешно применена.")

    except (IOError, mariadb_error) as e:
        logger.error(f"Ошибка при применении схемы: {e}")
        raise

def configure_application_user(admin_cursor, tables: list) -> None:
    """
    Создает пользователя и выдает минимальные права.
    Ограничивает доступ только хостом 'localhost'.
    """
    app_db_username = app_db_config.user
    app_db_password = app_db_config.password
    app_db_name = app_db_config.database
    allowed_host = DB_APP_ALLOWED_HOST

    logger.info(f"Настройка прав для пользователя '{app_db_username}'@'{allowed_host}'")

    try:
        admin_cursor.execute(
            f"CREATE USER IF NOT EXISTS '{app_db_username}'@'{allowed_host}' "
            f"IDENTIFIED BY '{app_db_password}'"
        )

        for table in tables:
            admin_cursor.execute(
                f"GRANT SELECT, INSERT, UPDATE, DELETE "
                f"ON {app_db_name}.{table} "
                f"TO '{app_db_username}'@'{allowed_host}'"
            )

        admin_cursor.execute(
            f"GRANT CREATE TEMPORARY TABLES ON {app_db_name}.* "
            f"TO '{app_db_username}'@'{allowed_host}'"
        )

        admin_cursor.execute("FLUSH PRIVILEGES")
        logger.info(f"Пользователь '{app_db_username}'@'{allowed_host}' успешно настроен.")
    except mariadb_error as e:
        logger.error(f"Ошибка при настройке пользователя БД: {e}")
        raise

def main(init_schema: bool = False):
    """Основная функция инициализации базы данных."""
    logger.info("=== НАЧАЛО ИНИЦИАЛИЗАЦИИ БД ===")

    admin_connection = None

    try:
        admin_connection = connect_db(config=admin_db_config)
        admin_cursor = admin_connection.cursor()

        tables = [TABLE_PROD_DROP, TABLE_WAREHOUSES]

        if init_schema:
            backup_existing_tables(admin_cursor, tables)
            apply_schema_from_file(admin_cursor)

        tables_for_app_user = tables + STOCK_PRICES_TABLES
        configure_application_user(admin_cursor, tables_for_app_user)

        admin_connection.commit()
        logger.info("=== ИНИЦИАЛИЗАЦИЯ УСПЕШНО ЗАВЕРШЕНА ===")
    except Exception as e:
        if admin_connection:
            admin_connection.rollback()
        logger.error(f"Критическая ошибка инициализации: {e}")
        sys.exit(1)
    finally:
        if admin_connection:
            close_db(admin_connection)

if __name__ == "__main__":
    main(init_schema=False)
