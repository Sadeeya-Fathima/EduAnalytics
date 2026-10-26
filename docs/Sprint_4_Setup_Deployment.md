# Sprint 4 - Setup & Deployment

**Project:** EduAnalytics
**Sprint goal:** Make EduAnalytics straightforward for a non-technical Windows user to install, configure, start, access over a local network, maintain, and back up securely.
**Status:** In progress - Phases 1-4 complete to their documented scope; Phase 5 LAN binding and second-device access verified, with startup LAN URL display and backup/recovery still open.
**Target platform:** Windows 10/11 (primary target; other operating systems are unverified).
**Last updated:** 2026-10-26

---

## 1. Sprint objective

A user with basic Windows computer skills should be able to:

1. Check a short list of prerequisites and clone the repository.
2. Run **one setup script** that checks the environment, installs dependencies, configures a persistent secret key, and safely initializes the database.
3. Complete a guided first-run setup in the browser to register the institution and create the initial Administrator account.
4. Start and stop EduAnalytics using simple scripts or shortcuts, without remembering Python or Flask commands.
5. Open EduAnalytics on the host computer and access it from authorized devices on the same LAN.
6. Configure daily, weekly, or monthly database backups, see whether backups succeeded, and follow a tested restore process.

The user-facing workflow should hide routine developer details behind scripts and clear UI instructions. Scripts must give understandable success and failure messages. This document is the working sprint record: mark work complete only after implementation and verification.

## 2. Scope

1. **Simple prerequisites and repository download:** Explain only what the user needs before setup and how to clone the project.
2. **Automated setup:** Provide a Windows setup script that checks prerequisites, creates/uses the project virtual environment, installs dependencies, and reports actionable errors.
3. **Secure configuration:** Generate a strong secret key when one is not already configured, persist it safely, and never overwrite an existing key without an explicit recovery process.
4. **Safe database initialization:** Create the SQLite database and required tables without deleting or resetting an existing database.
5. **First-run setup UI:** Guide the user through institution registration and creation of the initial Administrator account.
6. **Easy application lifecycle:** Provide straightforward start/stop/restart scripts or shortcuts using a suitable non-debug server.
7. **LAN access:** Show the host computer's local address and explain same-network access and any required firewall approval in clear, safe language.
8. **Scheduled backups:** Allow the user to select daily, weekly, or monthly backups; report failures; and use a predictable, protected backup location.
9. **Backup verification and restore:** Verify backup integrity and test restoration to a separate location without overwriting the active database.
10. **User-focused documentation:** Keep the README short and task-oriented. Developer-only diagnostic commands belong in troubleshooting or maintenance notes, not in the main user path.

## 3. Definition of Done

- [ ] A new Windows user can check prerequisites, clone the repository, and run one setup script.
- [ ] Setup checks the environment, installs dependencies, and displays clear actionable errors if a step fails.
- [ ] The secret key is generated only when needed, persisted securely, and retained across restarts and reruns.
- [ ] Database initialization is safe and does not overwrite an existing database.
- [ ] A browser-based first-run flow creates the institution and initial Administrator account.
- [ ] First-run setup is disabled or protected after successful completion.
- [ ] The user can start and stop the application with simple scripts or shortcuts.
- [ ] The application uses a suitable non-debug server for LAN access.
- [ ] Authorized devices on the same intended LAN can access the application, with clear host-address guidance.
- [ ] The user can configure daily, weekly, or monthly backups and can identify backup success or failure.
- [ ] A backup can be verified and restored to a separate test location.
- [ ] Existing authentication and regression tests continue to pass.
- [ ] A clean-environment walkthrough confirms the documented user workflow.

## 4. Phase plan and tracking

### Phase 1 - Installation foundation and prerequisites

**Objective:** Establish the supported Windows environment and make initial installation as close to a one-script workflow as practical.

**Planned work**
- [x] Confirm the current development environment: Windows, Python 3.12.2, Git 2.47.0.
- [x] Update README prerequisites to identify Windows 10/11 as the primary target and mark macOS/Linux as unverified.
- [x] Add a link to this Sprint 4 document in the README.
- [x] Verify dependency installation in the current virtual environment.
- [x] Verify the existing test suite: 51 tests passed.
- [x] Verify Flask can load the application and register routes once `SECRET_KEY` is available.
- [x] Design and implement the user-facing setup script (`setup.ps1`).
- [x] Test the setup script from a clean project copy with a newly created virtual environment.
- [x] Verify Flask initialization and the first-run setup page in the clean copy.
- [x] Ensure the main README prerequisites and setup guidance are documented.

