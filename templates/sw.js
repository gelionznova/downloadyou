// templates/sw.js
const VERSION = "v2";
const CACHE_STATIC = `static-${VERSION}`;
const ASSETS = [
  "/",
  "{{ url_for('static', filename='manifest.json') }}",
  "{{ url_for('static', filename='android-chrome-512x512.png') }}",
  "{{ url_for('static', filename='offline.html') }}",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
  "https://code.jquery.com/jquery-3.6.0.min.js"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_STATIC).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k !== CACHE_STATIC ? caches.delete(k) : null)))
    )
  );
  self.clients.claim();
});

const isMutableRequest = (req) =>
  req.method !== "GET" ||
  req.url.includes("/descargar") ||
  req.url.includes("/descargas");

self.addEventListener("fetch", (event) => {
  const { request } = event;

  if (isMutableRequest(request)) {
    return; // no cache
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      const fetchPromise = fetch(request)
        .then((networkResp) => {
          if (
            networkResp &&
            networkResp.status === 200 &&
            (request.url.startsWith(self.location.origin) ||
              request.url.includes("cdn.jsdelivr.net") ||
              request.url.includes("code.jquery.com"))
          ) {
            const respClone = networkResp.clone();
            caches.open(CACHE_STATIC).then((cache) => cache.put(request, respClone));
          }
          return networkResp;
        })
        .catch(() => {
          if (request.mode === "navigate") {
            return caches.match("{{ url_for('static', filename='offline.html') }}");
          }
        });

      return cached || fetchPromise;
    })
  );
});
