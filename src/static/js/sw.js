const CACHE_NAME = 'marks-manager-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/tailwind.css',
  '/static/images/icon_upscayl_6x_digital-art-4x.png',
  '/static/images/icon_upscayl_16x_digital-art-4x.png'
];

// Install event: cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

// Fetch event: Network-first with cache fallback
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});