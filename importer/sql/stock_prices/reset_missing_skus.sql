UPDATE shop_product_skus s
JOIN shop_product p ON p.id = s.product_id
LEFT JOIN tmp_stock_prices_products t ON t.product_id_1c = p.id_1c
SET
    s.price = 0,
    s.primary_price = 0,
    s.count = 0
WHERE t.product_id_1c IS NULL;
