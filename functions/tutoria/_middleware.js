// Guarda /tutoria/*: sense sessió vàlida no se serveix RES, ni HTML ni fotos.
// El porter és a functions/_zona.js, compartit amb les altres zones.
import { porta } from "../_zona.js";
import { requireSession } from "./_auth.js";

export const ZONA = {
  base: "/tutoria",
  titol: "Tutoría",
  subtitol: "Acceso privado",
  emoji: "🎓",
  requireSession,
};

export async function onRequest(context) {
  return porta(context, ZONA);
}
