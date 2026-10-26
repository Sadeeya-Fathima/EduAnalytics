# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project designed to help teachers and administrators explore student academic performance using interactive dashboards and data analytics.

The project is being developed incrementally, with an emphasis on data management, meaningful visualizations, and a maintainable Flask application.

## Project Objectives

- Analyze student academic performance using structured datasets.
- Visualize academic results and compare student groups.
- Filter and explore data using relevant academic attributes.
- Import student records from CSV files.
- Export filtered data for further analysis.

## Features

### Implemented

- **Authentication:** Administrator and educator login with password-hash verification.
- **Educator Management:** Administrator-controlled educator account creation, activation, and deactivation.
- **Access Control:** Role-based protection for administrator routes and rejection of inactive accounts.
- **Setup and Deployment:** Windows setup script (`setup.ps1`), browser-based first-run Administrator setup, and application start/stop scripts (`start.ps1` and `stop.ps1`).
- **Security:** CSRF protection and persistent application secret-key handling.

### Planned

- **CSV Data Import:** Upload, preview, validate, and import student data.
- **Analytics Dashboard:** Summary statistics, charts, filters, and group comparisons.
- **Data Export:** Export filtered records as CSV.
- **Import History:** Track dataset imports.

> EduAnalytics is under active development. Features listed as planned are not yet available as completed functionality.

## Technology Stack

- **Backend:** Python, Flask
- **Data Analysis:** Pandas, NumPy
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Charts:** Plotly.js
- **Testing:** pytest
- **Version Control:** Git and GitHub

## Current Implementation

The following components have been implemented:

- Flask application factory and application configuration.
- SQLAlchemy database models for institutions, users, datasets, student records, and upload errors.
- Database relationships and SQLite foreign-key enforcement.
- Initial database setup and browser-based first-run flow for creating the institution and initial Administrator account.
- Authentication, login, password-hash verification, session handling, and logout.
- Rejection of inactive accounts and role-based protection for administrator routes.
- Administrator-controlled educator account creation, activation, and deactivation.
- CSRF protection for forms and state-changing requests.
- Shared home-page template and extracted CSS for the home and educator-management pages.
- Windows setup script (`setup.ps1`) and application lifecycle scripts (`start.ps1` and `stop.ps1`).
- Waitress-based local startup, duplicate-instance prevention, and managed application shutdown.
- Persistent user-level `SECRET_KEY` loading by the start script without printing or replacing the key.
- Automated regression tests for authentication, authorization, educator management, and database behavior.

The latest recorded full automated test suite passed **52 tests**. See the Sprint 3 documentation for regression-test evidence and outstanding tasks. Run the test suite again to verify the current working copy.

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

- [MVP Scope and Requirements Specification](docs/MVP_Scope_and_Requirements.md) — Defines the approved features, technology stack, dataset, development plan, team responsibilities, and acceptance criteria.
- [Sprint 3 — Authentication and Educator Account Management](docs/Sprint_3_Authentication.md) — Documents authentication and authorization implementation, educator management, regression tests, manual verification, database backup restoration, and remaining closure actions.
- [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) — Tracks setup automation, first-run configuration, application lifecycle scripts, LAN access, backup/recovery, and verification status.

## Setup and Deployment

> **Sprint 4 is in progress.** The Windows setup script (`setup.ps1`), browser-based first-run Administrator setup, and Phase 4 application lifecycle scripts (`start.ps1` and `stop.ps1`) are implemented. Phase 4 verification confirmed successful Waitress startup, HTTP 200 at `http://127.0.0.1:5000`, duplicate-start prevention, successful shutdown, and unchanged database row counts across a start/stop cycle. The persistent user-level `SECRET_KEY` is configured and loaded by the start script without printing or replacing it. LAN access from another device and scheduled backup/recovery workflows remain to be implemented and verified. See [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) for phase details and outstanding work.

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

1. Run the setup script (`setup.ps1`) to check prerequisites, install dependencies, configure the secret key, and initialize the database safely.
2. Open the application in a browser and follow the first-run steps to create the institution and initial Administrator account.
3. Start or stop the application using the provided Windows scripts (`start.ps1` and `stop.ps1`).
4. Access the application at `http://127.0.0.1:5000` on the host computer. Access from other devices on the same network will be supported after LAN configuration is implemented and verified in Phase 5.
5. Configure daily, weekly, or monthly backups and use the documented restore process if needed. Backup scheduling and recovery workflows remain planned for a later phase.

**Implementation status:** The setup script, browser-based first-run Administrator setup, and Phase 4 application lifecycle scripts (`start.ps1` and `stop.ps1`) are implemented. Runtime verification confirmed that the application starts successfully using Waitress, returns HTTP 200 at `http://127.0.0.1:5000`, prevents duplicate managed instances, and shuts down successfully. Database row counts remained unchanged across a start/stop cycle. The persistent user-level `SECRET_KEY` is configured and loaded by the start script without printing or replacing it.

**Current limitations:** The application is currently configured for access on the host computer only. LAN access from another device, scheduled backups, and automated recovery remain to be implemented and verified. Refer to [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) for the current implementation status and remaining work.

### Temporary developer setup (until automated setup is ready)

These steps are for project development and verification, not the intended final end-user experience. The managed start/stop workflow is the recommended way to run the verified local application.

#### Install dependencies

From the project root, create and activate a virtual environment, then install the requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

#### Configure the secret key

EduAnalytics requires a persistent `SECRET_KEY`. The application will not start if the current process cannot access it. Run this block once in PowerShell if a user-level key has not already been configured:

```powershell
$key = [Environment]::GetEnvironmentVariable("SECRET_KEY", "User")
if ([string]::IsNullOrWhiteSpace($key)) {
    $key = python -c "import secrets; print(secrets.token_hex(32))"
    [Environment]::SetEnvironmentVariable("SECRET_KEY", $key, "User")
}
$env:SECRET_KEY = $key
Remove-Variable key
```

The script above preserves an existing user-level key and generates one only if it is missing. The `start.ps1` script loads the existing key from the current process environment or falls back to the Windows user-level environment variable. It does not print or replace the key.

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

Open `http://127.0.0.1:5000` in a browser. To stop the application, open another PowerShell session in the project root if needed and run:

```powershell
.\stop.ps1
```

For development-only debugging, the Flask development server can be used instead:

```powershell
python -m flask --app app:create_app run --debug
```

Open `http://127.0.0.1:5000` in a browser. The Flask debug server is for local development only; do not expose it for shared/LAN access. Do not run the Flask development server and the managed Waitress instance on the same port at the same time.

#### Shared/LAN testing (developer-only procedure)

> This manual command is for LAN experimentation and is separate from the verified `start.ps1` workflow. The managed application currently binds to `127.0.0.1:5000`; the Phase 5 LAN workflow has not yet been implemented and verified.

For trusted local-network testing, use Waitress instead of the Flask development server. Make sure `SECRET_KEY` is available in the PowerShell session.

1. Run `ipconfig` and find the IPv4 address for the active Wi-Fi or Ethernet adapter.
2. Start Waitress, replacing `<HOST-PC-IP>` with the host computer's private IPv4 address:

   ```powershell
   python -m waitress --host=<HOST-PC-IP> --port=8000 --call app:create_app
   ```

3. On the host computer, open `http://127.0.0.1:8000`. On another authorized device on the same network, open `http://<HOST-PC-IP>:8000`.
4. Press `Ctrl+C` in the terminal running Waitress to stop it.

Do not disable the firewall to make this work. Review firewall and network policies for the intended access scope. The host IP may change after reconnecting. This is for trusted LAN testing, not production deployment.

#### Manual database backup and restore (developer procedure)

Backups must be stored outside the repository and protected from unauthorized access. The application's SQLite database is normally `instance\eduanalytics.db`.

Create a backup folder outside the repository:

```powershell
New-Item -ItemType Directory -Force "..\EduAnalytics_Backups"
```

Use SQLite's backup API to create a consistent copy and verify its integrity:

```powershell
@'
import sqlite3
from datetime import datetime
from pathlib import Path

source = Path("instance/eduanalytics.db")
backup_dir = Path("..") / "EduAnalytics_Backups"
backup_dir.mkdir(parents=True, exist_ok=True)

if not source.is_file():
    raise SystemExit(f"Database not found: {source}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
destination = backup_dir / f"eduanalytics_{timestamp}.db"

try:
    with sqlite3.connect(source) as original:
        with sqlite3.connect(destination) as backup:
            original.backup(backup)
            result = backup.execute("PRAGMA integrity_check").fetchone()[0]

    if result != "ok":
        destination.unlink(missing_ok=True)
        raise SystemExit(f"Backup integrity check failed: {result}")

    print(f"Backup created: {destination}")
    print(f"Integrity check: {result}")
except Exception:
    destination.unlink(missing_ok=True)
    raise
'@ | python -
```

The expected integrity result is `ok`. To test a restore, restore the backup to a separate test location first; do not overwrite the active database during a restoration test. Check the restored copy with SQLite:

```powershell
python -c "import sqlite3; c=sqlite3.connect('file:PATH_TO_RESTORED_DB?mode=ro', uri=True); print(c.execute('PRAGMA integrity_check').fetchone()[0]); c.close()"
```

Replace `PATH_TO_RESTORED_DB` with the actual restored database path. For a stronger test, verify expected tables and records and check that the application can use a disposable copy. Automated daily, weekly, and monthly backup scheduling is not yet implemented.

#### Run automated tests

```powershell
python -m pytest -q
```

The latest recorded full test suite passed **52 tests**. Run the command above to verify the current working copy.

### Security and data protection

- Never commit secret keys, passwords, local databases, or sensitive backups.
- Keep backups outside the repository and restrict access to authorized users.
- Setup must not replace an existing secret key or delete/reset an existing database during ordinary reruns.
- Do not expose Flask debug mode on a LAN.
- Initial setup must be protected against unauthorized reuse after completion.
- Do not use real institutional data until storage location and access permissions have been reviewed.

## Project Status

**Current milestone:** Authentication, authorization, educator management, shared page styling, and Phase 4 application lifecycle scripts have been implemented. The setup script and browser-based first-run Administrator setup are also available. Phase 4 runtime verification confirmed successful Waitress startup, HTTP 200 at `http://127.0.0.1:5000`, duplicate-start prevention, successful shutdown, and unchanged database row counts across a start/stop cycle. LAN access from other devices and scheduled backup/recovery workflows remain outstanding. See [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) for phase-by-phase status.

**Remaining Sprint 3 closure work:** Verify network portability on another trusted network and verify access restrictions on the external database backup before using real institutional data. Logout controls for future authenticated pages remain deferred until those pages are implemented.

**Next development milestone:** CSV upload and preview, academic-record validation and import, followed by performance summaries, visualizations, filtering, and data export.

## Team

BCD586 mini project — team of three students.

Team member names and individual contributions can be added here as development progresses.