**Files inspected or updated:** `README.md`, `requirements.txt`, `app/__init__.py`, `app/setup.py`, `scripts/initialize_database.py`, `setup.ps1`, and related tests.

**Verification evidence**
- `python -m pip check` — no broken requirements found in the original environment.
- `python -m pytest -q` — 47 passed in 8.29 seconds in the original environment.
- `.\.venv\Scripts\python.exe -m pytest -q` — 47 passed in 18.83 seconds in the clean project copy.
- `.\setup.ps1` — completed successfully in the original project environment.
- `.\setup.ps1` — created a new virtual environment and installed dependencies in the clean project copy.
- Flask test client — application created successfully; `/setup/` returned HTTP 200 in the clean copy.
- The clean copy excluded the original `instance` directory and existing database.
- `git ls-files "*.db" "*.sqlite" "*.sqlite3" ".env" ".env.*"` — no matching database or environment files tracked.

**Limitations**
- The clean-copy test used the existing Windows user-level `SECRET_KEY`; a separate Windows user or machine has not been tested.
- Missing-prerequisite and dependency-installation failure scenarios have not been deliberately tested.
- Database initialization and first-run workflow testing remain part of subsequent phases.

**Status:** Complete

**Notes / decisions:** Windows 10/11 remains the primary target. Python 3.12.2 and Git 2.51.0 are the tested versions. Phase 1 establishes the installation foundation; safe database initialization, first-run workflow hardening, lifecycle scripts, LAN guidance, and backups remain tracked in later phases.

### Phase 2 - Secure automated setup and database initialization

**Objective:** Make setup configure the application safely without requiring the user to understand environment variables or database commands.

**Planned work**
- [x] Create a setup script that checks required tools and reports understandable errors.
- [x] Create or reuse the virtual environment and install dependencies.
- [x] Generate and persist a strong secret key only if one is not already configured.
- [ ] Ensure the key is available to application start scripts and survives terminal/session changes.
- [x] Initialize SQLite and create required tables safely.
- [x] Never delete, reset, or replace an existing database as part of ordinary setup.
- [x] Keep secrets and local databases excluded from version control.
- [x] Verify setup in the existing environment and a clean project copy.
- [x] Verify rerunning setup preserves the existing user-level secret key.
- [x] Test dependency-installation failure and confirm setup exits with code `1`.
- [x] Test missing-Python and missing-Git scenarios in controlled simulations; both exit with code `1`.
- [ ] Verify setup under a separate Windows user or machine (not yet tested).

**Files to inspect or update:** `app/__init__.py`, `app/extensions.py`, `app/models.py`, `.gitignore`, `setup.ps1`, and related tests.

**Verification evidence**
- `.\setup.ps1` completed successfully in the actual project and a temporary clean project copy.
- Setup correctly rejected execution outside the project root.
- Dependency-installation failure produced an error message and exit code `1` in the temporary copy.
- Restored `requirements.txt` after failure testing and verified its hash matched the backup.
- Confirmed the actual project database still contained 1 institution and 3 users; no reset was performed.
- Git tracking checks found no tracked database or environment-secret files.
- Full project test suite previously passed: `51 passed in 9.23s` on 2026-10-25.
- In the isolated Phase 3 test copy, dependencies installed successfully and `pip check` reported `No broken requirements found`.
- The isolated test copy successfully initialized its own database and served the first-run page with HTTP 200.
- Controlled missing-Python simulation returned exit code `1`.
- Controlled missing-Git simulation returned exit code `1`.
- Latest full regression suite: `52 passed in 20.64s`.

**Status:** Complete, with separate-user verification outstanding

**Notes / decisions:** The setup script, safe rerun behavior, dependency-failure handling, and controlled missing-Python/Git simulations have been verified. The isolated copy was used for manual first-run testing; its database is separate from the actual project database. Verification under a separate Windows user or machine remains outstanding. Lifecycle secret-key loading is documented and checked in Phase 4.

### Phase 3 - First-run institution and Administrator setup

**Objective:** Complete initial configuration through a browser UI.

