UPDATE shop_product_skus s
JOIN tmp_stock_prices_products t ON t.product_id_1c = s.id_1c
JOIN shop_product p ON p.id = s.product_id
SET
    s.price = t.price,
    s.primary_price = t.price,
    s.count = t.total_quantity;
