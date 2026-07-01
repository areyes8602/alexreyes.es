/* Centro de Mando — service worker (app shell offline, scope /panel/) */
const CACHE = "cm-v5";
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