**Planned work**
- [x] Detect whether first-run setup is required.
- [x] Provide a setup UI for institution details and initial Administrator credentials.
- [x] Validate required fields and reject invalid submissions with clear messages.
- [x] Hash the Administrator password before storage.
- [x] Make setup one-time and prevent unauthorized reinitialization after completion.
- [x] Test successful setup, invalid inputs, duplicate submissions, and attempts to repeat setup.
- [x] Manually verify institution and Administrator creation, followed by successful login in an isolated test environment.
- [x] Test simultaneous setup submissions and verify the local-only restriction through automated tests.

**Files inspected or updated:** `app/setup.py`, `app/templates/setup/`, `app/models.py`, `tests/test_setup.py`, and `tests/test_initialize_database.py`.

**Verification evidence**
- Automated tests cover setup-page access, rejection of non-local requests, existing-user protection, Administrator creation, password validation, and repeat submissions.
- Confirmed that the user ID is the primary key and email addresses have a database uniqueness constraint.
- The first-run page loaded successfully in the isolated test copy with HTTP 200.
- Manually submitted the first-run form to create a test institution and Administrator; the application redirected to the sign-in page.
- Manually signed in with the test Administrator credentials; the authenticated home page returned HTTP 200.
- Requested `/setup/` again after setup completed. The server returned HTTP 403, and the UI displayed that EduAnalytics was already set up.
- The isolated test-copy suite passed: `51 passed in 9.14s`.
- Latest focused setup tests passed: `9 passed in 4.04s`.
- Latest full regression suite passed: `52 passed in 20.64s`.
- A concurrent two-thread test verified that simultaneous setup requests resulted in one successful setup response and one HTTP 403 response, with only one initial Administrator created.
- The setup lock coordinates requests within a single Python process. Multi-process concurrency has not been verified.
- The local-only restriction has automated test coverage; behavior under the eventual deployment configuration remains to be verified.

**Status:** Complete — core implementation and automated verification passed; deployment-specific checks remain outstanding.

**Notes / decisions:** The browser-based first-run flow passed manual verification for initial registration, successful login, and repeat-setup protection. Manual testing used a disposable database in `EduAnalytics-Phase3-Manual`, not the actual project database. The concurrency test covers requests within one Python process only. Verify the local-only restriction under the intended deployment configuration before shared/LAN deployment.

### Phase 4 - Easy start, stop, and restart

**Objective:** Let users run the application without remembering terminal commands.

**Planned work**
- [x] Choose the supported application entry point and server: `app:create_app` served by Waitress.
- [x] Add Windows `start.ps1` and `stop.ps1` scripts. A separate `restart.ps1` is optional; users can restart with `.\stop.ps1` followed by `.\start.ps1`.
- [x] Ensure the start script loads the existing persistent user-level `SECRET_KEY` without printing or replacing it.
- [x] Use Waitress instead of Flask's development server; debug mode is not enabled by the lifecycle scripts.
- [x] Display the local URL and useful startup and failure messages.
- [x] Detect an already-running managed instance and reject duplicate starts.
- [x] Verify startup, duplicate-start prevention, shutdown, and a subsequent start/stop cycle.
- [x] Verify database row counts remain unchanged across a start/stop cycle.
- [x] Review the README and confirm the start/stop instructions are accurate and complete.

**Files inspected or updated:** `README.md`, `app/__init__.py`, `requirements.txt`, `setup.ps1`, `start.ps1`, and `stop.ps1`.

**Verification evidence**
- `python -m waitress --help` — Waitress is installed and its CLI options are available.
- `.\start.ps1` — started successfully; `http://127.0.0.1:5000` returned HTTP 200.
- A second `.\start.ps1` while the server was running was rejected with an already-running message and PID.
- `.\stop.ps1` — stopped the managed server successfully.
- A request to `http://127.0.0.1:5000` after shutdown timed out, as expected.
- A subsequent start and stop cycle both completed successfully.
- Checked the Windows user-level environment and confirmed `SECRET_KEY` is configured; its value was not printed.
- Read-only database checks before and after the lifecycle cycle returned the same row counts: `institution` — 1 row; `users` — 3 rows.
- Database row-count persistence is verified. Individual record contents were not compared.
- No `restart.ps1` has been created; restarting uses the existing stop and start scripts.

**Status:** Complete - lifecycle checks and README review passed. LAN deployment and backup/recovery remain in later phases.

