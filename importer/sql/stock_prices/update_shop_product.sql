UPDATE shop_product p
JOIN tmp_stock_prices_products t ON t.product_id_1c = p.id_1c
SET
  p.base_price = t.price,
  p.min_price = t.price,
  p.max_price = t.price,
  p.count = t.total_quantity;
