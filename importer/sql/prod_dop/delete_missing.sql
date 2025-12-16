DELETE t
FROM tbl_prod_dop t
LEFT JOIN tmp_prod_dop_ids x ON x.id_1c = t.id_1c
WHERE x.id_1c IS NULL;
