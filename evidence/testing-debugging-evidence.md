# Testing and Debugging Evidence

Scenario S18, Club Equipment Transport Planner. The final tests were run on 21 Nov 2026 against the merged `main` branch, with the whole stack started by `docker compose -f config/docker-compose.yml up --build -d --wait`. The browser evidence and the database checks for the four required cases are in `integration-evidence.md`. This file covers the API test requests, the browser and log checks, and the six problems the group found and fixed while building and testing the system. Each member recorded the problems they met themselves.

## API Request Evidence

The API was tested with Postman, using the collection [S18-postman-collection.json](assets/S18-postman-collection.json). Import it into Postman and set `baseUrl` to `http://127.0.0.1:8080/api` (Nginx) to repeat the runs. The collection checks the status code and the key fields of every response.

| Run | What it checks | Screenshot |
|---|---|---|
| Catalogue | Equipment list, one item by code, unknown code returns 404 | [postman-1-catalogue.png](assets/postman-1-catalogue.png) |
| Create or reuse plan | New session gets 201, same session again gets 200, missing `X-Session-Code` header gets 400 | [postman-2-create-reuse-plan.png](assets/postman-2-create-reuse-plan.png) |
| Required evidence cases | Add 2 x EQUIP-001 and 1 x EQUIP-002 (15 kg), update EQUIP-001 to 3 (19 kg), delete EQUIP-002 (12 kg), update to 0 rejected with 400 and the plan still 12 kg | [postman-3-evidence-cases.png](assets/postman-3-evidence-cases.png) |
| Extra error checks | Invalid unit counts, malformed requests, unknown plan or equipment, duplicate item | [postman-4-extra-error-checks.png](assets/postman-4-extra-error-checks.png) |
| Service communication | The same API through Nginx on port 8080 and directly on the backend on port 8000 | [postman-5-service-communication.png](assets/postman-5-service-communication.png) |

The seven endpoints that were tested are listed in the generated API documentation: [api-docs.png](assets/api-docs.png).

After each browser action, the saved plan was read again with `GET /api/load-plans/{planCode}` in the same session ([case1-postman.png](assets/case1-postman.png), [case2-postman.png](assets/case2-postman.png), [case3-postman.png](assets/case3-postman.png), [case4-postman.png](assets/case4-postman.png)). The server totals were 15, 19, 12 and 12 kg, the same as the page showed.

The backend also has unit tests for the domain rules (unit-count validation and the server-side total), in `backend/app/tests/test_scenario.py`.

## Browser or Network Evidence

The Network tab was recorded during the four required cases in one browser session. The request list shows the full sequence with the initiator `http.js:6`, and every request goes to `/api/...` on port 8080, so the browser only talks to Nginx:

| Case | Network screenshot | Requests that matter |
|---|---|---|
| Fresh page | [case0-network.png](assets/case0-network.png) | catalogue 200, create plan 201, read plan 200 |
| 1 | [case1-network.png](assets/case1-network.png) | two item adds, both 201 |
| 2 | [case2-network.png](assets/case2-network.png) | update, 200 |
| 3 | [case3-network.png](assets/case3-network.png) | delete, 204 |
| 4 | [case4-network.png](assets/case4-network.png) | rejected update, 400, shown in red |

For the rejected update in case 4, the request and response details were opened:
- [case4-headers.png](assets/case4-headers.png): `PUT http://127.0.0.1:8080/api/load-plans/PLAN-4396CD47/items/EQUIP-001`, status `400 Bad Request`, response from `nginx/1.30.5`, and the `X-Session-Code` header on the request.
- [case4-response.png](assets/case4-response.png): the response body `{"error_code": "INVALID_UNIT_COUNT", "message": "unitCount must be a whole number from 1 to 15."}`.

The page showed the same message as a visible red error ([case4-browser.png](assets/case4-browser.png)).

## Log or Console Evidence

