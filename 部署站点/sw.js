// Service Worker for 知识库 · 学习打卡
// Enables offline access and "Add to Home Screen" on mobile

const CACHE_NAME = 'kb-dashboard-v4';
const CORE_FILES = [
  '/',
  '/index.html',
  '/checkin.html',
  '/login.html',
  '/manifest.json',
  '/icons/favicon.ico',
  '/icons/favicon-32.png',
  '/icons/favicon-16.png',
  '/icons/favicon-48.png',
  '/icons/favicon-64.png',
  '/icons/favicon-128.png',
  '/icons/favicon-256.png',
  '/icons/favicon-512.png',
  '/icons/apple-touch-icon.png'
];

// Install: pre-cache core files
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_FILES).catch((err) => {
        console.warn('[SW] Pre-cache partial:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate: clean ALL old caches (force refresh)
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: NETWORK-FIRST strategy (always try fresh server data)
// Only fall back to cache when offline. This ensures notes update immediately.
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  event.respondWith(
    fetch(event.request).then((response) => {
      // Got fresh response — update cache in background
      if (response && response.status === 200 && url.origin === location.origin) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, clone);
        });
      }
      return response;
    }).catch(() => {
      // Network failed (offline) — return cached version
      return caches.match(event.request).then((cached) => {
        if (cached) return cached;
        // Last resort: serve index.html for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
        return new Response('Offline', { status: 503, statusText: 'Offline' });
      });
    })
  );
});
