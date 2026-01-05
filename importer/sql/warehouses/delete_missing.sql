DELETE t
FROM warehouses t
LEFT JOIN tmp_warehouses tmp
  ON tmp.product_id_1c = t.product_id_1c AND tmp.stock_id_1c = t.stock_id_1c
WHERE tmp.product_id_1c IS NULL;
