# Sprint 4 - Setup & Deployment

**Project:** EduAnalytics
**Sprint goal:** Make EduAnalytics straightforward for a non-technical Windows user to install, configure, start, access over a local network, maintain, and back up securely.
**Status:** Sprint 4 implementation and verification are complete for the agreed project scope, with limitations recorded. The full test suite, clean-copy walkthrough, LAN test, and backup/recovery checks passed. Existing backup-folder permissions are accepted for the current personal development PC because the listed local accounts are trusted; effective access for every account and access path has not been exhaustively verified. The final local diff and Git checks remain the last pre-commit steps. Separate-user/machine verification, cross-network testing, and production deployment remain unverified. Automated backup scheduling is intentionally deferred.
**Target platform:** Windows 10/11 (primary target; other operating systems are unverified).
**Last updated:** 2026-10-28

---

## 1. Sprint objective

A user with basic Windows computer skills should be able to:

1. Check a short list of prerequisites and clone the repository.
2. Run **one setup script** that checks the environment, installs dependencies, configures a persistent secret key, and safely initializes the database.
3. Complete a guided first-run setup in the browser to register the institution and create the initial Administrator account.
4. Start and stop EduAnalytics using simple scripts or shortcuts, without remembering Python or Flask commands.
5. Open EduAnalytics on the host computer and access it from authorized devices on the same LAN.
6. Create and verify manual database backups, and follow a tested recovery process. Automated backup scheduling is deferred.

The user-facing workflow should hide routine developer details behind scripts and clear UI instructions. Scripts must give understandable success and failure messages. This document is the working sprint record: mark work complete only after implementation and verification.

## 2. Scope

1. **Simple prerequisites and repository download:** Explain only what the user needs before setup and how to clone the project.
2. **Automated setup:** Provide a Windows setup script that checks prerequisites, creates/uses the project virtual environment, installs dependencies, and reports actionable errors.
3. **Secure configuration:** Generate a strong secret key when one is not already configured, persist it safely, and never overwrite an existing key without an explicit recovery process.
4. **Safe database initialization:** Create the SQLite database and required tables without deleting or resetting an existing database.
5. **First-run setup UI:** Guide the user through institution registration and creation of the initial Administrator account.
6. **Easy application lifecycle:** Provide straightforward start/stop/restart scripts or shortcuts using a suitable non-debug server.
7. **LAN access:** Show the host computer's local address and explain same-network access and any required firewall approval in clear, safe language.
8. **Manual backup and recovery:** Create timestamped backups in a predictable, protected location, verify their integrity, and provide a documented recovery workflow with safety-backup and rollback protections. Automated daily, weekly, or monthly scheduling is deferred.
9. **Backup verification and restore:** Verify backup integrity and test restoration to a separate location without overwriting the active database.
10. **User-focused documentation:** Keep the README short and task-oriented. Developer-only diagnostic commands belong in troubleshooting or maintenance notes, not in the main user path.

## 3. Definition of Done

