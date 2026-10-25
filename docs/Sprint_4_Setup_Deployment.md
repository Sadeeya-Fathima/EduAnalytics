# Sprint 4 â€” Setup & Deployment

**Project:** EduAnalytics
**Sprint goal:** Make EduAnalytics straightforward for a non-technical Windows user to install, configure, start, access over a local network, maintain, and back up securely.
**Status:** Planned â€” implementation and verification are tracked phase by phase.
**Target platform:** Windows 10/11 (primary target; other operating systems are unverified).
**Last updated:** 2026-10-25

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

### Phase 1 â€” Installation foundation and prerequisites

**Objective:** Establish the supported Windows environment and make initial installation as close to a one-script workflow as practical.

**Planned work**
- [x] Confirm the current development environment: Windows, Python 3.12.2, Git 2.47.0.
- [x] Update README prerequisites to identify Windows 10/11 as the primary target and mark macOS/Linux as unverified.
- [x] Add a link to this Sprint 4 document in the README.
- [x] Verify dependency installation in the current virtual environment.
- [x] Verify the existing test suite: 39 tests passed.
- [x] Verify Flask can load the application and register routes once `SECRET_KEY` is available in the current terminal session.
- [ ] Design and implement the user-facing setup script.
- [ ] Test the setup script from a clean checkout/environment where practical.
- [ ] Ensure the main README does not require users to manually run developer-oriented setup commands.

**Files to inspect or update:** `README.md`, `requirements.txt`, `.gitignore`, `app/__init__.py`, and new Windows setup script(s).

**Verification evidence so far**
- `python -m pip check` â€” no broken requirements found.
- `python -m pytest -q` â€” 39 passed in 17.55 seconds.
- `python -m pip install -r requirements.txt` â€” dependencies already satisfied.
- `python -m flask --app app:create_app routes` â€” routes registered successfully after loading the existing persistent `SECRET_KEY` into the current PowerShell session.
- The current terminal did not automatically have the persistent user-level `SECRET_KEY` loaded. The eventual setup/start workflow must handle this clearly and reliably without generating a new key unnecessarily.
- These checks were run in the existing environment; a clean-clone setup test has not yet been completed.

**Status:** In progress
**Notes / decisions:** Windows 10/11 is the initial target. Python 3.12.2 and Git 2.47.0 are the versions tested so far; do not claim other operating systems or versions are verified.

### Phase 2 â€” Secure automated setup and database initialization

**Objective:** Make setup configure the application safely without requiring the user to understand environment variables or database commands.

**Planned work**
- [ ] Create a setup script that checks required tools and reports understandable errors.
- [ ] Create or reuse the virtual environment and install dependencies.
- [ ] Generate and persist a strong secret key only if one is not already configured.
- [ ] Ensure the key is available to application start scripts and survives terminal/session changes.
- [ ] Initialize SQLite and create required tables safely.
- [ ] Never delete, reset, or replace an existing database as part of ordinary setup.
- [ ] Keep secrets and local databases excluded from version control.
- [ ] Test first setup, rerunning setup, missing prerequisites, and failure recovery with a disposable environment/database.

**Files to inspect or update:** `app/__init__.py`, `app/extensions.py`, `app/models.py`, `.gitignore`, and new setup/configuration scripts.

**Verification evidence:** _Add commands, test results, and observed database state._

**Status:** Not started
**Notes / decisions:** _Add during implementation._

### Phase 3 â€” First-run institution and Administrator setup

**Objective:** Complete initial configuration through a browser UI.

**Planned work**
- [ ] Detect whether first-run setup is required.
- [ ] Provide a setup UI for institution details and initial Administrator credentials.
- [ ] Validate required fields and reject invalid submissions with clear messages.
- [ ] Hash the Administrator password before storage.
- [ ] Make setup one-time and prevent unauthorized reinitialization after completion.
- [ ] Test successful setup, invalid inputs, duplicate submissions, and attempts to repeat setup.

**Files to inspect or update:** `app/auth/`, `app/admin/`, `app/templates/`, `app/models.py`, and tests as appropriate.

**Verification evidence:** _Add test results and manual verification notes._

**Status:** Not started
**Notes / decisions:** _Add during implementation._

### Phase 4 â€” Easy start, stop, and restart

**Objective:** Let users run the application without remembering terminal commands.

**Planned work**
- [ ] Choose the supported application entry point and server.
- [ ] Add simple Windows start/stop/restart scripts or shortcuts.
- [ ] Ensure the start script loads the configured secret key and required settings.
- [ ] Use a suitable non-debug server for LAN use.
- [ ] Display a clear local URL and helpful startup/failure messages.
- [ ] Handle an already-running instance and shutdown safely.
- [ ] Verify settings and data persist across restarts.

**Files to inspect or update:** `README.md`, entry-point files, and Windows lifecycle scripts.

**Verification evidence:** _Add startup, shutdown, restart, and persistence test results._

**Status:** Not started
**Notes / decisions:** _Add during implementation._

### Phase 5 â€” LAN access and deployment guidance

**Objective:** Make access from authorized devices on the same local network easy to understand and use.

**Planned work**
- [ ] Bind the server to the intended LAN interface without enabling debug mode.
- [ ] Show or explain how to find the host computer's LAN address.
- [ ] Display the address users should open on another device.
- [ ] Explain same-network requirements and firewall prompts in plain language.
- [ ] Test access from a second authorized device.
- [ ] Document known limitations when moving to a different network.

**Verification evidence:** Record the host configuration, client device used, and observed result. Do not claim cross-network portability until it has been tested.

**Status:** Not started
**Notes / decisions:** _Add during implementation._

### Phase 6 â€” Scheduled backup and recovery

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

### Phase 7 â€” End-to-end testing and user documentation

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
| 2026-10-25 | Phase 1 | Confirmed Windows/Python/Git environment, dependency health, Flask route loading, and existing test baseline; updated README prerequisites and Sprint 4 link. | `pip check` clean; 39 tests passed; Flask routes loaded after the existing user-level `SECRET_KEY` was copied into the current terminal session. Clean-environment setup is still pending. |

## 6. Issues and deferred work

| Item | Reason / risk | Next action | Status |
|---|---|---|---|
| Current terminal may not load persistent `SECRET_KEY` | A user-level environment variable existed, but it was missing from the already-open PowerShell session, so Flask startup failed until the value was loaded into that session. | Ensure setup/start scripts reliably load the persistent key and explain any session requirements without exposing the value or generating a replacement unnecessarily. | Open |
| Verify external backup access permissions | Backup existence and integrity do not establish that access is appropriately restricted. | Review and verify folder permissions before using real institutional data. | Pending |
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

- **Final status:** _In progress_
- **Definition of Done:** _Not yet verified_
- **Automated tests:** _Record final result_
- **Known limitations:** _Record remaining limitations_
- **Commit(s):** _Add relevant commit hashes_
