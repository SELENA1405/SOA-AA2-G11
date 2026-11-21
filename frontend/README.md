# Frontend
Nginx serves this directory using `config/nginx.conf`; `/api/` is proxied to the backend service.

The page shows the equipment catalogue and details, the current load plan with the server-calculated total mass, and controls to add, update and remove items. Requests go through a serial action queue so they run in order, errors are shown on the page, and the page never calculates the total itself. The session code lives for one page load.
