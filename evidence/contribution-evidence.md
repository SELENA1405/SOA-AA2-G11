# Contribution Evidence

Group 11, scenario S18 Club Equipment Transport Planner. The group has three members: San Ja Nar (6704860005), Kaung Nyein Lwin (6704860015) and Aung Kyaw Thu Phyo (6704860023). Evidence below comes from the repository history (https://github.com/SELENA1405/SOA-AA2-G11), the pull requests, and the members' own records of the problems they met.

## Contribution Summary

The work was split by layer, as agreed in the Phase 1 plan: database and configuration, backend, and frontend. San Ja Nar also led the group, merged the pull requests, and ran the integration tests and evidence capture.

| Date (2026) | What happened |
|---|---|
| 17 Nov | Repository created and the starter skeleton uploaded. `http.js` updated to keep server error messages, and `.gitignore` added. |
| 18 Nov | Group ID, student IDs and names set. PostgreSQL schema, seed data, `postgres.py` and the Dockerfile fix committed. |
| 19 Nov | Frontend UI and load-plan workflow committed. Backend domain files (`errors.py`, `scenario.py`, `ports.py`) and `main.py` started. |
| 20 Nov | Service layer, `api.py` and unit tests committed. Pull requests #1 (Database) and #2 (Frontend) merged. |
| 21 Nov | Adapter and 201/200 fixes, then pull request #3 (Backend). Mock fallback removed (PR #4), environment settings added (PR #5), frontend clean-up (PR #6). Integration run on the merged `main` branch: the four required cases passed, see `integration-evidence.md`. |

**Testing before merge.** Each member tested their own part on their own branch before it was merged:
- San Ja Nar checked the database layer with `psql` (`\dt`, `SELECT` and constraint tests) before pull request #1.
- Kaung Nyein Lwin ran the unit tests in `test_scenario.py` and checked the backend routes with `curl` before pull request #3.
- Aung Kyaw Thu Phyo tested the page in the browser and in Chrome DevTools on the Frontend branch before pull request #2, using the temporary sample data while the backend routes were not merged yet.

After the merges, the whole system was tested together on `main` (see `integration-evidence.md` and `testing-debugging-evidence.md`).

Commit history from GitHub, by date: [17 Nov (skeleton)](assets/git-history-1-nov-17-skeleton.png), [17 to 18 Nov](assets/git-history-2-nov-17-18.png), [19 Nov](assets/git-history-3-nov-19.png), [20 Nov](assets/git-history-4-nov-20.png) and [21 Nov](assets/git-history-5-nov-21.png).

## Individual Contributions

| Member | Work done | Supporting commits and files |
|---|---|---|
| San Ja Nar, 6704860005 (GitHub: SELENA1405), group leader | Repository set-up and starter skeleton. The `http.js` update that keeps the server's error message and code, and `.gitignore`. PostgreSQL schema (`equipment_types`, `load_plans`, `load_plan_items`, with key and CHECK constraints), seed data, and the persistence layer `postgres.py`. Dockerfile fix for the start-up crash. Environment-variable settings (`config/docker-compose.yml`, `config/.env.example`, `config/.gitignore`). Removal of the frontend mock fallback and a frontend clean-up. Group details in the manifest. Merging the pull requests. Integration testing, Postman collection and evidence files. | 17 Nov: `7c1180c`, `a260b0f`, `f3e582c`, `9f934b1`, `c513266`. 18 Nov: `3c0e122`, `a08fba3` (schema), `92ec48a` (seed), `dc82482` (`postgres.py`), `315e0eb` (Dockerfile). 21 Nov: `b972bfe` (mock fallback removed), `92cfd0f` (env and compose settings), `8a02bb3` (frontend clean-up). Pull requests #1, #2, #4, #5, #6. Files: `database/`, `config/`, `evidence/`. |
| Kaung Nyein Lwin, 6704860015 (GitHub: kaungnyeinlwin) | Backend domain and application layers: `errors.py`, `scenario.py` (unit-count validation 1 to 15 and server-side total mass), `ports.py`, `service.py` (service and adapter to the persistence layer). FastAPI routes and error handling in `api.py` and `main.py`. Unit tests in `test_scenario.py`. Fix of the adapter calls and the 201 (created) or 200 (existing) response for `POST /load-plans`. Rewrite of `api.py` to the seven required routes (his issue record). | 19 Nov: `16f63f1`, `1bcf9b4`, `f3eeec7`, `bc037a8`. 20 Nov: `4435fb5`, `89fd084`, `6f8b446`, `347cf25`, `fddbec8`, `0a6d1b1`, `e322280`, `1b613c1`. 21 Nov: `68d4f70` (adapter signatures), `8489543` (201/200), `1de85cc`, `1992c61`. Pull request #3. Files: `backend/app/`. Two "Update Database Files" commits (`01b0440` on 19 Nov and `bb123da` on 20 Nov) also changed the database files. |
| Aung Kyaw Thu Phyo, 6704860023 (GitHub: fallen-Eren) | Frontend: equipment catalogue and details, load-plan add, edit and remove controls, server-calculated total display, visible error messages, and request ordering through the action queue. | 19 Nov: `768a287` ("feat(frontend): implement S18 equipment transport planner UI and load plan workflow"). Pull request #2. Files: `frontend/index.html`, `frontend/scripts/index.js`, `frontend/assets/styles/main.css`. His four recorded issues are in `testing-debugging-evidence.md`. |

## Research or Technology Decisions

- **Layered backend:** the API layer calls the application service, which calls the persistence adapter in `postgres.py`. The domain layer (`errors.py`, `scenario.py`, `ports.py`) has no database code, so the rules can be unit-tested alone.
- **Server-side total:** the unit counts are validated and the total mass is calculated in the backend, so the page only shows what the server returns. Unit counts must be whole numbers from 1 to 15.
- **201 or 200 for `POST /load-plans`:** the group agreed in the Phase 1 plan that a new plan returns 201 and an existing plan for the same session returns 200.
- **Dockerfile fix instead of editing `pyproject.toml`:** the backend crashed with a missing `typing_extensions` module on the Python 3.14 image, so `typing-extensions` was added in the configuration layer without touching another member's file.
- **Docker Compose networking:** the three containers use the Compose default network and reach each other by service name (`database`, `backend`). Nginx serves the frontend and proxies `/api/` to the backend, so the browser uses a single origin.
- **Database start-up files:** the schema and seed SQL are mounted into `docker-entrypoint-initdb.d`. PostgreSQL only runs them for a new volume, so changes to them need `docker compose down -v` first. This was learned from a real failure (issue 6 in `testing-debugging-evidence.md`).
- **Environment settings:** `config/docker-compose.yml` reads the database name, user and password from environment variables with development defaults. `config/.env.example` documents them, and `config/.gitignore` keeps the real `config/.env` out of Git.
- **Serial request queue:** all plan actions go through one queue, so requests reach the server in the order the user made them, and the buttons are disabled while a request runs.
- **Testing tools:** Postman for the API runs, `psql` inside the database container for the stored rows, Chrome DevTools for the browser requests, and `pytest` for the domain unit tests.

## Academic Integrity and Source Acknowledgement

**Sources and libraries:** course starter `lesson-11_starter-code`, the assessment brief and scenario file `aa-02-s18.md`; FastAPI, psycopg 3, PostgreSQL 18, Nginx, Docker Compose, Postman, pytest, Chrome DevTools.

**AI use.** Each member lists below the tool used, the date, what it was used for, the related commits and how the output was checked. The dates follow the commits. The three evidence files and the README were drafted with Claude from the group's real screenshots, logs, commit history and the members' own issue records, then checked and edited by San Ja Nar. The screenshots, logs and test runs themselves come from the running system.

San Ja Nar (tool: Claude, claude.ai chat):

| Date | Task | Commits | How it was checked |
|---|---|---|---|
| Tue 17 Nov | Scenario choice, work split and review of the Phase 1 agreement | none (planning) | Kept only what matched the brief and the starter |
| Wed 18 Nov | Database schema, seed data and `postgres.py` | `a08fba3`, `92ec48a`, `dc82482` | Loaded into PostgreSQL in Docker and checked with `\dt`, `SELECT` and constraint tests |
| Wed 18 Nov | Diagnosing the 502 error and the Dockerfile fix | `315e0eb` | Applied only in `config/Dockerfile`, confirmed by a rebuild and the health checks |
| Sat 21 Nov | Review of teammates' code, and the edited `frontend/scripts/index.js` without the mock fallback | `b972bfe`, pull request #4 | The edited script was pasted into the frontend and tested in the browser |
| Sat 21 Nov | Environment-variable settings in `config/docker-compose.yml`, `config/.env.example` and `config/.gitignore` | `92cfd0f`, pull request #5 | Checked with `docker compose config` and a clean start-up |
| Sat 21 Nov | Frontend clean-up suggestions (the on-page test table, error display, README text) | `8a02bb3`, pull request #6 | Page reloaded and the four cases repeated in the browser |
| Sat 21 Nov | Postman collection, README and the three evidence files | `evidence/` and `README.md` | Collection run in Postman against the Docker stack; text checked against the screenshots, logs and commits |

Kaung Nyein Lwin (tool: Claude, claude.ai chat). The dates follow the commits that contain the work:

| Date | Task | Commits | How it was checked |
|---|---|---|---|
| Thu 19 Nov | Drafts of `backend/app/domain/errors.py` (a `DomainError` base class and the codes `INVALID_UNIT_COUNT`, `INVALID_REQUEST`, `EQUIPMENT_NOT_FOUND`, `PLAN_NOT_FOUND`, `DUPLICATE_ITEM`), `domain/scenario.py` (one shared `validate_unit_count` that rejects booleans first and accepts only a whole number from 1 to 15, and `calculate_result` using `Decimal`), `domain/ports.py` (`LoadPlanPort` replacing the starter `CollectionPort`) and the `DomainError` handler in `main.py`. The AI assumed the status mapping (400, 400, 404, 404, 409) because it did not have the errors table, and guessed the port method names | `16f63f1`, `1bcf9b4`, `bc037a8`, `f3eeec7` | The codes and statuses are exercised by the API runs in `testing-debugging-evidence.md`; the method names were aligned with the real `postgres.py` on 21 Nov |
| Fri 20 Nov | Rewrite of `application/service.py` and `presentation/api.py` (the seven required endpoints, translation of statuses into `DomainError`, a missing `unitCount` returning `INVALID_REQUEST`, the equipment name on each plan item, success codes 201, 200 and 204, removal of the 501 handler). Explanation of why a scratch check stays out of Git, then converting it into `backend/app/tests/test_scenario.py` (13 pytest cases) | `347cf25`, `0a6d1b1`, `1b613c1`, with follow-up edits `4435fb5`, `89fd084`, `e322280`, `fddbec8`, `6f8b446` | Unit tests run with pytest; routes checked with `curl` against the running stack |
| Fri 20 Nov | Git guidance for a non-fast-forward push rejection (`git pull --rebase origin Backend`) | `5b55a0a` | The push went through after the merge |
| Sat 21 Nov | Adjusting `LoadPlanAdapter` to the real `postgres.py` (`create_or_get_plan(plan_code, session_code)` returning whether the plan was created, and `get_plan`), making `POST /api/load-plans` return 201 when created and 200 when existing, and guidance for merging the Backend branch by pull request | `68d4f70`, `8489543`, `1de85cc`, `1992c61`, pull request #3 | `curl` evidence cases (totals 15, 19 and 12, and the rejected `unitCount: 0`), then the full API runs in `integration-evidence.md` |
| Sat 21 Nov | Diagnosing the 404 on `POST /api/load-plans` from the OpenAPI output, which showed only the starter routes, and helping to write issue 5 | none (diagnosis only; the fix is the `api.py` rewrite above) | Issue 5 in `testing-debugging-evidence.md` uses only his real `curl` and OpenAPI output. The AI had predicted a different failure (a 503), which was not used because the real output showed a 404 |

Aung Kyaw Thu Phyo (tool: Gemini, Antigravity Assistant CLI):

| Date | Task | How it was checked |
|---|---|---|
| Tue 17 Nov | Draft of the `frontend/scripts/http.js` change so that errors keep the server message and error code instead of a generic status text | Invalid quantities (0, 16 and decimals) were submitted again in the browser; the banner showed the server's message and code (issue 2 in `testing-debugging-evidence.md`) |
| Thu 19 Nov | Replacing the bootstrap page with the S18 planner interface (`frontend/index.html`, `frontend/assets/styles/main.css`) | Run in the browser through Docker Compose and checked in Chrome DevTools |
| Thu 19 Nov | State handling, mock session header, catalogue browsing, item details and load-plan actions in `frontend/scripts/index.js`; server-calculated total shown without any client-side calculation; error display for invalid quantities (0 or 16) | Added, updated and removed items in the browser and compared the total with the server response |
| Thu 19 Nov | Request ordering with `createActionQueue` to stop out-of-order responses on rapid clicks | Rapid clicks on "Add to Plan" and "Update"; the Network tab showed the requests running one after another (issue 4) |
| Thu 19 Nov | Temporary Phase 1 sample-data fallback while the backend routes returned 404 | Used only until the backend was merged; later removed (issue 3) |
| Sat 21 Nov | Diagnosing the `[SERVICE_UNAVAILABLE]` start-up error caused by the old database volume | `docker compose logs backend` showed the missing tables; fixed with `docker compose down -v` and retested (issue 6) |
| Sat 21 Nov | Pulling the merged `main`, rebuilding, and writing up the four frontend issues, fixes and retests | Live `GET /api/equipment-types` and `POST /api/load-plans` returned 200 and 201 from the real backend (issue 3) |