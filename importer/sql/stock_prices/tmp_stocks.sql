CREATE TEMPORARY TABLE tmp_stock_prices_stocks (
  `product_id_1c` VARCHAR(36) NOT NULL,
  `stock_id_1c` VARCHAR(36) NOT NULL,
  `quantity` DECIMAL(15,3) NOT NULL DEFAULT 0.000,
  PRIMARY KEY (`product_id_1c`, `stock_id_1c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
