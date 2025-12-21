INSERT INTO warehouses (
    product_id_1c,
    stock_id_1c,
    edit_date,
    price,
    it_rrc,
    change_price_date,
    load_price_date,
    arch
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    edit_date = VALUES(edit_date),
    price = VALUES(price),
    it_rrc = VALUES(it_rrc),
    change_price_date = VALUES(change_price_date),
    load_price_date = VALUES(load_price_date),
    arch = VALUES(arch);
