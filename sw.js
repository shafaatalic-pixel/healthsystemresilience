/* Retired. An earlier version of the site registered a service worker; this file unregisters it. */
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.registration.unregister()); });
