INSERT INTO tbl_prod_dop (id_1c, it_ya)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE
    it_ya = VALUES(it_ya);
