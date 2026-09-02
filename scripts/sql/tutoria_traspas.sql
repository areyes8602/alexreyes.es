-- Traspàs del tutor anterior: campos nuevos sobre una tabla ya cargada.
--
-- Va con ALTER TABLE a propósito: recrear la tabla se llevaría por delante
-- las fichas y las notas ya importadas. SQLite añade columnas sin tocar las
-- filas existentes, que quedan con NULL.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_traspas.sql
--
-- Es idempotente sólo por convención: si ya lo ejecutaste, SQLite dirá
-- "duplicate column name" y no pasa nada — la tabla ya está bien.

ALTER TABLE tutoria_alumnes ADD COLUMN tutor_anterior  TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN traspas         TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN derivacio       TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN derivacio_nota  TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN pi_contingut    INTEGER DEFAULT 0;
ALTER TABLE tutoria_alumnes ADD COLUMN pi_metodologic  INTEGER DEFAULT 0;
ALTER TABLE tutoria_alumnes ADD COLUMN acollida        INTEGER DEFAULT 0;
