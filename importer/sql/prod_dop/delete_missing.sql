DELETE t
FROM tbl_prod_dop t
LEFT JOIN tmp_tbl_prod_dop tmp ON tmp.id_1c = t.id_1c
WHERE tmp.id_1c IS NULL;
