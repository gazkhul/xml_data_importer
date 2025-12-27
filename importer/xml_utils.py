from datetime import date, datetime
from pathlib import Path
from typing import Any, Generator
from xml.etree.ElementTree import Element, iterparse


def get_xml_files(watch_dir: str | Path) -> list[Path]:
    """
    Возвращает список XML-файлов в указанной директории.
    """
    dir = Path(watch_dir)
    return list(dir.glob("*.xml"))

def parse_bool(text: str | None) -> int:
    """
    Преобразует текстовое значение в 0/1 по правилу «true -> 1, иначе -> 0».
    """
    if not text:
        return 0
    return 1 if text.strip().lower() == "true" else 0


def iter_lines(xml_path: Path) -> Generator[Element, Any, None]:
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
    for _event, elem in iterparse(xml_path, events=("end",)):
        if elem.tag == "delete":
            return (elem.text or "").strip().lower() == "true"
    return False

def parse_date(text: str | None) -> date | None:
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()
