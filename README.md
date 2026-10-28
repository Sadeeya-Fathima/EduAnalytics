# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project designed to help teachers and administrators explore student academic performance using data management, analytics, and interactive dashboards.

The project is being developed incrementally, with an emphasis on structured data, meaningful visualizations, and a maintainable Flask application.

## Project Objectives

- Analyze student academic performance using structured datasets.
- Visualize academic results and compare student groups.
- Filter and explore data using relevant academic attributes.
- Import student records from CSV files.
- Export filtered data for further analysis.

## Features

### Implemented

- **Authentication:** Administrator and educator login with password-hash verification.
- **Educator management:** Administrator-controlled educator account creation, activation, and deactivation.
- **Access control:** Role-based protection for administrator routes and rejection of inactive accounts.
- **Setup and deployment:** Windows setup script (`setup.ps1`), browser-based first-run Administrator setup, and application start/stop scripts (`start.ps1` and `stop.ps1`).
- **Application lifecycle:** Waitress-based startup, duplicate-instance prevention, and managed shutdown.
- **Security:** CSRF protection and persistent application secret-key handling.
- **Manual database backup and recovery:** Timestamped SQLite backups, integrity verification, and an interactive recovery workflow with safety-backup and rollback protections.
- **Local-network testing:** Optional LAN binding and automatic display of the detected LAN URL.

### Planned

- **CSV data import:** Upload, preview, validate, and import student data.
- **Analytics dashboard:** Summary statistics, charts, filters, and group comparisons.
- **Data export:** Export filtered records as CSV.
- **Import history:** Track dataset imports.

> EduAnalytics is under active development. Features listed as planned are not yet available as completed functionality.

## Technology Stack

- **Backend:** Python, Flask
- **Data analysis:** Pandas, NumPy
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Charts:** Plotly.js
- **Testing:** pytest
- **Version control:** Git and GitHub

## Current Implementation

The following components have been implemented:

- Flask application factory and application configuration.
- SQLAlchemy models and relationships for institutions, users, datasets, student records, and upload errors.
- SQLite foreign-key enforcement and safe database initialization.
- Browser-based first-run setup for creating the institution and initial Administrator account.
- Authentication, password-hash verification, session handling, and logout.
- Rejection of inactive accounts and role-based protection for administrator routes.
- Administrator-controlled educator account creation, activation, and deactivation.
- CSRF protection for forms and state-changing requests.
- Shared home-page template and extracted CSS for the home and educator-management pages.
- Windows setup script (`setup.ps1`) and lifecycle scripts (`start.ps1` and `stop.ps1`).
- Waitress-based startup, duplicate-instance prevention, and managed shutdown.
- Persistent user-level `SECRET_KEY` loading by the start script without printing or replacing the key.
- Configurable LAN binding through `EDUANALYTICS_HOST` and automatic LAN URL display when LAN mode is enabled.
- Manual SQLite backup and interactive recovery scripts, with automated tests for recovery and rollback scenarios.
- Automated regression tests for authentication, authorization, educator management, setup, and database behavior.

The latest verified full automated test suite passed **66 tests in 10.74 seconds** on 2026-10-28. The restore-specific suite passed **10 tests in 1.12 seconds**. An isolated clean-copy walkthrough also passed: setup created a new virtual environment, the setup page returned HTTP 200, managed startup returned HTTP 200, and shutdown completed with no listener remaining on port 5000. This walkthrough used the same Windows user; a separate-user or separate-machine walkthrough has not been completed. See [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) for detailed evidence and remaining verification work.

CSV import, academic analytics dashboards, charts, filtering, and data export remain planned features.

## Dataset

The project plans to use the UCI Student Performance dataset, focusing on either the mathematics or Portuguese language dataset.

Selected attributes include:

- `G1` — First-period grade
- `G2` — Second-period grade
- `G3` — Final grade
- `studytime` — Weekly study-time category
- `absences` — Number of school absences

In the selected UCI dataset, grades are recorded on a scale from 0 to 20. The `studytime` attribute represents categories of weekly study time rather than exact hours.

