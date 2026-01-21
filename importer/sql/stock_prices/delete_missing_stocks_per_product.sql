DELETE ps
FROM shop_product_stocks ps
JOIN shop_product p ON p.id = ps.product_id
JOIN shop_stock st ON st.id = ps.stock_id
JOIN tmp_stock_prices_products tp ON tp.product_id_1c = p.id_1c
LEFT JOIN tmp_stock_prices_stocks ts
  ON ts.product_id_1c = p.id_1c
  AND ts.stock_id_1c = st.id_1c
WHERE ts.stock_id_1c IS NULL;
