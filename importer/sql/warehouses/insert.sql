INSERT INTO warehouses (
    product_id_1c, stock_id_1c, edit_date, price, it_rrc,
    change_price_date, load_price_date, arch
)
SELECT
    tmp.product_id_1c, tmp.stock_id_1c, tmp.edit_date, tmp.price, tmp.it_rrc,
    tmp.change_price_date, tmp.load_price_date, tmp.arch
FROM tmp_warehouses tmp
LEFT JOIN warehouses t
  ON t.product_id_1c = tmp.product_id_1c AND t.stock_id_1c = tmp.stock_id_1c
WHERE t.product_id_1c IS NULL;
