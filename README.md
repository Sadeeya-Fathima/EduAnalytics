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

## Getting Started

### Prerequisites

- Python
- Git
- Visual Studio Code (recommended)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Sadeeya-Fathima/EduAnalytics.git
   cd EduAnalytics
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

### Initialize the Database

Run the initial database setup script:

```bash
python -m scripts.initialize_database
```

Follow the prompts to enter the institution details and initial administrator account information. The administrator password is stored as a hash.

**Important:** Run this setup only when you intend to initialize the local database. Use a strong password and do not commit database files or credentials to Git.


### Security Configuration

EduAnalytics requires a secret key to protect session data and other security-related functionality. The application reads this value from the `SECRET_KEY` environment variable and will not start if it is missing.

#### Configure the Secret Key on Windows

In PowerShell, run the following command **once** to generate a random secret key and store it in your Windows user environment variables:

```powershell
$key = python -c "import secrets; print(secrets.token_hex(32))"
[Environment]::SetEnvironmentVariable("SECRET_KEY", $key, "User")
$env:SECRET_KEY = $key
Remove-Variable key
```

This command does not print the key. Keep it private and do not hardcode it in application code or commit it to Git.

For future PowerShell sessions, Windows supplies the saved user environment variable to newly opened terminals. If the variable is missing, configure it again securely before starting the application.

#### Verify the Configuration

Check whether the variable is configured without displaying its value:

```powershell
if ([string]::IsNullOrWhiteSpace($env:SECRET_KEY)) {
    "SECRET_KEY is not set in this session."
} else {
    "SECRET_KEY is configured in this session."
}
```

#### Git and Deployment Safety

- `.env` and `.env.*` files are ignored by Git. Never commit secret values.
- Do not share the secret key in source code, screenshots, logs, or messages.
- Keep the same secret key across application restarts. Changing it may invalidate existing sessions.
- Before running EduAnalytics on a shared LAN, disable debug mode and configure the host, firewall, and database backups appropriately.

### Database Backup and Restoration

Database backups help recover the application if the database is accidentally deleted, corrupted, or damaged during development. Keep backups outside the Git repository so they are not accidentally committed or shared publicly.

#### Create a Backup on Windows

Run these commands from the project root with your virtual environment activated.

**1. Create a backup folder outside the repository**

```powershell
New-Item -ItemType Directory -Force "..\EduAnalytics_Backups"
```

**2. Create and verify a consistent SQLite backup**

The application database is normally located at `instance\eduanalytics.db`. Run the following Python script from the project root:

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
            result = backup.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

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

The script uses SQLite's backup API, verifies the resulting database, and reports the backup location. Confirm that the integrity result is `ok`.

#### Restore and Verify a Backup

1. Stop the application before replacing or restoring its database.
2. Keep a separate copy of the current database before making changes.
3. Restore the selected backup to a separate test location first; do not overwrite the working database during a restoration test.
4. Check the restored copy using SQLite:

```powershell
python -c "import sqlite3; c=sqlite3.connect('file:PATH_TO_RESTORED_DB?mode=ro', uri=True); print(c.execute('PRAGMA integrity_check').fetchone()[0]); c.close()"
```

Replace `PATH_TO_RESTORED_DB` with the restored database path, using forward slashes and URL-encoding any special characters if necessary. The expected result is `ok`. For a stronger restoration test, verify that the expected tables and records are present and that the application can initialize against a disposable copy.

#### Backup Safety

- Keep backup files outside the repository and ensure access is restricted to authorized users.
- Never commit database files containing account records, personal information, or institutional data to a public repository.
- Check `.gitignore` to ensure local database files and backup directories are excluded. Git ignore rules do not remove files that are already tracked.
- Store an additional copy in an appropriately protected location if the data is important.
- Before using real institutional data, obtain the required authorization and follow the institution's data-handling requirements.

### Run Locally for Development

Use Flask's development server for local development only. Do not use debug mode for shared/LAN access.

```bash
python -m flask --app app:create_app run --debug
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The application includes authentication, role-based access control, and educator management. Run `python -m pytest -q` to execute the automated test suite. The project may still have features under development; consult the project documentation for current scope and limitations.

### Run for Shared/LAN Testing

To access EduAnalytics from another device on the same trusted local network, use Waitress instead of Flask's development server.

**1. Configure the environment**

Ensure `SECRET_KEY` is configured in the PowerShell session running the application.

**2. Find the host computer's private IPv4 address**

On Windows, run:

```powershell
ipconfig
```

Under the active Wi-Fi or Ethernet adapter, find the `IPv4 Address` (for example, `192.168.1.5`). Use your own computer's address, not the example.

**3. Start Waitress**

Replace `<HOST-PC-IP>` with the private IPv4 address found in Step 2:

```powershell
python -m waitress --host=<HOST-PC-IP> --port=8000 --call app:create_app
```

For example, if your computer's address is `192.168.1.5`:

```powershell
python -m waitress --host=192.168.1.5 --port=8000 --call app:create_app
```

**4. Open the application**

- On the host computer, open `http://127.0.0.1:8000`.
- On another device connected to the same LAN, open `http://<HOST-PC-IP>:8000`, replacing the placeholder with the host's actual private IPv4 address.

**5. Stop the server**

Press `Ctrl+C` in the terminal running Waitress.

**Security notes:**
- Do not use Flask debug mode for shared access.
- Binding to a specific IP limits the listener to that interface, but does not replace firewall controls.
- The host's IP address may change after reconnecting to the network. Check it again if the connection stops working.
- Windows Firewall must be configured appropriately for the intended network and access scope. Do not assume access is restricted to trusted devices.
- If access is blocked, ask the network administrator to review the firewall and network policies rather than disabling the firewall.
- This setup is intended for trusted LAN testing, not production deployment.

### Run Tests

```bash
python -m pytest -q
```

The latest recorded full automated test suite passed 39 tests. Run the
command above to verify the current result in your local environment.

## Project Status

**Current milestone:** Authentication, authorization, educator management, shared page styling, and regression testing have been implemented. The latest recorded full test suite passed 39 tests.

**Remaining Sprint 3 closure work:** Verify network portability on another trusted network and verify access restrictions on the external database backup before using real institutional data. Logout controls for future authenticated pages remain deferred until those pages are implemented.

**Next development milestone:** CSV upload and preview, academic-record validation and import, followed by performance summaries, visualizations, filtering, and data export.

## Team

BCD586 mini project — team of three students.

Team member names and individual contributions can be added here as development progresses.
