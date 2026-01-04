CREATE TEMPORARY TABLE tmp_warehouses (
    product_id_1c VARCHAR(36) NOT NULL,
    stock_id_1c VARCHAR(36) NOT NULL,
    edit_date DATE,
    price DECIMAL(15,2) NOT NULL,
    it_rrc TINYINT(1),
    change_price_date DATE,
    load_price_date DATE,
    arch TINYINT(1),
    PRIMARY KEY (product_id_1c, stock_id_1c)
) ENGINE=InnoDB;
