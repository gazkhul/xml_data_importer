-- ВАЖНО:
-- it_ya гарантированно NOT NULL.
-- NULL отсекается на этапе парсинга XML (ValueError → строка пропускается).
-- Поэтому для этого поля используется != вместо NULL-safe (<=>).
-- При изменении схемы или правил валидации UPDATE необходимо пересмотреть.
UPDATE tbl_prod_dop t
JOIN tmp_tbl_prod_dop tmp ON t.id_1c = tmp.id_1c
SET t.it_ya = tmp.it_ya
WHERE t.it_ya != tmp.it_ya;
