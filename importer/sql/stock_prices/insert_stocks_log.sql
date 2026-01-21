INSERT INTO shop_product_stocks_log
(product_id, sku_id, stock_id, stock_name, before_count, after_count, diff_count, type, description, datetime)
SELECT
  p.id,
  p.sku_id,
  st.id,
  st.name,
  COALESCE(ps.count, 0) AS before_count,
  ts.quantity AS after_count,
  ts.quantity - COALESCE(ps.count, 0) AS diff_count,
  'import' AS type,
  'Update from XML' AS description,
  NOW() AS datetime
FROM tmp_stock_prices_stocks ts
JOIN shop_product p ON p.id_1c = ts.product_id_1c
JOIN shop_stock st ON st.id_1c = ts.stock_id_1c
LEFT JOIN shop_product_stocks ps
  ON ps.product_id = p.id AND ps.sku_id = p.sku_id AND ps.stock_id = st.id
WHERE 
  COALESCE(ps.count, 0) <> ts.quantity;
