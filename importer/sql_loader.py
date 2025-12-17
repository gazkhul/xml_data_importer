from importer.settings import SQL_DIR


def load_sql(relative_path: str) -> str:
    """
    Загружает SQL из <PROJECT_ROOT>/importer/sql/**/*
    """
    path = SQL_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"SQL-файл не найден: {path}")
    return path.read_text(encoding="utf-8")
