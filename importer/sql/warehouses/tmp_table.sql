CREATE TEMPORARY TABLE tmp_warehouses_keys (
    product_id_1c VARCHAR(36) NOT NULL,
    stock_id_1c VARCHAR(36) NOT NULL,
    PRIMARY KEY (product_id_1c, stock_id_1c)
) ENGINE=InnoDB;