**Notes / decisions:** Waitress is used on `127.0.0.1:5000` during Phase 4. LAN binding and second-device access are reserved for Phase 5. The start script reads the existing process-level `SECRET_KEY` first, then falls back to the Windows user-level key; it does not generate a replacement. The persistent key's existence was verified, but its exact value was not independently compared across restarts. Database row counts remained unchanged during the tested lifecycle cycle. A separate restart script is optional and is not required for the current workflow.

### Phase 5 - LAN access and deployment guidance

**Objective:** Make access from authorized devices on the same local network easy to understand and use.

**Planned work**
- [x] Add configurable Waitress binding through `EDUANALYTICS_HOST`, retaining `127.0.0.1` as the default and keeping debug mode disabled in the managed lifecycle workflow.
- [x] Document how to find the host computer's active LAN IPv4 address.
- [ ] Display the actual LAN URL (`http://<HOST-PC-IP>:5000`) in the `start.ps1` output when LAN binding is enabled.
- [x] Document same-network requirements and safe firewall guidance; no firewall rules were created automatically.
- [x] Test access from a second authorized device.
- [x] Document that the host's private IP can change on another network and that cross-network portability has not been tested.

**Verification evidence**
- Default mode: with `EDUANALYTICS_HOST` cleared from the current PowerShell process, `.\start.ps1` started successfully, `http://127.0.0.1:5000/` returned HTTP 200, `.\stop.ps1` stopped the server, and `.eduanalytics.pid` was removed.
- LAN mode: set `$env:EDUANALYTICS_HOST = "0.0.0.0"` in the current PowerShell session and ran `.\start.ps1`. Startup succeeded; local HTTP access returned 200; `Get-NetTCPConnection -State Listen -LocalPort 5000` showed `0.0.0.0` in `Listen` state.
- Host network: active Wi-Fi adapter reported private IPv4 address `192.168.1.20` and gateway `192.168.1.1`.
- Second-device test: another authorized device on the same Wi-Fi network loaded the EduAnalytics sign-in page at `http://192.168.1.20:5000`. The sign-in page also loaded on the host.
- Cleanup: `.\stop.ps1` stopped the LAN-bound server, and `EDUANALYTICS_HOST` was removed from the current PowerShell process environment. The next startup therefore uses the safe default `127.0.0.1` unless an override is set.

**Status:** In progress — configurable binding and second-device access verified; startup display of the host's actual LAN URL remains outstanding.

**Notes / decisions:** `0.0.0.0` is a listening address, not an address clients should open. It binds all IPv4 interfaces, so use it only on a trusted network and review firewall scope rather than disabling the firewall. No firewall rules were added. A successful test on Wi-Fi `192.168.1.0/24` does not establish portability to another network or production readiness. The server was stopped after the test, and the temporary process-level override was cleared.

### Phase 6 - Scheduled backup and recovery

**Objective:** Make regular backups easy to configure and recovery safe to test.

**Planned work**
- [ ] Choose a predictable backup folder and explain how to protect access to it.
- [ ] Provide daily, weekly, and monthly backup schedule options.
- [ ] Implement or configure scheduling using a reliable Windows mechanism.
- [ ] Create timestamped backups without exposing sensitive data.
- [ ] Report backup success and failure in a way users can understand.
- [ ] Verify backup integrity and avoid copying an inconsistent live SQLite database.
- [ ] Test restoration to a separate location or database.
- [ ] Document recovery steps and what to do if a scheduled backup fails.
- [ ] Confirm the backup schedule survives a restart and explain any requirement for the host computer to be on.

**Files to inspect or update:** Existing backup scripts, `scripts/`, `README.md`, and any backup UI or configuration added.

**Verification evidence:** Record selected schedule, backup location, integrity result, restore-test location, and checks performed. Avoid including real credentials or sensitive records in this document.

**Status:** Not started
**Notes / decisions:** _Add during implementation._

### Phase 7 - End-to-end testing and user documentation

**Objective:** Validate the complete experience from a fresh checkout through normal operation and recovery.

**Planned work**
- [ ] Run the full automated test suite.
- [ ] Confirm authentication and authorization tests still pass.
- [ ] Test setup from a clean environment.
- [ ] Test first-run institution and Administrator creation.
- [ ] Test start, stop, restart, and LAN access.
- [ ] Test daily, weekly, and monthly backup configuration as practical.
- [ ] Test backup verification and restoration to a separate target.
- [ ] Review the README as a non-technical user and remove unnecessary developer steps from the primary path.
- [ ] Review all Definition of Done items and mark only verified items complete.

