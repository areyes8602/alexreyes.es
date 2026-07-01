// Utilidades de sesión para /panel/ — cookie firmada con HMAC-SHA256.
// Sin dependencias: solo Web Crypto (disponible en Cloudflare Pages Functions).

const COOKIE = "panel_session";
const MAX_AGE = 60 * 60 * 24 * 30; // 30 días

const enc = new TextEncoder();

function b64urlBytes(bytes) {
  let s = btoa(String.fromCharCode(...bytes));
  return s.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlStr(str) {
  return btoa(unescape(encodeURIComponent(str)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function fromB64urlStr(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return decodeURIComponent(escape(atob(s)));
}

export function timingEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return b64urlBytes(new Uint8Array(sig));
}

export async function makeToken(user, secret) {
  const exp = Date.now() + MAX_AGE * 1000;
  const p = b64urlStr(`${user}|${exp}`);
  const sig = await hmac(secret, p);
  return `${p}.${sig}`;
}

export async function verifyToken(token, secret) {
  if (!token) return null;
  const i = token.lastIndexOf(".");
  if (i < 0) return null;
  const p = token.slice(0, i), sig = token.slice(i + 1);
  const expect = await hmac(secret, p);
  if (!timingEqual(sig, expect)) return null;
  let payload;
  try { payload = fromB64urlStr(p); } catch (e) { return null; }
  const sep = payload.lastIndexOf("|");
  if (sep < 0) return null;
  const user = payload.slice(0, sep);
  const exp = Number(payload.slice(sep + 1));
  if (!exp || Date.now() > exp) return null;
  return user;
}

export function getCookie(request, name = COOKIE) {
  const raw = request.headers.get("Cookie") || "";
  const m = raw.match(new RegExp("(?:^|; )" + name + "=([^;]+)"));
  return m ? m[1] : null;
}

export function sessionCookie(token) {
  return `${COOKIE}=${token}; Path=/panel; HttpOnly; Secure; SameSite=Lax; Max-Age=${MAX_AGE}`;
}
export function clearCookie() {
  return `${COOKIE}=; Path=/panel; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}
