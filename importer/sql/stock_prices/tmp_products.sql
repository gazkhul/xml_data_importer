CREATE TEMPORARY TABLE tmp_stock_prices_products (
  `product_id_1c` VARCHAR(36) NOT NULL,
  `price` DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
  `total_quantity` DECIMAL(15,3) NOT NULL DEFAULT 0.000,
  PRIMARY KEY (`product_id_1c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
