INSERT INTO shop_product_stocks (sku_id, stock_id, product_id, count)
SELECT
    s.id as sku_id,
    st.id as stock_id,
    p.id as product_id,
    ts.quantity
FROM tmp_stock_prices_stocks ts
JOIN shop_product p ON p.id_1c = ts.product_id_1c
JOIN shop_product_skus s ON s.id_1c = ts.product_id_1c
JOIN shop_stock st ON st.id_1c = ts.stock_id_1c
ON DUPLICATE KEY UPDATE count = VALUES(count);
