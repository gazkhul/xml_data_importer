-- ВАЖНО:
-- price, it_rrc, arch гарантированно NOT NULL.
-- NULL отсекается на этапе парсинга XML (ValueError → строка пропускается).
-- Поэтому для этих полей используется != вместо NULL-safe (<=>).
-- При изменении схемы или правил валидации UPDATE необходимо пересмотреть.
UPDATE warehouses t
JOIN tmp_warehouses tmp
  ON t.product_id_1c = tmp.product_id_1c AND t.stock_id_1c = tmp.stock_id_1c
SET
    t.edit_date = tmp.edit_date,
    t.price = tmp.price,
    t.it_rrc = tmp.it_rrc,
    t.change_price_date = tmp.change_price_date,
    t.load_price_date = tmp.load_price_date,
    t.arch = tmp.arch
WHERE
    t.price != tmp.price OR
    t.it_rrc != tmp.it_rrc OR
    t.arch != tmp.arch OR
    NOT (t.edit_date <=> tmp.edit_date) OR
    NOT (t.change_price_date <=> tmp.change_price_date) OR
    NOT (t.load_price_date <=> tmp.load_price_date);