## Project Documentation

- [MVP Scope and Requirements Specification](docs/MVP_Scope_and_Requirements.md) — Approved features, technology stack, dataset, development plan, team responsibilities, and acceptance criteria.
- [Sprint 3 — Authentication and Educator Account Management](docs/Sprint_3_Authentication.md) — Authentication and authorization implementation, educator management, regression tests, manual verification, and related closure notes.
- [Sprint 4 — Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) — Setup automation, first-run configuration, lifecycle scripts, LAN access, manual backup/recovery, verification evidence, and outstanding limitations.

## Setup and Deployment

> **Sprint 4 closure decision: implementation and verification are complete for the agreed project scope, with limitations recorded.** Setup, first-run configuration, lifecycle scripts, LAN access, and manual database backup/recovery are implemented and tested. The latest full suite passed 66 tests in 10.74 seconds on 2026-10-28; all 10 restore-specific tests passed in the focused run. A live database restore and post-restore application check also passed. Existing backup-folder permissions are accepted for the current personal development PC because the listed local accounts are trusted; effective access for every account and access path has not been exhaustively verified. Separate-user/machine, cross-network, and production deployment checks remain outstanding. Automated backup scheduling is intentionally deferred.

### Prerequisites

- Windows 10 or Windows 11 (primary target; macOS and Linux have not been verified)
- Python 3.12 (tested with Python 3.12.2)
- Git (tested with Git 2.47.0)
- Visual Studio Code (recommended, not required)

### 1. Download the project

Open PowerShell in the folder where you want the project and run:

```powershell
git clone https://github.com/Sadeeya-Fathima/EduAnalytics.git
cd EduAnalytics
```

### 2. Setup and deployment workflow

The intended end-user workflow is:

