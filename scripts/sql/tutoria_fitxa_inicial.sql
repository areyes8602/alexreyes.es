-- Fitxa de l'alumne de la primera tutoria.
--
-- Executar un cop a la D1 `tutoria`:
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_fitxa_inicial.sql
--
-- Camps que omple l'alumne el primer dia i que no tenien columna pròpia. Els
-- que ja en tenien (nom, cognoms, naixement, telèfon, correu, extraescolars,
-- i el pare i la mare dins de `familia`) no es repeteixen aquí: el formulari
-- els torna a preguntar, però van a la seva columna de sempre.
--
-- OJO: D1 no té ALTER TABLE ... IF NOT EXISTS, i `wrangler d1 execute --file`
-- s'atura al primer error, NO segueix amb la resta. O sigui que si el fitxer
-- ja s'ha passat un cop, tornar-lo a executar peta a la primera línia
-- ("duplicate column name: ciutat") i no fa res més. No és cap desastre —no
-- hi ha res a mitges— però no serveix per completar una migració parcial:
-- per a això, executa a mà només les línies que falten.
--
-- Per saber si ja hi és:
--   npx wrangler d1 execute tutoria --remote --command \
--     "SELECT COUNT(*) FROM pragma_table_info('tutoria_alumnes') WHERE name='ciutat'"

ALTER TABLE tutoria_alumnes ADD COLUMN ciutat            TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN escola_primaria   TEXT;

-- Situació familiar: l'opció triada, amb qui viu i l'explicació lliure.
ALTER TABLE tutoria_alumnes ADD COLUMN situacio_familiar TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN situacio_amb_qui  TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN situacio_nota     TEXT;

ALTER TABLE tutoria_alumnes ADD COLUMN germans_nombre    TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN germans           TEXT;

-- Dada sensible: tractar-la com la resta de la fitxa, que no surt del gate.
ALTER TABLE tutoria_alumnes ADD COLUMN salut             TEXT;

ALTER TABLE tutoria_alumnes ADD COLUMN amics_classe      TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN amics_nivell      TEXT;

-- Com sóc jo
ALTER TABLE tutoria_alumnes ADD COLUMN mat_millor        TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN mat_pitjor        TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN virtuts           TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN millorar          TEXT;

-- Quan i com s'ha omplert, per saber qui falta.
ALTER TABLE tutoria_alumnes ADD COLUMN fitxa_inicial     TEXT;
