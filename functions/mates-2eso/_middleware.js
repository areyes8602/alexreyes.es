// Guarda /mates-2eso/*: sense sessió vàlida no se serveix res.
import { porta } from "../_zona.js";
import { requireSession } from "./_auth.js";

export const ZONA = {
  base: "/mates-2eso",
  titol: "Matemàtiques 2n ESO",
  subtitol: "Acceso privado",
  emoji: "📐",
  requireSession,
};

export async function onRequest(context) {
  return porta(context, ZONA);
}
