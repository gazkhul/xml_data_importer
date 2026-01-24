UPDATE shop_product p
LEFT JOIN tmp_stock_prices_products t ON t.product_id_1c = p.id_1c
SET
    p.price = 0,
    p.base_price = 0,
    p.min_price = 0,
    p.max_price = 0,
    p.count = 0
WHERE t.product_id_1c IS NULL;