- [x] The documented Windows setup workflow was completed from an isolated clean copy under the current Windows user; a separate Windows user has not been tested.
- [x] Setup checks prerequisites, installs dependencies, and reports actionable errors; missing-Python, missing-Git, and dependency-failure scenarios were simulated.
- [x] Setup preserves an existing user-level secret key, and the managed start script loads the process-level key first then falls back to the user-level key. Cross-user behavior remains unverified.
- [x] Setup/database initialization checks and reruns did not reset the existing database; database row counts were checked.
- [x] The browser-based first-run flow was manually tested against a disposable database, including institution/Admin creation and successful login.
- [x] Repeat setup was blocked with HTTP 403 after successful setup; automated tests cover this behavior.
- [x] Managed startup and shutdown succeeded in the original project and isolated clean copy; no port-5000 listener remained after shutdown.
- [x] The managed workflow uses Waitress with debug mode disabled.
- [x] A second authorized device on the same Wi-Fi network loaded the sign-in page using the displayed LAN URL.
- [x] Manual backups can be created and integrity-checked; recovery has been tested using disposable databases and a separate temporary database.
- [x] Review the displayed backup-folder ACL entries and record the local access decision: existing permissions are accepted for this personal development PC because the listed local accounts are trusted. This does not prove effective access for every account and access path; review further before using real institutional data.
- [x] Existing authentication and regression tests continue to pass (66 tests passed in the latest full suite).
- [x] An isolated clean-copy walkthrough verified setup, the setup page, managed startup, and clean shutdown. A separate Windows user or machine has not been tested.

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
- `python -m pip check` - no broken requirements found in the original environment.
- `python -m pytest -q` - 47 passed in 8.29 seconds in the original environment.
- `.\.venv\Scripts\python.exe -m pytest -q` - 47 passed in 18.83 seconds in the clean project copy.
- `.\setup.ps1` - completed successfully in the original project environment.
- `.\setup.ps1` - created a new virtual environment and installed dependencies in the clean project copy.
- Flask test client - application created successfully; `/setup/` returned HTTP 200 in the clean copy.
- The clean copy excluded the original `instance` directory and existing database.
- `git ls-files "*.db" "*.sqlite" "*.sqlite3" ".env" ".env.*"` - no matching database or environment files tracked.

**Limitations**
- The clean-copy test used the existing Windows user-level `SECRET_KEY`; a separate Windows user or machine has not been tested.
- Missing-prerequisite and dependency-installation failure scenarios have not been deliberately tested.
- Database initialization and first-run workflow testing remain part of subsequent phases.

**Status:** Complete

**Notes / decisions:** Windows 10/11 remains the primary target. The verified environment reported Python 3.12.2 and Git 2.47.0. A separate clean-copy walkthrough also succeeded on 2026-10-28. Phase 1 establishes the installation foundation; later phases track database initialization, first-run workflow, lifecycle scripts, LAN guidance, and backups.

### Phase 2 - Secure automated setup and database initialization

**Objective:** Make setup configure the application safely without requiring the user to understand environment variables or database commands.

**Planned work**
- [x] Create a setup script that checks required tools and reports understandable errors.
- [x] Create or reuse the virtual environment and install dependencies.
- [x] Generate and persist a strong secret key only if one is not already configured.
- [x] The managed start script loads a process-level `SECRET_KEY` first, then falls back to the persistent Windows user-level key. Separate-user behavior remains unverified.
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
- Latest focused setup tests passed: `10 passed in 1.12s`.
- Latest full regression suite passed: `52 passed in 20.64s`.
- A concurrent two-thread test verified that simultaneous setup requests resulted in one successful setup response and one HTTP 403 response, with only one initial Administrator created.
- The setup lock coordinates requests within a single Python process. Multi-process concurrency has not been verified.
- The local-only restriction has automated test coverage; behavior under the eventual deployment configuration remains to be verified.

**Status:** Complete - core implementation and automated verification passed; deployment-specific checks remain outstanding.

**Notes / decisions:** The browser-based first-run flow passed manual verification for initial registration, successful login, and repeat-setup protection. Manual testing used a disposable database in `EduAnalytics-Phase3-Manual`, not the actual project database. The concurrency test covers requests within one Python process only. Verify the local-only restriction under the intended deployment configuration before shared/LAN deployment.

### Phase 4 - Easy start, stop, and restart

**Objective:** Let users run the application without remembering terminal commands.

