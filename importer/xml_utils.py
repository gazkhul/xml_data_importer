from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Iterator
from xml.etree.ElementTree import Element, ParseError, iterparse


def get_xml_files(watch_dir: str | Path) -> list[Path]:
    """
    Возвращает список XML-файлов в указанной директории.
    """
    dir = Path(watch_dir)
    return list(dir.glob("*.xml"))

def parse_bool(text: str | None, line: int, field_name: str = "unknown") -> int:
    """
    Парсит boolean из строки 'true'/'false' в 1/0.
    """
    if not text:
        raise ValueError(f"Отсутствует значение '{field_name}' в строке #{line}.")

    clean_text = text.strip().lower()

    if clean_text == "true":
        return 1
    if clean_text == "false":
        return 0
    raise ValueError(f"Некорректное значение '{field_name}' в строке #{line}: '{text}'. Ожидается true/false.")

def iter_lines(xml_path: Path) -> Iterator[Element]:
    """
    Потоковый итератор по элементам <line>.
    """
    try:
        context = iterparse(xml_path, events=("end",))
        for _, elem in context:
            if elem.tag == "line":
                yield elem
                elem.clear()
    except ParseError as e:
        raise ParseError(f"Критическая ошибка структуры XML: {e}") from e

def parse_datetime_to_date(text: str | None, line: int, field_name: str = "unknown") -> date | None:
    """
    Парсит ISO-datetime (YYYY-MM-DDTHH:MM:SS) и возвращает date.
    """
    if not text:
        return None

    clean_text = text.strip()

    if not clean_text:
        return None

    try:
        return datetime.fromisoformat(clean_text).date()
    except ValueError as e:
        raise ValueError(f"Некорректный формат даты в строке #{line} в поле '{field_name}': '{text}'."
                         "Ожидается ISO-datetime (YYYY-MM-DDTHH:MM:SS).") from e

def _read_flag(xml_path: Path, tag_name: str) -> bool:
    """
    Функция для чтения boolean-флага из XML.
    """
    context = iterparse(str(xml_path), events=("end",))
    for _, elem in context:
        if elem.tag == tag_name:
            val = (elem.text or "").strip().lower() == "true"
            elem.clear()
            return val
        elem.clear()
    return False

def read_delete_flag(xml_path: Path) -> bool:
    """
    True, если в XML встречается <delete>true</delete>, иначе False.
    """
    return _read_flag(xml_path, "delete")

def read_reset_flag(xml_path: Path) -> bool:
    """
    True, если в XML встречается <Reset>true</Reset>, иначе False.
    """
    return _read_flag(xml_path, "Reset")

def get_info_update_date(xml_path: Path) -> str | None:
    """
    Читает атрибут date из тега <info_update>.
    """
    context = iterparse(str(xml_path), events=("start",))
    for _, elem in context:
        if elem.tag == "info_update":
            date_val = elem.get("date")
            elem.clear()
            return date_val
    return None
