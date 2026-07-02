/* Centro de Mando — service worker (app shell offline + push, scope /panel/) */
const CACHE = "cm-v9";
const SHELL = [
  "/panel/",
  "/panel/index.html",
  "/panel/manifest.webmanifest",
  "/panel/icon-192.png",
  "/panel/icon-512.png",
  "/panel/icon-180.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

// Push sin payload: al despertar, pedimos el resumen al servidor (con la cookie de sesión).
self.addEventListener("push", (e) => {
  e.waitUntil((async () => {
    let title = "Centro de Mando", body = "Toca para abrir tu panel.";
    try {
      const r = await fetch("/panel/api/digest", { credentials: "same-origin" });
      if (r.ok) {
        const j = await r.json();
        if (j && j.title) { title = j.title; body = j.body || body; }
      }
    } catch (_) {}
    await self.registration.showNotification(title, {
      body, icon: "/panel/icon-192.png", badge: "/panel/icon-192.png",
      tag: "cm-digest", data: { url: "/panel/" }
    });
  })());
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil((async () => {
    const wins = await clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const w of wins) if (w.url.includes("/panel/")) return w.focus();
    return clients.openWindow("/panel/");
  })());
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;      // no tocar CDN / externos
  if (!url.pathname.startsWith("/panel/")) return;       // solo el panel
  if (url.pathname.includes("/api/")) return;            // nunca cachear auth

  // network-first para navegación (no servir login cacheado como app);
  // cache-first para assets estáticos del shell.
  const isNav = req.mode === "navigate";
  if (isNav) {
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match(req).then((m) => m || caches.match("/panel/index.html")))
    );
  } else {
    e.respondWith(
      caches.match(req).then((m) => m || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }))
    );
  }
});
