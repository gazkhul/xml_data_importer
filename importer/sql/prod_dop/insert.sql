INSERT INTO tbl_prod_dop (id_1c, it_ya)
SELECT tmp.id_1c, tmp.it_ya
FROM tmp_tbl_prod_dop tmp
LEFT JOIN tbl_prod_dop t ON t.id_1c = tmp.id_1c
WHERE t.id_1c IS NULL;