**Planned work**
- [x] Choose the supported application entry point and server: `app:create_app` served by Waitress.
- [x] Add Windows `start.ps1` and `stop.ps1` scripts. A separate `restart.ps1` is optional; users can restart with `.\stop.ps1` followed by `.\start.ps1`.
- [x] Harden `stop.ps1` to discover and stop all matching EduAnalytics Waitress processes listening on `0.0.0.0:5000`, including stale or duplicate processes when the PID file is missing or outdated.
- [x] Ensure the start script loads the existing persistent user-level `SECRET_KEY` without printing or replacing it.
- [x] Use Waitress instead of Flask's development server; debug mode is not enabled by the lifecycle scripts.
- [x] Display the local URL and useful startup and failure messages.
- [x] Detect an already-running managed instance and reject duplicate starts.
- [x] Verify startup, duplicate-start prevention, shutdown, and a subsequent start/stop cycle.
- [x] Verify database row counts remain unchanged across a start/stop cycle.
- [x] Review the README and confirm the start/stop instructions are accurate and complete.

**Files inspected or updated:** `README.md`, `app/__init__.py`, `requirements.txt`, `setup.ps1`, `start.ps1`, and `stop.ps1`.

**Verification evidence**
- Duplicate-process recovery: after multiple stale Waitress processes were found listening on port 5000, the updated `stop.ps1` stopped all matching `app:create_app` listeners before a clean single-process restart.
- `python -m waitress --help` - Waitress is installed and its CLI options are available.
- `.\start.ps1` - started successfully; `http://127.0.0.1:5000` returned HTTP 200.
- A second `.\start.ps1` while the server was running was rejected with an already-running message and PID.
- `.\stop.ps1` - stopped the managed server successfully.
- A request to `http://127.0.0.1:5000` after shutdown timed out, as expected.
- A subsequent start and stop cycle both completed successfully.
- Checked the Windows user-level environment and confirmed `SECRET_KEY` is configured; its value was not printed.
- Read-only database checks before and after the lifecycle cycle returned the same row counts: `institution` - 1 row; `users` - 3 rows.
- Database row-count persistence is verified. Individual record contents were not compared.
- No `restart.ps1` has been created; restarting uses the existing stop and start scripts.

**Status:** Complete - lifecycle checks and README review passed. LAN deployment and backup/recovery remain in later phases.

**Notes / decisions:** Waitress is used on `127.0.0.1:5000` during Phase 4. LAN binding and second-device access are reserved for Phase 5. The start script reads the existing process-level `SECRET_KEY` first, then falls back to the Windows user-level key; it does not generate a replacement. The persistent key's existence was verified, but its exact value was not independently compared across restarts. Database row counts remained unchanged during the tested lifecycle cycle. A separate restart script is optional and is not required for the current workflow.

### Phase 5 - LAN access and deployment guidance

**Objective:** Make access from authorized devices on the same local network easy to understand and use.

**Planned work**
- [x] Add configurable Waitress binding through `EDUANALYTICS_HOST`, retaining `127.0.0.1` as the default and keeping debug mode disabled in the managed lifecycle workflow.
- [x] Document how to find the host computer's active LAN IPv4 address.
- [x] Display the actual LAN URL (`http://<HOST-PC-IP>:5000`) in the `start.ps1` output when LAN binding is enabled.
- [x] Document same-network requirements and safe firewall guidance; no firewall rules were created automatically.
- [x] Test access from a second authorized device.
- [x] Document that the host's private IP can change on another network and that cross-network portability has not been tested.

**Verification evidence**
- Default mode: with `EDUANALYTICS_HOST` cleared from the current PowerShell process, `.\start.ps1` started successfully, `http://127.0.0.1:5000/` returned HTTP 200, `.\stop.ps1` stopped the server, and `.eduanalytics.pid` was removed.
- LAN mode: set `$env:EDUANALYTICS_HOST = "0.0.0.0"` in the current PowerShell session and ran `.\start.ps1`. Startup succeeded; local HTTP access returned 200; `Get-NetTCPConnection -State Listen -LocalPort 5000` showed `0.0.0.0` in `Listen` state.
- Host network: active Wi-Fi adapter reported private IPv4 address `192.168.1.20` and gateway `192.168.1.1`.
- Second-device test: another authorized device on the same Wi-Fi network loaded the EduAnalytics sign-in page at `http://192.168.1.20:5000`. The sign-in page also loaded on the host.
- Cleanup: `.\stop.ps1` stopped the LAN-bound server, and `EDUANALYTICS_HOST` was removed from the current PowerShell process environment. The next startup therefore uses the safe default `127.0.0.1` unless an override is set.
- Startup output displayed `http://192.168.1.20:5000/` automatically when LAN binding was enabled.
- A request to the displayed LAN URL returned HTTP 200 on the host computer.

