from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple

from importer.config import FILE_STOCK_PRICES
from importer.logger import logger
from importer.report import ImportReport
from importer.sync import sync_stock_prices
from importer.xml_utils import iter_lines, read_reset_flag


@dataclass
class ProductRow:
    product_id_1c: str
    price: Decimal
    total_quantity: Decimal

@dataclass
class StockItem:
    product_id_1c: str
    stock_id_1c: str
    quantity: Decimal

def _parse_stock_prices(xml_path: Path, report: ImportReport) -> Tuple[List[ProductRow], List[StockItem]]:
    """
    Парсит stock_prices.xml.
    """
    products_data: List[ProductRow] = []
    stocks_data: List[StockItem] = []

    for i, elem in enumerate(iter_lines(xml_path), start=6):
        if elem.tag != "line":
            continue

        try:
            product_id_1c = elem.get("product_id_1c")
            if not product_id_1c:
                elem.clear()
                raise ValueError(f"Отсутствует обязательный атрибут 'product_id_1c' в строке #{i}.")


            price_elem = elem.find("price")
            price = Decimal(
                price_elem.text) if (price_elem is not None and price_elem.text) else Decimal("0")

            total_qty_elem = elem.find("total_quantity")
            total_qty = Decimal(
                total_qty_elem.text) if (total_qty_elem is not None and total_qty_elem.text) else Decimal("0")

            stocks_elem = elem.find("stocks")

            if stocks_elem is not None:
                for stock in stocks_elem.findall("stock"):
                    stock_id_1c = stock.get("stock_id_1c")
                    qty_val = stock.get("Quantity")

                    if stock_id_1c and qty_val:
                        try:
                            stocks_data.append(StockItem(
                                product_id_1c=product_id_1c,
                                stock_id_1c=stock_id_1c,
                                quantity=Decimal(qty_val)
                            ))
                        except ValueError as e:
                            raise ValueError(f"Ошибка данных склада {stock_id_1c} в строке #{i}") from e

            products_data.append(ProductRow(
                product_id_1c=product_id_1c,
                price=price,
                total_quantity=total_qty
            ))

        except ValueError as e:
            report.add_row_error(i, str(e))
            continue
        except Exception as e:
            report.add_row_error(i, f"Неизвестная ошибка парсинга: {e}")
        finally:
            elem.clear()

    return products_data, stocks_data


def import_stock_prices(xml_path: Path, report: ImportReport) -> None:
    """
    Основная точка входа для импорта stock_prices.xml.
    """
    logger.info(f"Начат импорт файла '{FILE_STOCK_PRICES}': {xml_path}")

    try:
        is_reset = read_reset_flag(xml_path)
        logger.info(f"Параметры импорта: reset={is_reset}")

        products_rows, stocks_rows = _parse_stock_prices(xml_path, report)

        if not products_rows:
            logger.warning(f"В файле {xml_path.name} нет валидных данных для импорта.")
            return

        report.set_products_parsed(len(products_rows))

        logger.info(f"Подготовлено к загрузке: товаров={len(products_rows)}, записей складов={len(stocks_rows)}")

        sync_results = sync_stock_prices(
            products_data=products_rows,
            stocks_data=stocks_rows,
            is_reset=is_reset
        )

        report.set_metrics({
            "products_updated": sync_results["products_updated"],
            "skus_updated": sync_results["skus_updated"],
            "stocks_upserted": sync_results["stocks_upserted"],
            "products_reset": sync_results["products_reset"],
            "skus_reset": sync_results["skus_reset"],
            "stocks_deleted": sync_results["stocks_deleted"]
        })

        report.set_success()
        logger.success(f"Импорт '{FILE_STOCK_PRICES}' успешно завершён.")

    except Exception as e:
        logger.exception(f"Критическая ошибка при импорте '{FILE_STOCK_PRICES}': {e}")
        report.set_failed(e)
        raise
