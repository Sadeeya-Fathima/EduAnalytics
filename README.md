# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project that will help teachers and administrators explore student academic performance through structured data, analytics, and interactive dashboards.

## Project Objectives

- Analyze student academic performance using structured datasets.
- Visualize academic results and compare student groups.
- Filter and explore data using academic attributes.
- Import student records from CSV files.
- Export filtered data for further analysis.

## Features

### Implemented

- Administrator and educator authentication with password-hash verification.
- Role-based access control and educator account management.
- Windows setup script and browser-based first-run Administrator setup.
- Managed application startup and shutdown using Waitress.
- CSRF protection and persistent application secret-key handling.
- Manual SQLite database backup and interactive recovery.
- Optional access from authorized devices on the same local network.

### Planned

- CSV upload, preview, validation, and import.
- Academic performance summaries and interactive dashboards.
- Charts, filters, and group comparisons.
- Export of filtered records as CSV.
- Import history.

## Technology Stack

- **Backend:** Python, Flask
- **Data analysis:** Pandas, NumPy
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Charts:** Plotly.js
- **Testing:** pytest
- **Version control:** Git and GitHub

## Setup and Deployment

### Prerequisites

- Windows 10 or Windows 11 (the primary target; macOS and Linux have not been verified)
- Python 3.12
- Git
- PowerShell

### 1. Download the project

Open PowerShell in the folder where you want to keep the project:

```powershell
git clone https://github.com/Sadeeya-Fathima/EduAnalytics.git
cd EduAnalytics
```

### 2. Set up the application

From the project root, run:

```powershell
.\setup.ps1
```

Follow any prompts shown by the script. The setup script prepares the local development environment and configures the application secret key. Do not share or commit secret keys, passwords, or local database files.

### 3. Complete first-run setup

1. Start the application:

   ```powershell
   .\start.ps1
   ```

2. Open `http://127.0.0.1:5000` in your browser.
3. Follow the setup page to create your institution and the initial Administrator account.
4. After setup, sign in with the Administrator account you created.

Use the managed scripts for normal application use:

```powershell
.\start.ps1
.\stop.ps1
```

Run `.\stop.ps1` in a separate PowerShell window when needed. The default configuration listens on localhost, so the application is accessible only from the host computer.

### 4. Create a database backup

Backups are stored outside the repository by default, in `..\EduAnalytics_Backups`. The live SQLite database is normally located at `instance\eduanalytics.db`.

1. Make sure the project is in a usable state and open PowerShell in the project root.
2. Run:

   ```powershell
   python .\scripts\backup_database.py
   ```

3. Check the success message and note the backup filename. The script creates a timestamped SQLite backup labelled with the institution name and verifies its integrity.
4. Keep the backup folder accessible only to authorized users. Do not use real institutional data until the folder's effective access restrictions have been reviewed and verified.

Do not store backups in the Git repository or commit them.

### 5. Restore a database backup

**Restoring replaces the live database with the selected backup. Any changes made after that backup was created may be lost.**

1. Stop the application:

   ```powershell
   .\stop.ps1
   ```

2. Close any other process that might be using the database.
3. Start the interactive recovery script:

   ```powershell
   python .\scripts\restore_database.py
   ```

4. Select the desired backup by its listed number. Check the institution, date, and filename carefully.
5. Type `RESTORE` only when you intend to replace the current live database. Enter `Q` at the selection prompt to cancel.
6. Wait for the script to finish. It validates the backup, creates a safety backup of the current database, and checks the replacement database. After a successful replacement, the previous database is retained as a rollback file.
7. Start the application again:

   ```powershell
   .\start.ps1
   ```

8. Open `http://127.0.0.1:5000`, sign in, and check that the expected data is present.
9. Do not delete the safety backup or rollback file until you have verified the recovered application and data. If recovery reports an error, read the full message and investigate before trying again.

### 6. Run automated tests

From the project root, run:

```powershell
python -m pytest -v
```

The latest recorded full test run passed **66 tests** on 2026-10-28. The restore-specific test suite passed **10 tests**. These are recorded verification results, not a guarantee that every deployment environment has been tested.

### Optional: Access from another device on the same network

LAN access is intended only for testing on a trusted local network. By default, the application listens on localhost.

1. On the host computer, open PowerShell in the project root.
2. Set the host to listen on network interfaces and start the application:

   ```powershell
   $env:EDUANALYTICS_HOST = "0.0.0.0"
   .\start.ps1
   ```

3. Find the host computer's private IPv4 address:

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

4. On another authorized device connected to the same Wi-Fi or wired network, open `http://<HOST-PC-IP>:5000`, replacing `<HOST-PC-IP>` with the host computer's private IPv4 address.

Both devices must be on the same network. Router client isolation or Windows Firewall rules may block connections. Do not disable the firewall; review any access prompt and allow only the appropriate trusted private-network scope. The project does not add firewall rules automatically.

To return to localhost-only mode, stop the server and clear the override in the same PowerShell session:

```powershell
.\stop.ps1
Remove-Item Env:EDUANALYTICS_HOST -ErrorAction SilentlyContinue
```

`0.0.0.0` is the listening address, not the address to enter in a browser. LAN access across other networks and production deployment have not been verified. Do not expose the Flask development server or debug mode to a network.

## Dataset

The project plans to use the UCI Student Performance dataset, focusing on either the mathematics or Portuguese language dataset.

Selected attributes include:

- `G1` — First-period grade
- `G2` — Second-period grade
- `G3` — Final grade
- `studytime` — Weekly study-time category
- `absences` — Number of school absences

In the selected UCI dataset, grades are recorded on a scale from 0 to 20. The `studytime` attribute represents categories of weekly study time rather than exact hours.

## Next Implementation

The next development milestone is to implement the core student-data workflow in small, testable steps:

1. **CSV upload and preview** — allow an educator to upload a dataset and inspect its rows before import.
2. **Data validation and import** — validate required columns and values, report invalid rows, and save valid student records.
3. **Academic performance summaries** — calculate useful summaries from imported records.
4. **Dashboard and visualizations** — add charts, filters, and student-group comparisons.
5. **CSV export and import history** — allow filtered results to be exported and keep a record of dataset imports.

These features are planned and are not yet implemented as completed functionality.

## Project Documentation

- [MVP Scope and Requirements Specification](docs/MVP_Scope_and_Requirements.md) — approved features, technology stack, dataset, development plan, team responsibilities, and acceptance criteria.
- [Sprint 3 — Authentication and Educator Account Management](docs/Sprint_3_Authentication.md) — authentication, authorization, educator management, and verification.
- [Sprint 4 — Setup and Deployment](docs/Sprint_4_Setup_Deployment.md) — detailed setup, lifecycle scripts, LAN access, backup and recovery, verification evidence, and known limitations.

## Current Status

Authentication, authorization, educator management, setup, first-run Administrator setup, lifecycle scripts, and manual database backup and recovery are implemented. The full automated test suite has passed 66 tests, and the restore-specific suite has passed 10 tests. Setup and LAN checks were completed on the current Windows development environment; separate-user/machine setup, cross-network access, and production deployment remain unverified. Automated backup scheduling is not implemented.

**Security note:** Keep the backup folder restricted to authorized users. Its effective access permissions have not been exhaustively verified, so do not use real institutional data until storage and access controls have been reviewed.

## Team

**Project Title:** Student Academic Performance Analytics

**Team Members:**
- Sadeeya Fathima
- Noor Mifra Nadeem
- Shariya Amber

**Course:** BCD586 — Mini Project