The container logs from the whole test session are saved in [08-logs.txt](assets/08-logs.txt). They show:
- Start-up: the database initialised and ran the schema and seed files, then the backend reported `Application startup complete`, and the first `GET /api/health` returned 200.
- The four cases for `PLAN-4396CD47`, in order: `POST .../items` 201 twice, `PUT .../items/EQUIP-001` 200, `DELETE .../items/EQUIP-002` 204, then `PUT .../items/EQUIP-001` 400 Bad Request, followed by `GET` 200 reads of the plan.
- The extra error checks from the Postman run: `400` for invalid requests, `404` for an unknown plan, equipment or item, and `409 Conflict` for a duplicate item.
- No `500` status codes and no Python tracebacks appear in the backend log.

Start-up and health evidence: [01-compose-up.log](assets/01-compose-up.log), [03-ps.txt](assets/03-ps.txt) (database healthy, backend and frontend up), [04-health-8080.json](assets/04-health-8080.json) and [05-health-8000.json](assets/05-health-8000.json) (both return `{"status":"ok","database":"connected"}`), and [06-service-name-dns.txt](assets/06-service-name-dns.txt) (the backend resolves the service name `database`).

## Issue Found

Six issues were found and recorded, one list for the whole group. The issue numbers are used again under Fix Applied and Retest Evidence.

| No. | Member | Date (Asia/Bangkok) | Problem |
|---|---|---|---|
| 1 | Member 3 (San Ja Nar) | Tue 17 Nov | Backend container exited at start-up, so Nginx returned 502 Bad Gateway |
| 2 | Member 1 (Aung Kyaw Thu Phyo) | Tue 17 Nov | Browser showed only "Request failed (400)" and hid the server's validation message |
| 3 | Member 1 (Aung Kyaw Thu Phyo) | Thu 19 to Sat 21 Nov | Page got 404 from `/api/equipment-types` and `/api/load-plans` before the backend routes were merged |
| 4 | Member 1 (Aung Kyaw Thu Phyo) | Thu 19 Nov | Rapid clicks sent overlapping requests that finished out of order, so the page briefly showed stale totals |
| 5 | Member 2 (Kaung Nyein Lwin) | Sat 21 Nov | The running backend returned 404 for the required routes because it still had the starter `api.py` |
| 6 | Member 1 (Aung Kyaw Thu Phyo) | Sat 21 Nov | After a rebuild the page showed `[SERVICE_UNAVAILABLE]` because the tables did not exist |