**Status:** Complete - configurable binding, automatic LAN URL display, and second-device access verified.

**Notes / decisions:** `0.0.0.0` is a listening address, not an address clients should open. It binds all IPv4 interfaces, so use it only on a trusted network and review firewall scope rather than disabling the firewall. No firewall rules were added. A successful test on Wi-Fi `192.168.1.0/24` does not establish portability to another network or production readiness. The server was stopped after the test, and the temporary process-level override was cleared.

### Phase 6 - Manual backup and recovery

**Objective:** Provide a predictable manual backup workflow and a cautious, verifiable database recovery process.

**Implementation**
- [x] Choose a predictable backup folder outside the repository and document access-protection requirements.
- [x] Implement a manual command to create timestamped database backups.
- [x] Include the institution name and readable date/time in backup filenames and output.
- [x] Use SQLite's backup API and verify backup integrity.
- [x] Prevent backup creation from silently overwriting an existing file.
- [x] Implement interactive backup selection and explicit confirmation before replacing the live database.
- [x] Filter listed backups to the institution configured in the live database.
- [x] Create a safety backup before recovery and prepare the replacement separately.
- [x] Retain the previous live database as a rollback file after successful replacement.
- [x] Add automated tests for backup creation, backup inspection, integrity validation, staging preparation, database replacement, and cancellation.
- [x] Document manual backup and recovery commands and important data-loss precautions.

**Additional verification completed**
- [x] Inspect the external backup folder's ACL entries without changing permissions.
- [x] Test successful recovery and rollback using disposable SQLite databases on the Windows development environment.
- [x] Restore an actual backup into a separate temporary database and verify its integrity and record counts without changing the live database.
- [x] Initialize the Flask application against the temporary restored database and verify the expected login redirect using the test client.
- [x] Perform a live-database restore, restart the managed application, and verify the homepage returned HTTP 200.
- [x] Verify the integrity of the live database's safety backup and retained rollback file after recovery.

**Accepted decision, outstanding verification, and deferred work**
- [x] Review the displayed ACL entries and accept the existing permissions for this personal development PC because the listed local accounts are trusted. Broader effective access is not exhaustively verified; review it before using real institutional data.
- [ ] Verify setup and operation under a separate Windows user or on a separate machine. The isolated clean-copy walkthrough was completed under the current Windows user.
- [ ] Automated daily, weekly, or monthly scheduling. Intentionally deferred; manual backup commands remain the project decision.

**Files implemented or updated:** `scripts/backup_database.py`, `scripts/restore_database.py`, `tests/test_backup_database.py`, `tests/test_restore_database.py`, `README.md`, and this deployment guide.

