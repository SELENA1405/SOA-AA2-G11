# Integration Evidence

Scenario S18, Club Equipment Transport Planner. All evidence was captured on 21 Nov 2026 from the merged `main` branch, running the whole stack with `docker compose -f config/docker-compose.yml up --build -d --wait`. One browser session was used for the four required cases, so every step builds on the previous one. The plan code in the evidence is `PLAN-4396CD47`.

## Integrated Workflow

The browser talks only to Nginx. Nginx serves the static frontend and forwards `/api/` to the backend, which reads and writes PostgreSQL.

```
Browser (index.html + JS)  ->  Nginx :8080  ->  FastAPI backend :8000  ->  PostgreSQL 18 (service "database")
   serial request queue        /api/ proxy      api -> service -> adapter -> postgres.py
```

How one action travels through the system, using "add 2 x Foldable Chair":
1. The page sends `POST /api/load-plans/PLAN-4396CD47/items` with the `X-Session-Code` header and the body `{"equipmentCode":"EQUIP-001","unitCount":2}`. Requests go through a serial action queue, so they reach the server in order.
2. Nginx proxies the request to `backend:8000`. The Compose service name resolves inside the Compose network (`database -> 172.23.0.2` in [06-service-name-dns.txt](assets/06-service-name-dns.txt)).
3. The API layer validates the request, the application service calls the persistence adapter, and `postgres.py` stores the row in `load_plan_items`.
4. The page then fetches `GET /api/load-plans/PLAN-4396CD47` and displays the saved items and the total mass. The total is calculated by the server (unit count x unit mass), never in JavaScript.

Start-up and connectivity checks:
- [01-compose-up.log](assets/01-compose-up.log): the network, volume and three containers were created. The database became healthy first, then the backend and frontend.
- [03-ps.txt](assets/03-ps.txt): backend on port 8000, database `healthy`, frontend on port 8080.
- [04-health-8080.json](assets/04-health-8080.json) and [05-health-8000.json](assets/05-health-8000.json): both the Nginx route and the direct backend route return `{"status":"ok","database":"connected"}`.
- [02-compose-config.txt](assets/02-compose-config.txt): the resolved Compose configuration.

## Frontend Evidence

The page was loaded fresh, then the four required cases were run in order. Each screenshot shows the page after the action. The Network screenshots show the request list with status codes and the initiator `http.js:6`.

| Step | Browser screenshot | Network screenshot | What the page shows |
|---|---|---|---|
| Fresh page | [case0-empty-plan.png](assets/case0-empty-plan.png) | [case0-network.png](assets/case0-network.png) | Catalogue with two items, empty plan, total 0 kg |
| Case 1: add 2 x EQUIP-001, 1 x EQUIP-002 | [case1-browser.png](assets/case1-browser.png) | [case1-network.png](assets/case1-network.png) | Two saved rows, total **15 kg**, success message |
| Case 2: change EQUIP-001 to 3 | [case2-browser.png](assets/case2-browser.png) | [case2-network.png](assets/case2-network.png) | EQUIP-001 = 3, EQUIP-002 = 1, total **19 kg** |
| Case 3: remove EQUIP-002 | [case3-browser.png](assets/case3-browser.png) | [case3-network.png](assets/case3-network.png) | Only EQUIP-001 = 3, total **12 kg** |
| Case 4: change EQUIP-001 to 0 | [case4-browser.png](assets/case4-browser.png) | [case4-network.png](assets/case4-network.png) | Red error "unitCount must be a whole number from 1 to 15. [INVALID_UNIT_COUNT]", total still **12 kg** |

The Network list in [case4-network.png](assets/case4-network.png) shows the whole session in order: catalogue `200`, create plan `201`, two item adds `201`, update `200`, delete `204`, and the rejected update in red with status `400`. Each change is followed by a `GET` of the plan with status `200`, which is how the page refreshes the saved state.

## Backend API Evidence

Postman requests against the running stack (base URL `http://127.0.0.1:8080/api`, plus direct calls to port 8000):

| Evidence | Screenshot |
|---|---|
| Catalogue list, one item, unknown item (404) | [postman-1-catalogue.png](assets/postman-1-catalogue.png) |
| Create plan (201), same session again (200), missing session header (400) | [postman-2-create-reuse-plan.png](assets/postman-2-create-reuse-plan.png) |
| The four required cases with assertions on status codes and totals | [postman-3-evidence-cases.png](assets/postman-3-evidence-cases.png) |
| Extra error checks (invalid counts, malformed request, unknown plan or equipment, duplicate item) | [postman-4-extra-error-checks.png](assets/postman-4-extra-error-checks.png) |
| Same API through Nginx (8080) and directly on the backend (8000) | [postman-5-service-communication.png](assets/postman-5-service-communication.png) |
| The seven API endpoints in the generated API documentation | [api-docs.png](assets/api-docs.png) |

