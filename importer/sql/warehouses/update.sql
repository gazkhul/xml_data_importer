UPDATE warehouses t
JOIN tmp_warehouses tmp
  ON t.product_id_1c = tmp.product_id_1c AND t.stock_id_1c = tmp.stock_id_1c
SET
    t.edit_date = tmp.edit_date,
    t.price = tmp.price,
    t.it_rrc = tmp.it_rrc,
    t.change_price_date = tmp.change_price_date,
    t.load_price_date = tmp.load_price_date,
    t.arch = tmp.arch
WHERE NOT (
    t.edit_date <=> tmp.edit_date AND
    t.price <=> tmp.price AND
    t.it_rrc <=> tmp.it_rrc AND
    t.change_price_date <=> tmp.change_price_date AND
    t.load_price_date <=> tmp.load_price_date AND
    t.arch <=> tmp.arch
);