**Verification evidence**
- `python .\scripts\backup_database.py` created a timestamped backup outside the repository and reported successful integrity verification.
- `python .\scripts\restore_database.py` listed valid backups for the configured institution; entering `Q` cancelled recovery without making changes.
- `python -m pytest tests/test_restore_database.py -v` — **10 passed in 1.12s** on Windows.
- Restore tests cover backup inspection, corrupt-backup rejection, staging preparation, metadata removal, cancellation without live-file changes, SQLite file replacement, successful recovery with safety-copy retention, rollback after a simulated post-restore verification failure, and preservation of recovery artifacts when rollback replacement itself fails.
- `python -m pytest -v` — **66 passed in 25.16s** on 2026-10-27; latest rerun on 2026-10-28 — **66 passed in 10.74s**.
- `icacls ..\EduAnalytics_Backups` showed inherited entries: `CodexSandboxUsers` with read/execute, and `SYSTEM`, `Administrators`, and the current user with full control. The group contains the trusted local accounts `CodexSandboxOffline` and `CodexSandboxOnline`. The existing permissions are accepted for this personal development PC; no permission changes were made. The ACL listing does not establish effective access for every account and access path.
- A live-database restore was performed on 2026-10-27. The restored database passed SQLite integrity checks, the application restarted successfully, and the homepage returned HTTP 200. The safety backup `EduAnalytics_2026-10-27_11-34-34_379328_AM.db` and rollback file `.eduanalytics_rollback_f278059350a84e38b3327bfc38c11eca.db` both passed SQLite integrity checks. The initial live restore selected a 2026-10-24 backup; a second restore selected the safety backup created by the first operation.
- Separately, the actual backup `EduAnalytics_2026-10-27_11-34-34_379328_AM.db` was restored to a temporary database. Its SQLite integrity check returned `ok`. The restored database contained institution `EduAnalytics`, 1 institution record, 3 users, 0 student records, 0 datasets, and 0 upload-error records. The live database hash was unchanged by this isolated restore-preparation test.
- A Flask application was initialized against the temporary restored database. The test-client request to `/` returned HTTP 302, redirecting to `/auth/login?next=%2F`, as expected for a login-protected homepage. This was an application-level test-client check, not a separate HTTP server test. The temporary test directory was subsequently removed.
- Following live recovery, a separate application startup using `.\start.ps1` returned HTTP 200. `.\stop.ps1` then stopped the managed application cleanly.

**Status:** Manual backup/recovery implementation and automated disposable-database tests are verified. Live-database recovery, restoration into a separate temporary database, application checks, and safety/rollback integrity checks passed. The isolated clean-copy setup walkthrough also passed. Existing backup-folder permissions are accepted for this personal development PC, while broader effective-access verification and separate-user/machine verification remain limitations. Automated scheduling is intentionally deferred.

**Notes / decisions:** The team chose a manual backup workflow rather than scheduled tasks. Recovery replaces the live database with the selected snapshot, so changes made after that snapshot may be lost. The current recovery procedure requires the managed server to appear stopped and warns against other processes accessing the database. Keep safety backups and rollback files until the recovered application and its data have been checked. Do not use real institutional data until backup storage and effective access restrictions have been reviewed.

### Phase 7 - End-to-end testing and user documentation

**Objective:** Verify the complete setup, deployment, backup, and recovery workflow and document the results accurately.

**Implementation and verification checklist**
- [x] Run the complete automated test suite after the backup and recovery implementation (66 passed in 25.16 seconds on 2026-10-27; latest rerun on 2026-10-28 passed 66 tests in 10.74 seconds).
- [x] Verify local server startup, duplicate-start protection, HTTP response, and clean shutdown.
- [x] Verify LAN-mode startup and access from a second authorized device on the same Wi-Fi network.
- [x] Update the README with setup, startup, shutdown, LAN access, manual backup, and recovery instructions.
- [x] Document known limitations and outstanding verification work.
- [x] Perform a clean-copy setup walkthrough using the documented instructions (same Windows user; separate-user/machine verification remains outstanding).
- [x] Delete the existing local database and rerun `setup.ps1`; setup reported successful database initialization.
- [x] Verify the first startup displayed the first-run `/setup/` URL and returned HTTP 200.
- [x] Verify a subsequent startup displayed `/auth/login` and returned HTTP 200 after the application reported setup was complete.
- [x] Verify `stop.ps1` stopped the application successfully after each startup.
- [x] Test successful recovery and rollback using disposable SQLite databases through automated recovery tests.
- [x] Perform a live-database restore and verify post-restore application startup and recovery-artifact integrity.
- [x] Restore the live database from a selected backup, then start the application and verify the homepage returned HTTP 200.
- [x] Restore an actual backup into a separate temporary database and verify its integrity and record counts without changing the live database.
- [x] Initialize the Flask application against the temporary restored database and verify the expected login redirect using the test client.
- [x] Inspect backup-folder ACL entries on the Windows development environment without changing permissions.
- [x] Review the displayed backup-folder ACL entries and record acceptance of the current permissions for this personal development PC; broader effective access remains unverified.
- [ ] Review the final implementation and documentation diffs in the local repository before committing.

