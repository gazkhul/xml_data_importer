CREATE TABLE tbl_prod_dop (
    id_1c VARCHAR(36) NOT NULL,
    it_ya TINYINT(1) DEFAULT 0,
    UNIQUE KEY uniq_tbl_prod_dop_id_1c (id_1c)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE warehouses (
    stock_id_1c VARCHAR(36) NOT NULL,
    product_id_1c VARCHAR(36) NOT NULL,
    edit_date DATE DEFAULT NULL,
    price DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    it_rrc TINYINT(1) DEFAULT NULL,
    change_price_date DATE DEFAULT NULL,
    load_price_date DATE DEFAULT NULL,
    arch TINYINT(1) DEFAULT NULL,
    change_rrc_date DATE DEFAULT NULL,
    UNIQUE KEY uniq_warehouses_product_id_1c_stock_id_1c (product_id_1c, stock_id_1c)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
