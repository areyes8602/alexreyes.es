-- Com es mira cada distribució de l'aula.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_aula_vista.sql
--
-- Fins ara l'estil de les targetes i la vista des de la taula només vivien al
-- navegador: canviaves d'ordinador i tornaven als valors de sempre, i les
-- dues distribucions es veien igual encara que una sigui per treballar a la
-- pantalla i l'altra el full que es queda a la taula. Amb aquesta columna la
-- manera de mirar-la va amb la distribució, com les posicions.
--
-- JSON {"mida": "16"|"foto", "fotos": true|false, "girada": true|false}.
--
-- Si no s'executa no es trenca res: la pàgina segueix recordant-ho al
-- navegador i el desat de posicions no en depèn.

ALTER TABLE tutoria_aules ADD COLUMN vista TEXT;
