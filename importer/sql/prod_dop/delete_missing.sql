DELETE t
FROM tbl_prod_dop t
LEFT JOIN tmp_tbl_prod_dop x ON x.id_1c = t.id_1c
WHERE x.id_1c IS NULL;
