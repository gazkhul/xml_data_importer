DELETE FROM shop_product_stocks_log
WHERE datetime < DATE_SUB(NOW(), INTERVAL 1 YEAR);