**Verification evidence**
- Database-recreation walkthrough on 2026-10-28: after deleting `instance\eduanalytics.db`, `setup.ps1` completed successfully and reported that the database and required tables were initialized. The first startup displayed `http://127.0.0.1:5000/setup/` with HTTP 200; a subsequent startup displayed `http://127.0.0.1:5000/auth/login` with HTTP 200. `stop.ps1` stopped the application after both runs. This test used the current Windows user and Python 3.15.0. The provided logs do not independently document submission of the browser setup form.
- Full automated test suite in the original project: `66 passed in 25.16s` on 2026-10-27.
- Isolated clean-copy setup: `setup.ps1` completed successfully, created a new virtual environment, and installed dependencies while preserving the configured user-level `SECRET_KEY` without printing its value.
- Isolated clean-copy test suite: `66 passed in 23.59s`.
- Flask test client in the isolated copy: `/setup/` returned HTTP 200.
- Managed startup in the isolated copy: `start.ps1` displayed `http://127.0.0.1:5000/` and returned HTTP 200; `stop.ps1` stopped the application successfully, and no listener remained on port 5000.
- Restore-specific suite: `10 passed in 1.12s`.
- Successful disposable-database recovery restored the expected student record, retained a safety backup of the original data, and retained the prior live test database as a rollback file.
- A simulated post-restore verification failure returned an error and restored the original database; the failed restored database was retained for inspection.
- A simulated rollback-replacement failure was tested; the recovery artifacts were preserved and the error was reported.
- Recovery cancellation was verified; entering `Q` made no database changes.
- `icacls ..\EduAnalytics_Backups` was reviewed without changing permissions. `CodexSandboxUsers` has inherited read/execute access and contains the trusted local accounts `CodexSandboxOffline` and `CodexSandboxOnline`; `SYSTEM`, `Administrators`, and the current user have full control. The current permissions are accepted for this personal development PC, but the displayed ACL does not establish effective access for every account and access path.
- Live-database recovery was performed successfully on 2026-10-27. The restored database returned `PRAGMA integrity_check = ok`; the institution was `EduAnalytics`, with 3 users, 0 student records, 0 datasets, and 0 upload-error records. After recovery, `start.ps1` succeeded and the homepage returned HTTP 200; `stop.ps1` then stopped the application cleanly. The safety backup `EduAnalytics_2026-10-27_11-34-34_379328_AM.db` and rollback file `.eduanalytics_rollback_f278059350a84e38b3327bfc38c11eca.db` both passed SQLite integrity checks. The initial live restore selected the 2026-10-24 backup; a second restore selected the safety backup created by the first restore.
- Separately, the actual backup `EduAnalytics_2026-10-27_11-34-34_379328_AM.db` was restored to a temporary database. Its SQLite integrity check returned `ok`. It contained institution `EduAnalytics`, 1 institution record, 3 users, 0 student records, 0 datasets, and 0 upload-error records. The live database hash was unchanged by this isolated restore-preparation test, and the temporary test directory was subsequently removed.
- A Flask application initialized against the temporary restored database. Its test-client request to `/` returned HTTP 302, redirecting to `/auth/login?next=%2F`, as expected for a login-protected homepage. This was an application-level test-client check, not a separate HTTP server test.

**Scope decision:** Automated daily, weekly, or monthly scheduling is intentionally deferred. The current implementation uses manual backup and recovery commands.

