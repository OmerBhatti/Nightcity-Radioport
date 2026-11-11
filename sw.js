const CACHE = 'radioport-v1';
const SHELL = ['./', './index.html', './manifest.webmanifest', './tracks.catalog.json', './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', event => {
	event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
	event.waitUntil(
		caches
			.keys()
			.then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
			.then(() => self.clients.claim()),
	);
});

// Network-first for same-origin GETs so updates show up; fall back to cache offline.
// Spotify and Google Fonts requests are left to the browser.
self.addEventListener('fetch', event => {
	const { request } = event;
	if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
	event.respondWith(
		fetch(request)
			.then(response => {
				const copy = response.clone();
				caches.open(CACHE).then(cache => cache.put(request, copy));
				return response;
			})
			.catch(() => caches.match(request).then(hit => hit || caches.match('./index.html'))),
	);
});