1. Open PowerShell in the project root and run `.\setup.ps1`.
2. Open the application in a browser and follow the first-run steps to create the institution and initial Administrator account.
3. Start or stop the application using `.\start.ps1` and `.\stop.ps1`.
4. By default, access the application at `http://127.0.0.1:5000` on the host computer. For trusted same-network LAN testing, follow [LAN access](#lan-access-on-a-trusted-local-network).
5. Create manual database backups with `python .\scripts\backup_database.py`. Use `python .\scripts\restore_database.py` for the interactive recovery procedure when needed. Automated backup scheduling is not implemented.

**Implementation status:** The managed scripts use Waitress, default to localhost, and support an optional `EDUANALYTICS_HOST` override. Localhost lifecycle checks passed; LAN binding and second-device sign-in-page access were verified on one Wi-Fi network.

**Current limitations:** Access on other networks and production deployment have not been verified. Manual backup and interactive recovery passed automated tests using disposable databases, including simulated failure and rollback scenarios. A live restore was also performed: the database passed integrity checks, the application returned HTTP 200 after recovery, and the safety backup and rollback file passed SQLite integrity checks. The backup folder's ACL entries were inspected and the existing permissions are accepted for this personal development PC because the listed local accounts are trusted. Effective access for every account and access path has not been exhaustively verified; review this before using real institutional data. Automated backup scheduling is intentionally deferred. Refer to [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) for current status.

### LAN access on a trusted local network

LAN access is optional. The default is **localhost only**, meaning the app is available on the host computer at `http://127.0.0.1:5000`.

To test access from another authorized device on the **same trusted Wi-Fi or wired LAN**, open PowerShell in the project root on the host computer and run:

```powershell
$env:EDUANALYTICS_HOST = "0.0.0.0"
.\start.ps1
```

Find the host computer's private IPv4 address:

```powershell
Get-NetIPConfiguration |
    Where-Object {
        $_.IPv4DefaultGateway -ne $null -and
        $_.NetAdapter.Status -eq "Up"
    } |
    Select-Object InterfaceAlias,
        @{Name="IPv4Address"; Expression={$_.IPv4Address.IPAddress}},
        @{Name="Gateway"; Expression={$_.IPv4DefaultGateway.NextHop}}
```

Choose the IPv4 address for the active Wi-Fi or Ethernet adapter. On the tested network, the host address was `192.168.1.20`; that address is only an example and may differ on your network. On the second device, open `http://<HOST-PC-IP>:5000`, replacing `<HOST-PC-IP>` with the host's actual private IPv4 address.

Both devices must be on the same network, and network/router client isolation or Windows Firewall rules may block connections. **Do not disable the firewall.** If Windows asks about network access, allow only the appropriate trusted private-network scope after reviewing the prompt. No firewall rules are added automatically by the project.

`0.0.0.0` is the server's listening address, not the URL to enter in a browser. To return to localhost-only mode, stop the server and clear the temporary override in the same PowerShell session:

```powershell
.\stop.ps1
Remove-Item Env:EDUANALYTICS_HOST -ErrorAction SilentlyContinue
```

The override applies only to the current PowerShell process. The next start defaults to localhost unless `EDUANALYTICS_HOST` is set again. When LAN binding is enabled, the managed start script displays the detected LAN URL automatically. A host's private IP can change when reconnecting or moving to another network. This procedure is for trusted LAN testing, not internet-facing or production deployment.

### Developer setup (manual workflow)

These steps are for project development and verification, not the intended final end-user experience. The managed start/stop workflow is recommended for normal local use.

#### Install dependencies

From the project root, create and activate a virtual environment, then install the requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

#### Configure the secret key

EduAnalytics requires a persistent `SECRET_KEY`. The application will not start if the current process cannot access it. The setup script configures the key. If you need to configure it manually for development, run this block only if a user-level key has not already been configured:

```powershell
$key = [Environment]::GetEnvironmentVariable("SECRET_KEY", "User")
if ([string]::IsNullOrWhiteSpace($key)) {
    $key = python -c "import secrets; print(secrets.token_hex(32))"
    [Environment]::SetEnvironmentVariable("SECRET_KEY", $key, "User")
}
$env:SECRET_KEY = $key
Remove-Variable key
```

The script preserves an existing user-level key and generates one only if it is missing. The `start.ps1` script loads the existing key from the current process environment or falls back to the Windows user-level environment variable. It does not print or replace the key.

When using the Flask development server or another manual startup command, ensure that `SECRET_KEY` is available in that PowerShell session. Never print, commit, or share the key, and keep it consistent across restarts.

#### Initialize the database

For the current development version, run:

```powershell
python -m scripts.initialize_database
```

Follow the prompts to enter institution details and initial Administrator account information. Run this only when you intend to initialize the local database. Do not delete or reset an existing database as a troubleshooting step.

#### Start the application for local development

Use the managed lifecycle scripts for normal local use:

```powershell
.\start.ps1
```

Open `http://127.0.0.1:5000` in a browser. To stop the application, run:

```powershell
.\stop.ps1
```

For development-only debugging, the Flask development server can be used instead:

```powershell
python -m flask --app app:create_app run --debug
```

Open `http://127.0.0.1:5000` in a browser. The Flask debug server is for local development only; do not expose it for shared/LAN access. Do not run the Flask development server and the managed Waitress instance on the same port at the same time.

#### Shared/LAN testing (developer-only procedure)

> This is an optional manual procedure for LAN experimentation. The recommended managed workflow supports LAN binding through `EDUANALYTICS_HOST` and displays the detected LAN URL at startup. See the trusted LAN access instructions above.

For trusted local-network testing, use Waitress instead of the Flask development server. Make sure `SECRET_KEY` is available in the PowerShell session.

1. Run `ipconfig` and find the IPv4 address for the active Wi-Fi or Ethernet adapter.
2. Start Waitress, replacing `<HOST-PC-IP>` with the host computer's private IPv4 address:

   ```powershell
   python -m waitress --host=<HOST-PC-IP> --port=8000 --call app:create_app
   ```

3. On the host computer, open `http://127.0.0.1:8000`. On another authorized device on the same network, open `http://<HOST-PC-IP>:8000`.
4. Press `Ctrl+C` in the terminal running Waitress to stop it.

Do not disable the firewall to make this work. Review firewall and network policies for the intended access scope. The host IP may change after reconnecting. This is for trusted LAN testing, not production deployment.

#### Manual database backup and recovery

EduAnalytics supports manual database backups and an interactive recovery procedure. Backups are stored outside the repository by default, in `..\EduAnalytics_Backups`. The live SQLite database is normally `instance\eduanalytics.db`.

**Create a backup**

Run this command from the project root in PowerShell:

```powershell
python .\scripts\backup_database.py
```

The script creates a timestamped `.db` backup, labels it with the institution name, and verifies database integrity. Review the success message. The backup folder's effective access restrictions have not yet been fully verified; do not use real institutional data until access has been reviewed and verified.

**Recover from a backup**

1. Stop EduAnalytics using `.\stop.ps1`.
2. Close any other process that might be using the database.
3. Run:

   ```powershell
   python .\scripts\restore_database.py
   ```

4. Select the listed backup by number. Check the institution, date, and filename.
5. Type `RESTORE` only if you intend to replace the current live database. Enter `Q` at the selection prompt to cancel.

The recovery script validates the selected backup, creates a safety backup of the current database, prepares a replacement, and checks its integrity. It retains the previous database as a rollback file after a successful replacement. Restart the application with `.\start.ps1` after successful recovery.

**Important:** Recovery replaces the live database with the selected snapshot. Changes made after that snapshot may be lost. Do not delete safety backups or rollback files until the recovered application and its data have been checked. If recovery reports an error, read the full message and investigate before retrying.

The restore test suite passed **10 tests**, covering successful recovery, safety-copy retention, rollback after a simulated post-restore verification failure, and handling of a simulated rollback-replacement failure. A live restore was also performed on 2026-10-27; the recovered database passed integrity checks, the application returned HTTP 200 after recovery, and both the safety backup and retained rollback file passed integrity checks. The backup folder's ACL entries were inspected with `icacls`; no permission changes were made, and the output alone does not establish all effective access paths. Automated daily, weekly, and monthly scheduling is intentionally deferred.

#### Run automated tests

```powershell
python -m pytest -q
```

Latest verified result (2026-10-28): **66 passed in 10.74 seconds**. Restore-specific result: **10 passed in 1.12 seconds**. A separate clean-copy test suite also passed 66 tests in 23.59 seconds on 2026-10-28.

### Security and data protection

- Never commit secret keys, passwords, local databases, or sensitive backups.
- Keep backups outside the repository and restrict access to authorized users.
- Setup must not replace an existing secret key or delete/reset an existing database during ordinary reruns.
- Do not expose Flask debug mode on a LAN.
- Initial setup must be protected against unauthorized reuse after completion.
- Do not use real institutional data in the backup location until its storage and effective access restrictions have been reviewed and verified.

## Project Status

**Current milestone:** Authentication, authorization, educator management, setup, first-run Administrator setup, lifecycle scripts, LAN access guidance, and manual database backup and recovery are implemented. Localhost lifecycle checks and same-network LAN access have been verified. The full automated suite passed 66 tests, all 10 restore-specific tests passed, and the isolated clean-copy setup walkthrough passed under the current Windows user. A live-database restore, post-restore application startup (HTTP 200), and safety/rollback integrity checks also passed.

**Closure decision and limitations:** Sprint 4 implementation and verification are complete for the agreed project scope. Existing backup-folder permissions are accepted for this personal development PC because the listed local accounts are trusted, but effective access for every account and access path has not been exhaustively verified. Separate-user/machine setup, access on another network, and production deployment remain unverified. Automated backup scheduling is intentionally deferred. Do not use real institutional data until backup storage and access controls have been appropriately reviewed. See [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) for the detailed acceptance checklist and evidence.

**Next development milestone:** CSV upload and preview, academic-record validation and import, followed by performance summaries, visualizations, filtering, and data export.

## Team

BCD586 mini project — team of three students.

Team member names and individual contributions can be added here as development progresses.
