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

## Planned Features

- **Authentication:** Admin and teacher login with secure password hashing.
- **Teacher Management:** Admin-controlled teacher accounts.
- **CSV Data Import:** Upload, preview, validate, and import student data.
- **Analytics Dashboard:** Summary statistics, charts, filters, and group comparisons.
- **Data Export:** Export filtered records as CSV.
- **Import History:** Track dataset imports.

> EduAnalytics is under active development. The features listed above are planned capabilities and are not all implemented yet.

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
- Initial database setup script for creating the institution and administrator account.
- Authentication and login with password-hash verification.
- Session handling, logout, and rejection of inactive accounts.
- Role-based protection for administrator routes.
- Administrator-controlled educator account creation, activation, and deactivation.
- CSRF protection for forms and state-changing requests.
- Shared home-page template and extracted CSS for the home and educator-management pages.
- Automated regression tests for authentication, authorization, educator management, and database behavior.

The latest recorded full automated test suite passed **39 tests**. See the Sprint 3 documentation for verification evidence and outstanding tasks.

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
- [Sprint 4: Setup and Deployment](docs/Sprint_4_Setup_Deployment.md)

## Setup and Deployment

> **Sprint 4 is in progress.** The goal is to provide a simple Windows setup script, a guided first-run setup page, easy start/stop controls, LAN access guidance, and scheduled backups. These features are being implemented and verified phase by phase. Until the automated setup is complete, EduAnalytics still requires the temporary developer setup described below.

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

1. Run one setup script to check prerequisites, install dependencies, configure the secret key, and initialize the database safely.
2. Open the application in a browser and follow the first-run steps to create the institution and initial Administrator account.
3. Start or stop the application using simple Windows scripts or shortcuts.
4. Open the displayed local address on the host computer or use the LAN address from an authorized device on the same network.
5. Configure daily, weekly, or monthly backups and use the documented restore process if needed.

**Implementation status:** This is the target workflow, not yet a fully available installer. Follow the temporary developer instructions below only when setting up the current development version. As Sprint 4 phases are completed, this section will be updated with the verified user-facing steps.

### Temporary developer setup (until automated setup is ready)

These steps are for project development and verification, not the intended final end-user experience.

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

This preserves an existing user-level key and creates one only if it is missing. A newly opened terminal may load the persistent variable automatically; an already-open terminal may need the value loaded into its session. Never print, commit, or share the key. Keep the same key across restarts.

#### Initialize the database

For the current development version, run:

```powershell
python -m scripts.initialize_database
```

Follow the prompts to enter institution details and initial Administrator account information. Run this only when you intend to initialize the local database. Do not delete or reset an existing database as a troubleshooting step.

#### Start the application for local development

```powershell
python -m flask --app app:create_app run --debug
```

Open `http://127.0.0.1:5000` in a browser. The Flask debug server is for local development only; do not expose it for shared/LAN access.

#### Shared/LAN testing

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

The latest recorded full test suite passed 39 tests. Run the command above to check the current working copy.

### Security and data protection

- Never commit secret keys, passwords, local databases, or sensitive backups.
- Keep backups outside the repository and restrict access to authorized users.
- Setup must not replace an existing secret key or delete/reset an existing database during ordinary reruns.
- Do not expose Flask debug mode on a LAN.
- Initial setup must be protected against unauthorized reuse after completion.
- Do not use real institutional data until storage location and access permissions have been reviewed.

## Project Status

**Current milestone:** Authentication, authorization, educator management, shared page styling, and regression testing have been implemented. The latest recorded full test suite passed 39 tests.

**Remaining Sprint 3 closure work:** Verify network portability on another trusted network and verify access restrictions on the external database backup before using real institutional data. Logout controls for future authenticated pages remain deferred until those pages are implemented.

**Next development milestone:** CSV upload and preview, academic-record validation and import, followed by performance summaries, visualizations, filtering, and data export.

## Team

BCD586 mini project — team of three students.

Team member names and individual contributions can be added here as development progresses.