After each browser case, the plan was read again from Postman with `GET /api/load-plans/{planCode}` in the same session. The server's JSON agreed with the browser each time:
- [case1-postman.png](assets/case1-postman.png): two items, `totalMassKg: 15`
- [case2-postman.png](assets/case2-postman.png): EQUIP-001 count 3, `totalMassKg: 19`
- [case3-postman.png](assets/case3-postman.png): one item, `totalMassKg: 12`
- [case4-postman.png](assets/case4-postman.png): unchanged after the rejected update, `totalMassKg: 12`

The backend log in [08-logs.txt](assets/08-logs.txt) records the same sequence for `PLAN-4396CD47`: `POST .../items` 201 twice, `PUT .../items/EQUIP-001` 200, `DELETE .../items/EQUIP-002` 204, then `PUT .../items/EQUIP-001` 400.

## Database Evidence

The schema and seed data were created by the SQL files mounted into the database container ([07-db-schema-seed.txt](assets/07-db-schema-seed.txt)). There are three tables (`equipment_types`, `load_plan_items`, `load_plans`) and two seeded equipment types: EQUIP-001 Foldable Chair at 4.00 kg and EQUIP-002 Portable Speaker at 7.00 kg.

After each case, the stored rows were read directly with `psql` inside the database container, so the browser result can be compared with what is actually saved:

| Case | Rows in `load_plan_items` | File | Screenshot |
|---|---|---|---|
| 1 | EQUIP-001 = 2, EQUIP-002 = 1 | [case1-db.txt](assets/case1-db.txt) | [case1-db.png](assets/case1-db.png) |
| 2 | EQUIP-001 = 3, EQUIP-002 = 1 | [case2-db.txt](assets/case2-db.txt) | [case2-db.png](assets/case2-db.png) |
| 3 | EQUIP-001 = 3 only | [case3-db.txt](assets/case3-db.txt) | [case3-db.png](assets/case3-db.png) |
| 4 | EQUIP-001 = 3 only (unchanged) | [case4-db.txt](assets/case4-db.txt) | [case4-db.png](assets/case4-db.png) |

[case3-db.txt](assets/case3-db.txt) also shows that `equipment_types` still holds both catalogue items after EQUIP-002 was removed. Removing an item deletes the plan entry only, not the equipment type.

## Success Case

Cases 1 to 3 form the success path. Totals, line masses and stored counts agree in the browser, the API and the database:

| Case | Action | Response | Total in page and API | Database |
|---|---|---|---|---|
| 1 | Add 2 x EQUIP-001, then 1 x EQUIP-002 | 201, 201 | 15 kg (2 x 4 + 1 x 7) | 2 and 1 |
| 2 | Set EQUIP-001 to 3 | 200 | 19 kg (3 x 4 + 1 x 7) | 3 and 1 |
| 3 | Remove EQUIP-002 | 204 | 12 kg (3 x 4) | 3 only |

Screenshots: [case1-browser.png](assets/case1-browser.png), [case2-browser.png](assets/case2-browser.png) and [case3-browser.png](assets/case3-browser.png), with the matching `network`, `postman` and `db` files listed above. The totals come from the server's `totalMassKg` value, so a page reload would show the same numbers.

## Error or Empty-Data Case

**Empty data.** On a fresh page the new plan has no items. The page shows the message "No equipment in load plan yet. Add items below." and a total of 0 kg ([case0-empty-plan.png](assets/case0-empty-plan.png)). The plan already exists on the server, because the page created it with `POST /api/load-plans` (201).

**Invalid edit (required case 4).** With EQUIP-001 at 3 units and the plan at 12 kg, the unit count was changed to 0 and Update was clicked ([case4-browser.png](assets/case4-browser.png)):
- The server rejected the request with status `400` and the error code `INVALID_UNIT_COUNT`. It appears as the red row in [case4-network.png](assets/case4-network.png) and in the backend log as `PUT /api/load-plans/PLAN-4396CD47/items/EQUIP-001 ... 400 Bad Request` ([08-logs.txt](assets/08-logs.txt)).
- Browser request and response details: [case4-headers.png](assets/case4-headers.png) shows `PUT /api/load-plans/PLAN-4396CD47/items/EQUIP-001` with the `X-Session-Code` header and status `400 Bad Request` from Nginx, and [case4-response.png](assets/case4-response.png) shows the JSON error body `{"error_code": "INVALID_UNIT_COUNT", "message": "unitCount must be a whole number from 1 to 15."}`.
- The page shows a visible red error message with the code and keeps the table as saved.
- The saved state did not change: the plan is still 12 kg in the page and in Postman ([case4-postman.png](assets/case4-postman.png)), and the database still holds only EQUIP-001 = 3 ([case4-db.txt](assets/case4-db.txt)).

**Other error cases.** The Postman run in [postman-4-extra-error-checks.png](assets/postman-4-extra-error-checks.png) checks further invalid input and unknown or duplicate data. The backend log shows the resulting status codes: `400` for invalid requests, `404` for an unknown plan, equipment or item, and `409` for a duplicate item.