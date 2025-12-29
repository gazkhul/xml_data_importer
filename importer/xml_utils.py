from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Iterator
from xml.etree.ElementTree import Element, iterparse

from importer.config import DATE_FORMAT_XML


def get_xml_files(watch_dir: str | Path) -> list[Path]:
    """
    Возвращает список XML-файлов в указанной директории.
    """
    dir = Path(watch_dir)
    return list(dir.glob("*.xml"))

def parse_bool(text: str | None, line: int, field_name: str = "unknown") -> int:
    """
    Преобразует текстовое значение в 0/1 по правилу true -> 1, false -> 0».
    Выбрасывает ValueError, если значение не 'true' и не 'false'.
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
    Итератор по элементам <line> в XML-файле.
    Реализован через потоковый парсинг (iterparse), чтобы не загружать весь XML в память.
    После выдачи элемента выполняется elem.clear() для снижения потребления памяти.
    """
    context = iterparse(xml_path, events=("end",))
    for _event, elem in context:
        if elem.tag == "line":
            yield elem
            elem.clear()

def read_delete_flag(xml_path: Path) -> bool:
    """
    True, если в XML встречается <delete>true</delete>, иначе False.
    """
    context = iterparse(str(xml_path), events=("end",))
    for _event, elem in context:
        if elem.tag == "delete":
            val = (elem.text or "").strip().lower() == "true"
            elem.clear()
            return val
        elem.clear()
    return False

def parse_date(text: str | None, line: int, field_name: str = "unknown") -> date | None:
    """
    Парсит дату в формате YYYY-MM-DD.
    Возвращает объект date или None (если текст пустой).
    Выбрасывает ValueError, если формат некорректен.
    """
    if not text:
        return None

    clean_text = text.strip()

    if not clean_text:
        return None

    try:
        return datetime.strptime(clean_text, DATE_FORMAT_XML).date()
    except ValueError as e:
        msg = f"Некорректный формат даты в строке #{line} в поле '{field_name}': '{text}'. Ожидается YYYY-MM-DD."
        raise ValueError(msg) from e