**Status:** Implementation and recorded verification are complete for the agreed Sprint 4 scope. Closure decision: accept the existing backup-folder permissions for the current personal development PC because the listed local accounts are trusted; do not claim exhaustive effective-access verification. Separate-user/machine setup, cross-network access, and production deployment remain unverified. Automated backup scheduling is intentionally deferred. Final local diff review and Git checks remain required before any commit.

## 5. Implementation log

Add a dated entry whenever a phase is implemented, tested, or deliberately deferred.

| Date | Phase | Change or decision | Verification / outcome |
|---|---|---|---|
| 2026-10-25 | Planning | Created Sprint 4 tracking document. | Implementation not started. |
| 2026-10-25 | Phase 1 | Implemented and verified `setup.ps1`; tested setup in the existing environment and a clean project copy. | 47 tests passed in both environments; setup completed in both; clean-copy Flask app initialized and `/setup/` returned HTTP 200. Existing database excluded from the clean copy. Separate-user and deliberate failure-scenario testing remain outstanding. |
| 2026-10-25 | Phases 2-3 | Continued setup verification in an isolated temporary copy; manually completed first-run registration, Admin login, and repeat-setup check. | Dependencies installed; `pip check` reported no broken requirements; repeat setup returned HTTP 403; full suite passed with 51 tests in 9.14 seconds. Missing-prerequisite, separate-user, concurrency, and deployment-specific checks remain open. |
| 2026-10-26 | Phases 2-3 | Verified prerequisite failure handling and first-run setup concurrency; updated setup tests. | Missing-Python/Git simulations returned exit code 1; focused setup suite passed 9 tests; full suite passed 52 tests in 20.64 seconds. Separate-user and multi-process deployment checks remain outstanding. |
| 2026-10-26 | Phase 5 | Added configurable LAN binding through `EDUANALYTICS_HOST` and tested second-device access. | Default localhost lifecycle passed; LAN mode listened on `0.0.0.0:5000`; host `192.168.1.20` served the sign-in page to a second device on the same Wi-Fi; LAN server stopped and temporary override cleared. |
| 2026-10-26 | Phase 5 | Added automatic LAN URL display and graceful handling of LAN address detection failures. | Startup displayed `http://192.168.1.20:5000/`; a request to the displayed URL returned HTTP 200; the full regression suite passed with 52 tests. |
| 2026-10-26 | Phase 6 | Implemented manual SQLite backup and interactive database recovery scripts; documented the workflow and chose not to add scheduled tasks. | Initial backup creation and integrity verification succeeded; recovery cancellation made no changes. |
| 2026-10-27 | Phases 6–7 | Fixed explicit SQLite connection closure in recovery tests and added isolated file-swap plus end-to-end success/rollback coverage. Reviewed backup-folder ACL entries without modifying them. | Restore suite: 10 passed in 1.12 seconds. Full original-project suite: 66 passed in 25.16 seconds. Live restore and recovery-artifact integrity checks passed. |
| 2026-10-28 | Phase 7 | Completed an isolated clean-copy walkthrough using the documented setup and lifecycle scripts. | Setup succeeded and created a new virtual environment; isolated-copy suite: 66 passed in 23.59 seconds; `/setup/` returned HTTP 200; managed startup returned HTTP 200; shutdown succeeded and no listener remained on port 5000. This used the same Windows user; separate-user/machine verification and effective-permissions review remain open. |
| 2026-10-28 | Sprint closure decision | Recorded the agreed scope and local backup-folder permission decision; updated current test evidence. | Latest full suite: 66 passed in 10.74 seconds; `git diff --check` reported no issues. Existing ACLs are accepted for the personal development PC because the listed local accounts are trusted. Effective access for every account/path, separate-user/machine setup, cross-network access, and production deployment remain unverified; automated scheduling is deferred. Final local diff/Git checks remain before commit. |
| 2026-10-28 | Phase 7 | Tested first-run routing after deleting and recreating the local database. | `setup.ps1` reported successful initialization; first startup displayed `/setup/` with HTTP 200; subsequent startup displayed `/auth/login` with HTTP 200; shutdown succeeded after both runs. Browser form submission was not independently documented in the supplied logs. Separate-user/machine verification remains outstanding. |



