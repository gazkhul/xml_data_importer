UPDATE tbl_prod_dop t
JOIN tmp_tbl_prod_dop tmp ON t.id_1c = tmp.id_1c
SET t.it_ya = tmp.it_ya
WHERE NOT (t.it_ya <=> tmp.it_ya);
