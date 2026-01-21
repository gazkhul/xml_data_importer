DELETE ps
FROM shop_product_stocks ps
JOIN shop_product p ON p.id = ps.product_id
LEFT JOIN tmp_stock_prices_products tp ON tp.product_id_1c = p.id_1c
WHERE tp.product_id_1c IS NULL;