**Issue 1: backend exits at start-up (502 Bad Gateway).**
After `docker compose -f config/docker-compose.yml up --build -d --wait`, the page and `curl http://127.0.0.1:8080/api/health` returned `502 Bad Gateway`. A 502 from Nginx means it could not reach the backend, so the containers were checked with `docker compose -f config/docker-compose.yml ps`: the frontend and database were running but the backend container had exited. The backend log (`docker compose -f config/docker-compose.yml logs backend`) ended with `ModuleNotFoundError: No module named 'typing_extensions'`. FastAPI crashed at import time because that package was not installed in the image built from `python:3.14-slim`. The exact upstream reason (probably the starter's unpinned dependencies) was not investigated further and is not confirmed. The error came back on 21 Nov on the Frontend branch, because that branch had been created before the fix was merged. There, `grep typing config/Dockerfile` returned nothing, which confirmed the old Dockerfile.

**Issue 2: generic HTTP error hid the server's validation details.**
For invalid input such as quantity 0 or 16, the page showed only "Request failed (400)." The Network tab showed that the backend had returned `{"error_code": "INVALID_UNIT_COUNT", "message": "unitCount must be a whole number from 1 to 15."}`. The cause was in the starter `frontend/scripts/http.js`: whenever the response was not OK it threw a generic error with only the status code and dropped the server's message and error code.

**Issue 3: 404 responses before the backend routes were merged.**
While the frontend was built in parallel with the backend, loading the page returned `404 Not Found` for `GET /api/equipment-types` and `POST /api/load-plans`, so the catalogue and the plan could not load. The Network tab showed red 404 rows and the console logged the failed fetches. The backend S18 routes were still on the Backend branch, and `main` still had the starter routes (`/api/catalogue` and `/api/collections`).

**Issue 4: stale plan display and race conditions on rapid actions.**
Clicking "Add to Plan", "Update" or "Remove" quickly sent several requests at once. A slower earlier request could finish after a later one, so item quantities and the total mass briefly showed old values. The Network tab showed overlapping requests. The cause was that the handlers called `fetch` concurrently, with no queue and no disabled buttons while a request was running.

**Issue 5: required routes return 404 because the backend had the starter `api.py`.**
Running `curl.exe -i -X POST http://127.0.0.1:8080/api/load-plans -H "X-Session-Code: bullet-test"` returned `404 Not Found` with `{"detail":"Not Found"}` instead of `201`. In the same run, `GET /api/health` returned 200 but still included the starter's `"scope": "bootstrap only"` field. `http://127.0.0.1:8080/api/openapi.json` listed only `/api/health`, `/api/catalogue` and `/api/collections/...`, none of the seven required routes. The OpenAPI title was already "AA-02 S18 Club Equipment Transport Planner", so the running image had the updated `main.py` together with the starter `api.py`. The 404 was FastAPI's normal answer for an unknown path, so the application itself was running correctly with the wrong route definitions.

**Issue 6: `[SERVICE_UNAVAILABLE]` and "Failed to load catalogue." after a rebuild.**
After pulling `main` and running `docker compose down` followed by `docker compose up --build`, the page showed "Online" (health returned 200), Plan Code `None`, an error banner `Check API/database logs. [SERVICE_UNAVAILABLE]`, and "Failed to load catalogue." The backend log showed `503` on `GET /api/equipment-types` and `POST /api/load-plans`, caused by `psycopg.errors.UndefinedTable: relation "equipment_types" does not exist` (and the same for `load_plans`). The cause was that `docker compose down` without `-v` kept the older PostgreSQL volume. PostgreSQL only runs the files in `docker-entrypoint-initdb.d` (`001-schema.sql` and `002-seed.sql`) the first time a volume is created, so the new schema was never applied.

## Fix Applied

**Issue 1 (Wed 18 Nov).** One line in `config/Dockerfile` installs the missing package together with the project:
```
RUN python -m pip install --no-cache-dir . typing-extensions
```
It was committed on the Database branch on 18 Nov (commit `315e0eb`) and merged into `main`. It was made in the Dockerfile and not in `backend/pyproject.toml`, because that file belongs to the backend developer and the problem only affected the container image. On the Frontend branch the fix arrived by merging `origin/main` (`git fetch origin`, then `git merge origin/main`), followed by a rebuild.

**Issue 2 (Tue 17 Nov, 21:01).** `frontend/scripts/http.js` was changed to keep the server's message and code. It now uses `payload?.message` as the error message and attaches `error.status`, `error.serverMessage` and `error.code` (from `error_code`). The page shows the message and code in its error banner. Committed by San Ja Nar as `c513266` (17 Nov, 21:01, "feat(frontend): update http.js to keep server messages and add .gitignore"). The problem was found and reported by Aung Kyaw Thu Phyo while testing invalid input in the browser.

**Issue 3 (Thu 19 Nov to Sat 21 Nov).** Temporary Phase 1 fallback data (a sample catalogue and a sample plan) was added to `frontend/scripts/index.js` (commit `768a287`, 19 Nov) for the case where those endpoints returned 404, so the layout, styling and request queue could be built and checked independently. When the backend routes were merged into `main`, the local Frontend branch was synced with `origin/main` and the fallback code was removed on 21 Nov by San Ja Nar (commit `b972bfe` "Removed the mock fallback", merged in pull request #4). The page now talks only to the real backend, and the plan total shown comes from the server.

**Issue 4 (Thu 19 Nov).** The existing `createActionQueue` helper in `frontend/scripts/action-queue.js` was used for every plan action (`initLoadPlan`, `handleAddItem`, `handleUpdateItem`, `handleRemoveItem`) in `frontend/scripts/index.js` (commit `768a287`, 19 Nov). Requests now run strictly one after another, and each action button is disabled (`button.disabled = true`) while its request is in progress.

**Issue 5 (Sat 21 Nov).** `backend/app/api.py` was rewritten with the seven required routes (`/api/equipment-types` and `/api/load-plans/...`) and the service layer behind them. The stack was then rebuilt from clean with `docker compose -f config/docker-compose.yml down -v` and `docker compose -f config/docker-compose.yml up --build -d --wait`.

**Issue 6 (Sat 21 Nov).** The stale database volume was removed with `docker compose -f config/docker-compose.yml down -v` and the containers were rebuilt with `up --build`. The same rule is now used for every rebuild that changes the SQL files: `down -v` first, so PostgreSQL runs the schema and seed files again.

## Retest Evidence

**Issue 1 (retested Sat 21 Nov).** A clean start on the merged `main` branch: [01-compose-up.log](assets/01-compose-up.log) shows the build step `RUN python -m pip install --no-cache-dir . typing-extensions` and all three containers reaching `Healthy`. [03-ps.txt](assets/03-ps.txt) shows the backend `Up` on port 8000, the database `healthy` and the frontend `Up` on port 8080. [04-health-8080.json](assets/04-health-8080.json) and [05-health-8000.json](assets/05-health-8000.json) both return `{"status":"ok","database":"connected"}`. The four required cases then ran through Nginx without a 502, and [08-logs.txt](assets/08-logs.txt) shows no tracebacks.

**Issue 2 (retested after the 17 Nov fix; final run Sat 21 Nov).** Invalid quantities (0, 16 and decimal values) were submitted again. The error banner and the browser console now show the exact server message and the code `INVALID_UNIT_COUNT`. The final run is in [case4-browser.png](assets/case4-browser.png) (red banner with the message and code) and [case4-response.png](assets/case4-response.png) (the JSON body returned by the server).

**Issue 3 (retested Sat 21 Nov).** After pulling `main` and rebuilding, `GET /api/equipment-types` returned the seeded records EQUIP-001 and EQUIP-002 with status 200, and `POST /api/load-plans` returned a real plan code with status 201. All add, update and delete requests ran against PostgreSQL only. The requests are visible in [case0-network.png](assets/case0-network.png) and [case1-network.png](assets/case1-network.png), and the page in [case1-browser.png](assets/case1-browser.png).

**Issue 4 (retested after the 19 Nov fix; final run Sat 21 Nov).** Rapid clicks on "Add to Plan" and "Update" were repeated. The Network tab showed the requests running one after another, and the item list and "Authoritative Total Mass" updated consistently without flicker. In the final evidence run, every change is followed by its own refresh of the plan in order (see [case2-network.png](assets/case2-network.png)).

**Issue 5 (retested Sat 21 Nov, 10:00 to 10:01 GMT).** After the rebuild, `curl.exe -i -X POST http://127.0.0.1:8080/api/load-plans -H "X-Session-Code: backend-test"` returned `201 Created` with `{"planCode":"PLAN-32D2D68F"}`, and `curl.exe -i http://127.0.0.1:8080/api/health` returned `200 OK` with `{"status":"ok","database":"connected"}`. The starter's `"scope"` field was gone, which confirms that the rewritten `api.py` is the one running. The required routes are registered and plan creation works through the real database. The final run of all seven routes is in [postman-1-catalogue.png](assets/postman-1-catalogue.png), [postman-2-create-reuse-plan.png](assets/postman-2-create-reuse-plan.png) and [api-docs.png](assets/api-docs.png).

**Issue 6 (retested Sat 21 Nov).** After `down -v` and the rebuild, the page loaded the catalogue with EQUIP-001 (4 kg) and EQUIP-002 (7 kg), created a live plan code, and showed the correct "Authoritative Total Mass" after items were added. The database check in [07-db-schema-seed.txt](assets/07-db-schema-seed.txt) shows the three tables and the two seeded equipment types.