## 6. Issues and deferred work

| Item | Reason / risk | Next action | Status |
|---|---|---|---|
| Current terminal may not load persistent `SECRET_KEY` | A user-level environment variable may be missing from an already-open PowerShell session. | Continue using the start script's process-level then user-level key lookup; perform separate-user verification before shared deployment. | Resolved for the tested local workflow; separate-user verification pending |
| Backup-folder effective access | ACL entries show inherited read/execute access for `CodexSandboxUsers`; the group contains local accounts trusted by the owner. The listing does not prove every effective access path. | Existing permissions are accepted for this personal development PC; review effective access before using real institutional data or deploying elsewhere. | Local decision recorded; broader effective-access verification not exhaustive |
| Display the actual LAN URL at startup | The startup script needed to identify and display the host's private LAN IPv4 address. | Implemented LAN address detection and startup URL display; verified the displayed URL returned HTTP 200. | Complete |
| Test LAN portability on a different network | A successful test on one Wi-Fi network does not prove portability to another. | Test when the target network is available and document any configuration changes. | Deferred |

Add new issues here as they arise.

## 7. Security and safety notes

- Never commit a real secret key, password, production database, or sensitive backup.
- Generate a strong secret key only when needed, persist it safely, and make sure start scripts can load it consistently; do not generate a different key on every application launch.
- Setup scripts must be safe to rerun and must not delete or reset an existing database.
- Do not expose Flask debug mode on the LAN.
- Restrict initial setup so it cannot be used to create or replace the initial Administrator after setup is complete.
- Separate-target restoration has been verified using a temporary database. Continue using disposable targets for future recovery tests; avoid unnecessary experiments on the working database.
- Do not use real institutional data until the storage location and effective access restrictions have been reviewed and verified.

## 8. Completion summary

Complete this section at the end of the sprint.

- **Final status:** Implementation and the recorded verification workflows are complete for the agreed Sprint 4 scope, with limitations documented. The existing backup-folder permissions are accepted for the current personal development PC because the listed local accounts are trusted. This is a scoped local decision, not proof of exhaustive effective-access verification. The final local diff and Git checks remain to be completed before a commit.
- **Definition of Done:** The implementation and verification criteria for the agreed scope are complete. The clean-copy walkthrough passed under the current Windows user; separate-user/machine verification remains outstanding. The ACL entries were reviewed and accepted for this personal development PC, but effective access for every account and access path has not been exhaustively verified. The temporary restored-database application test returned HTTP 302 to the expected login page; live database integrity and record counts were rechecked, and the temporary test directory was removed. Automated scheduling is intentionally deferred.
- **Automated tests:** Latest verified full suite: `66 passed in 10.74s` on 2026-10-28. Restore-specific suite: `10 passed in 1.12s`.
- **Backup/recovery:** Manual backup creation and integrity verification succeeded. Disposable-database recovery and simulated-failure rollback tests passed. A live-database restore was completed; the restored database passed integrity verification, the application returned HTTP 200 after restart, and safety/rollback files passed integrity checks.
- **Known limitations:** LAN access was verified on one Wi-Fi network; the private host IP can change. Separate-user/machine setup, cross-network access, and production deployment have not been verified. Existing backup-folder permissions are accepted for this personal development PC, but effective access for every account and access path has not been exhaustively verified. Do not use real institutional data until access controls are appropriately reviewed.
- **Commit(s):** `53473d4` — Complete Sprint 4 setup and LAN deployment. The backup/recovery and later documentation changes listed in this guide remain uncommitted as of the last recorded status check.
