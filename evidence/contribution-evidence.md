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

**AI use.** Claude (Anthropic) was used as a study and coding assistant. Each entry records the tool, purpose, what was used, and how it was checked. All AI output was reviewed and tested by the member before it was committed. The three evidence files (`integration-evidence.md`, `testing-debugging-evidence.md` and this file) were drafted with Claude from the group's real screenshots, logs, commit history and the members' own issue records, then checked and edited by San Ja Nar. The screenshots, logs and test runs themselves were produced by the group from the running system.

San Ja Nar:

| Date | Task | AI output | How it was checked |
|---|---|---|---|
| 17 Nov | Scenario choice, work split, review of the Phase 1 agreement | Suggested corrections and a task breakdown | Kept what matched the brief and the starter |
| 18 Nov | Database schema, seed data and `postgres.py` | Draft SQL and Python | Loaded into PostgreSQL in Docker and checked with `\dt`, `SELECT` and constraint tests |
| 18 Nov | Diagnosing the 502 error and the Dockerfile fix | Explanation of the missing module and the one-line fix | Applied only in `config/Dockerfile`, confirmed by a rebuild and the health checks |
| 20 to 21 Nov | Review of teammates' code, a test script, a Postman collection, and the edited `frontend/scripts/index.js` without the mock fallback | Review notes, draft files and the edited script | The edited script was pasted into the frontend, tested in the browser and committed (`b972bfe`); the collection was run in Postman against the Docker stack |
| 21 Nov | Environment-variable settings and the three evidence files | Draft config files and draft text | Config files checked with `docker compose config` and a clean start-up; evidence text checked against the screenshots, logs and commits |

Kaung Nyein Lwin: [FILL tool, purpose, output used, changes, verification and dates, or "no AI used"]

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