CREATE TEMPORARY TABLE tmp_warehouses (
    product_id_1c VARCHAR(36) NOT NULL,
    stock_id_1c VARCHAR(36) NOT NULL,
    edit_date DATE NULL,
    price DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    it_rrc TINYINT(1) NOT NULL DEFAULT 0,
    change_price_date DATE NULL,
    load_price_date DATE NULL,
    arch TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (product_id_1c, stock_id_1c)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