**Verification evidence:** _Add test commands, results, and final manual checks._

**Status:** Not started
**Notes / decisions:** _Add during implementation._

## 5. Implementation log

Add a dated entry whenever a phase is implemented, tested, or deliberately deferred.

| Date | Phase | Change or decision | Verification / outcome |
|---|---|---|---|
| 2026-10-25 | Planning | Created Sprint 4 tracking document. | Implementation not started. |
| 2026-10-25 | Phase 1 | Implemented and verified `setup.ps1`; tested setup in the existing environment and a clean project copy. | 47 tests passed in both environments; setup completed in both; clean-copy Flask app initialized and `/setup/` returned HTTP 200. Existing database excluded from the clean copy. Separate-user and deliberate failure-scenario testing remain outstanding. |
| 2026-10-25 | Phases 2–3 | Continued setup verification in an isolated temporary copy; manually completed first-run registration, Admin login, and repeat-setup check. | Dependencies installed; `pip check` reported no broken requirements; repeat setup returned HTTP 403; full suite passed with 51 tests in 9.14 seconds. Missing-prerequisite, separate-user, concurrency, and deployment-specific checks remain open. |
| 2026-10-26 | Phases 2–3 | Verified prerequisite failure handling and first-run setup concurrency; updated setup tests. | Missing-Python/Git simulations returned exit code 1; focused setup suite passed 9 tests; full suite passed 52 tests in 20.64 seconds. Separate-user and multi-process deployment checks remain outstanding. |
| 2026-10-26 | Phase 5 | Added configurable LAN binding through `EDUANALYTICS_HOST` and tested second-device access. | Default localhost lifecycle passed; LAN mode listened on `0.0.0.0:5000`; host `192.168.1.20` served the sign-in page to a second device on the same Wi-Fi; LAN server stopped and temporary override cleared. Startup display of the actual LAN URL remains outstanding. |

## 6. Issues and deferred work

| Item | Reason / risk | Next action | Status |
|---|---|---|---|
| Current terminal may not load persistent `SECRET_KEY` | A user-level environment variable may be missing from an already-open PowerShell session. | Continue using the start script's process-level then user-level key lookup; perform separate-user verification before shared deployment. | Resolved for the tested local workflow; separate-user verification pending |
| Verify external backup access permissions | Backup existence and integrity do not establish that access is appropriately restricted. | Review and verify folder permissions before using real institutional data. | Pending |
| Display the actual LAN URL at startup | The script reports the listening host but does not yet resolve and display the host's private LAN IPv4 URL. | Add a safe LAN URL display to `start.ps1` and verify it with LAN binding enabled. | Pending |
| Test LAN portability on a different network | A successful test on one Wi-Fi network does not prove portability to another. | Test when the target network is available and document any configuration changes. | Deferred |

Add new issues here as they arise.

## 7. Security and safety notes

- Never commit a real secret key, password, production database, or sensitive backup.
- Generate a strong secret key only when needed, persist it safely, and make sure start scripts can load it consistently; do not generate a different key on every application launch.
- Setup scripts must be safe to rerun and must not delete or reset an existing database.
- Do not expose Flask debug mode on the LAN.
- Restrict initial setup so it cannot be used to create or replace the initial Administrator after setup is complete.
- Test database restoration against a separate target; do not experiment on the working database.
- Do not use real institutional data until storage location and access permissions have been reviewed.

## 8. Completion summary

Complete this section at the end of the sprint.

- **Final status:** _In progress - Phases 1-4 complete to their documented scope; Phase 5 LAN binding and same-network access verified, with LAN URL display and Phase 6 backup/recovery still outstanding._
- **Definition of Done:** _Not yet fully verified; deployment-specific checks remain._
- **Automated tests:** Latest recorded full suite: `52 passed in 20.64s` on 2026-10-26. Rerun after the current Phase 5 script edits to verify the working copy.
- **Known limitations:** LAN access was verified only on one Wi-Fi network; the private host IP can change, startup does not yet display the actual LAN URL, and production/cross-network deployment has not been verified. Backup scheduling and recovery remain outstanding.
- **Commit(s):** _Add relevant commit hashes_
