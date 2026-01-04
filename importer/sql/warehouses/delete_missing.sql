DELETE t
FROM warehouses t
LEFT JOIN tmp_warehouses x
  ON x.product_id_1c = t.product_id_1c
 AND x.stock_id_1c = t.stock_id_1c
WHERE x.product_id_1c IS NULL;
