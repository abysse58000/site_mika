// Service Worker pour le cache hors-ligne du Cinéma Privé
const CACHE_NAME = 'cinema-prive-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(ASSETS_TO_CACHE);
      })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Retourne la réponse en cache si disponible
        if (response) {
          return response;
        }
        
        // Sinon, récupère depuis le réseau et met en cache
        return fetch(event.request)
          .then((response) => {
            // Clone la réponse pour la mettre en cache
            const responseClone = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseClone);
              });
            return response;
          });
      })
  );
});

self.addEventListener('activate', (event) => {
  // Supprime les anciens caches
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
