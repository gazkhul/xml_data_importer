from __future__ import annotations

import json
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from importer.logger import logger


class ImportReport:
    """
    Класс для формирования и сохранения отчета о работе импортера.
    """
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.info_update_date: str | None = None
        self.status = "pending"
        self.started_at = self._get_current_time_iso()
        self.finished_at: str | None = None
        self.products_parsed = 0
        self.metrics: dict[str, int] = {}
        self.row_errors: list[dict[str, Any]] = []
        self.error: dict[str, Any] | None = None

    def set_products_parsed(self, count: int):
        """Устанавливает количество распарсенных товаров."""
        self.products_parsed = count

    def set_metrics(self, metrics: dict[str, int]):
        """Устанавливает специфичные метрики для каждого xml-файла."""
        self.metrics = metrics

    def set_info_update_date(self, date_str: str) -> None:
        """Устанавливает дату обновления из XML файла."""
        self.info_update_date = date_str

    def add_row_error(self, line_number: int, message: str) -> None:
        """
        Добавляет информацию об ошибке в конкретной строке.
        """
        error_entry = {
            "line": line_number,
            "message": message
        }
        self.row_errors.append(error_entry)
        logger.warning(f"Ошибка в строке {line_number} файла {self.file_name}: {message}")

    def set_success(self) -> None:
        """
        Фиксирует успешное завершение.
        """
        self.status = "success"
        self.finished_at = self._get_current_time_iso()
        if self.row_errors:
            self.status = "completed_with_errors"

    def set_failed(self, exc: Exception) -> None:
        """
        Фиксирует ошибку и сохраняет traceback.
        """
        self.status = "failed"
        self.finished_at = self._get_current_time_iso()
        self.error = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc()
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "info_update_date": self.info_update_date,
            "file": self.file_name,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "products_parsed": self.products_parsed,
            "metrics": self.metrics,
            "row_errors": self.row_errors,
            "error": self.error
        }

    def _get_current_time_iso(self) -> str:
        """
        Возвращает текущее время (UTC+3) в формате ISO 8601.
        """
        tz_plus_3 = timezone(timedelta(hours=3))
        return datetime.now(tz_plus_3).replace(microsecond=0).isoformat()

def load_existing_reports(report_path: Path) -> list[dict]:
    """Загружает существующие отчеты, если файл существует."""
    if not report_path.exists():
        return []
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def filter_reports_by_retention(reports: list[dict], hours: int = 24) -> list[dict]:
    """Оставляет отчеты только за последние N часов (или сутки)."""
    cutoff_time = datetime.now().astimezone() - timedelta(hours=hours)
    valid_reports = []

    for rep in reports:
        try:
            finished_at_str = rep.get("finished_at")
            if not finished_at_str:
                continue

            rep_time = datetime.fromisoformat(finished_at_str)

            if rep_time.tzinfo is None:
                 rep_time = rep_time.astimezone()

            if rep_time > cutoff_time:
                valid_reports.append(rep)
        except ValueError:
            continue

    return valid_reports
