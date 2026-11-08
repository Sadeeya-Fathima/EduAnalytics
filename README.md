# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project that helps teachers and administrators
explore student academic performance through structured datasets, analytics,
and interactive dashboards.

## Project Objectives

-   Analyze student academic performance using structured datasets.
-   Visualize academic results and compare student groups.
-   Filter and explore data using academic attributes.
-   Import student records from CSV files.
-   Export filtered data for further analysis.

## Features

### Implemented

-   Administrator and educator authentication with password-hash
    verification.
-   Role-based access control and educator account management.
-   Windows setup script and browser-based first-run Administrator setup.
-   Managed application startup and shutdown using Waitress.
-   CSRF protection and persistent application secret-key handling.
-   Manual SQLite database backup and interactive recovery.
-   LAN access by default for authorized devices on the same local network.

-   Guided CSV upload with dataset metadata and downloadable templates.
-   Automatic CSV preview and validation with row-level errors and remarks.
-   Dynamic teacher-defined assessment labels mapped to stable database fields.
-   Per-row `Do Not Upload` exclusion and select-all controls.
-   Transactional SQLite imports with rollback on failure.
-   Server-side preview storage and one-time confirmation-token protection.
-   File-type, encoding, delimiter, header, field-size, row-count, and 5 MiB
    upload safeguards.
-   Import success feedback with the imported dataset and record count.
-   Dataset Management with institution-scoped listing, dataset details,
    metadata, imported-record views, active analysis-dataset selection, and
    stored import information.
-   Responsive dashboard with workspace KPIs and academic dataset cohort cards.
-   Overview-first Academic Analytics Dashboard with verified summaries,
    statistics, findings, and dataset-quality information.
-   Plotly charts for grade distribution, assessment comparison, study-time,
    attendance, and paired assessment relationships.
-   Dataset-aware interactive filters with combined filtering, reset behavior,
    empty-result handling, and matching-record counts.
-   Secure filtered CSV export with server-side filter reuse,
    institution-scoped authorization, approved column ordering, missing-value
    handling, CSV quoting, and spreadsheet formula-injection protection.
-   Modern setup, administration, backup, and error-page interfaces.

### Planned

-   Advanced reporting formats, scheduled reports, and automated email delivery.

## Technology Stack

-   **Backend:** Python, Flask
-   **Data analysis:** Pandas, NumPy
-   **Database:** SQLite, Flask-SQLAlchemy
-   **Authentication:** Flask-Login, Werkzeug
-   **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
-   **Charts:** Plotly.js
-   **Testing:** pytest
-   **Version control:** Git and GitHub

## Setup and Deployment

### Prerequisites

-   Windows 10 or Windows 11 (the primary target; macOS and Linux have
    not been verified)
-   Python 3.12
-   Git
-   PowerShell

### 1. Download the project

Open PowerShell in the folder where you want to keep the project:

``` powershell
git clone https://github.com/Sadeeya-Fathima/EduAnalytics.git
cd EduAnalytics
```

### 2. Set up the application

From the project root, run:

``` powershell
.\setup.ps1
```

Follow any prompts shown by the script. The setup script prepares the
local development environment and configures the application secret key.
Do not share or commit secret keys, passwords, or local database files.

### 3. Start and access the application

1.  Start EduAnalytics from the project root:

    ``` powershell
    .\start.ps1
    ```

2.  Follow the URL displayed by the script:

    -   **First-time setup:** Open `http://127.0.0.1:5000/setup/` to
        register your institution and create the initial Administrator
        account.
    -   **Setup already completed:** Open
        `http://127.0.0.1:5000/auth/login` to sign in with your existing
        account.

3.  After creating the initial Administrator account, sign in using the
    credentials you registered.

The startup script checks whether first-run setup is complete and
displays the appropriate link. If EduAnalytics is already running, it
displays the appropriate link without starting another instance.

Use the managed scripts for normal application use:

``` powershell
.\start.ps1
.\stop.ps1
```

Run `.\stop.ps1` to stop the application before restarting it. If the
application is already running, `.\start.ps1` will report this and
display the appropriate setup or login link.

By default, EduAnalytics listens on `0.0.0.0:5000`, allowing access from
the host computer and authorized devices on the same local network. Use
the local URL for the host PC and the LAN URL printed by `start.ps1` for
other devices.

### 4. Create a database backup

Backups are stored outside the repository by default, in
`..\EduAnalytics_Backups`. The live SQLite database is normally located
at `instance\eduanalytics.db`.

1.  Make sure the project is in a usable state and open PowerShell in
    the project root.

2.  Run:

    ``` powershell
    python .\scripts\backup_database.py
    ```

3.  Check the success message and note the backup filename. The script
    creates a timestamped SQLite backup labelled with the institution
    name and verifies its integrity.

4.  Keep the backup folder accessible only to authorized users. Do not
    use real institutional data until the folder's effective access
    restrictions have been reviewed and verified.

Do not store backups in the Git repository or commit them.

### 5. Restore a database backup

**Restoring replaces the live database with the selected backup. Any
changes made after that backup was created may be lost.**

1.  Stop the application:

    ``` powershell
    .\stop.ps1
    ```

2.  Close any other process that might be using the database.

3.  Start the interactive recovery script:

    ``` powershell
    python .\scripts\restore_database.py
    ```

4.  Select the desired backup by its listed number. Check the
    institution, date, and filename carefully.

5.  Type `RESTORE` only when you intend to replace the current live
    database. Enter `Q` at the selection prompt to cancel.

6.  Wait for the script to finish. It validates the backup, creates a
    safety backup of the current database, and checks the replacement
    database. After a successful replacement, the previous database is
    retained as a rollback file.

7.  Start the application again:

    ``` powershell
    .\start.ps1
    ```

8.  Open `http://127.0.0.1:5000`, sign in, and check that the expected
    data is present.

9.  Do not delete the safety backup or rollback file until you have
    verified the recovered application and data. If recovery reports an
    error, read the full message and investigate before trying again.

### 6. Developer access and maintenance

Developer Administration is an optional local-development workstream. It is
disabled by default and must never be enabled on an institution deployment.
No shared or default Developer credentials are provided.

On the local development machine, enable the tools for the current
PowerShell session:

``` powershell
$env:SECRET_KEY = [Environment]::GetEnvironmentVariable("SECRET_KEY", "User")
$env:EDUANALYTICS_ENV = "development"
$env:EDUANALYTICS_DEV_TOOLS_ENABLED = "true"
$env:EDUANALYTICS_DEV_TOOLS_LOCAL_ONLY = "true"
```

Complete normal first-run setup first, then create a per-installation
Developer account:

``` powershell
python scripts/create_dev_account.py
```

The script prompts for the username, email, first name, last name, and a
hidden password confirmation. It refuses non-development or disabled
installations and never prints credentials or password hashes.

Start the application and sign in locally:

``` powershell
.\start.ps1
```

Open `http://127.0.0.1:5000/` and use the **Developer Tools** menu. The local
Developer area provides:

-   A safe operational dashboard.
-   Read-only inspection of approved database resources with pagination.
-   Controlled updates for approved User, Dataset, and Student Record fields.
-   Verified manual backup creation and backup metadata.
-   Diagnostics, audit-log viewing, and maintenance guidance.

Developer tools are loopback-only by default. The LAN application URL must not
be used for Developer routes. Database restore remains an offline operation:

``` powershell
.\stop.ps1
python scripts/restore_database.py
```

For a full development reset, stop the application and use:

``` powershell
python scripts/reset_database.py
```

The reset creates and verifies a safety backup and requires the exact phrase
`RESET DATABASE`. Use it only for an explicitly enabled development database.
It removes application accounts and academic data while preserving external
backup files and application configuration. Do not run it against an
institution database.

Detailed design, security boundaries, phase evidence, and acceptance criteria
are documented in [Developer Administration](docs/Developer_Administration.md).

### 7. Run automated tests

From the project root, use the project virtual environment:

``` powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The Sprint 5 regression evidence records **86 tests** passed across the
grouped application suites, including **22 upload-workflow tests** and
**10 restore-specific tests**. This is historical Sprint 5 evidence.

Historical full-regression results:

| Sprint | Result | Date |
|---|---:|---|
| Sprint 5 | 86 passed | Historical record |
| Sprint 6 | 136 passed | Historical record |
| Sprint 7 | 157 passed | 7 November 2026 |
| Sprint 8 | 170 passed | 7 November 2026 |
| Sprint 9 | 171 passed | 8 November 2026 |

The Sprint 9 result was run with
`.\.venv\Scripts\python.exe -m pytest -q`.

Both results are recorded verification evidence for the current development
environment; rerun the suite after future changes.

### 8. Access from another device on the same network

LAN access is enabled by default for testing on a trusted local network.
Start EduAnalytics normally:

``` powershell
.\start.ps1
```

The startup script displays the local URL and any detected LAN URL(s).
On another authorized device connected to the same Wi-Fi or wired
network, open the displayed LAN URL, for example
`http://<HOST-PC-IP>:5000`, replacing `<HOST-PC-IP>` with the host
computer's private IPv4 address.

If you need to find the host computer's private IPv4 address manually,
run:

``` powershell
Get-NetIPConfiguration |
    Where-Object {
        $_.IPv4DefaultGateway -ne $null -and
        $_.NetAdapter.Status -eq "Up"
    } |
    Select-Object InterfaceAlias,
        @{Name="IPv4Address"; Expression={$_.IPv4Address.IPAddress}},
        @{Name="Gateway"; Expression={$_.IPv4DefaultGateway.NextHop}}
```

Both devices must be on the same network. Router client isolation or
Windows Firewall rules may block connections. Do not disable the
firewall; review any access prompt and allow only the appropriate
trusted private-network scope. The project does not add firewall rules
automatically.

`0.0.0.0` is the listening address, not the address to enter in a
browser. LAN access across other networks and production deployment have
not been verified. Do not expose the app directly to the internet or run
Flask debug mode on a network.

## Dataset

EduAnalytics supports both converted UCI-based datasets and institutional
CSV datasets through the same configured template. Each dataset is imported
and analyzed independently. Uploaded files must use this canonical header:

```csv
student_name,g1,g2,g3,studytime,absences
```

Canonical field meanings:

- `student_name` — student display name or pseudonymous label.
- `g1` — first assessment grade.
- `g2` — second assessment grade.
- `g3` — final or primary grade; required for every record.
- `studytime` — optional study-time value; UCI category codes are not exact
  hours.
- `absences` — optional non-negative absence value when the source unit is
  known.

For UCI-derived files, the source columns are `G1`, `G2`, and `G3`. Before
upload, convert them to the EduAnalytics canonical fields `g1`, `g2`, and
`g3`; the canonical header uses lowercase names and the exact order shown
above.

Selected attributes include:

-   `G1` --- First-period grade
-   `G2` --- Second-period grade
-   `G3` --- Final grade
-   `studytime` --- Study-time value supplied by the source; UCI category codes
    are not interpreted as hours.
-   `absences` --- Number of absences for the subject when the source unit is
    known.

In the selected UCI dataset, grades are recorded on a scale from 0 to
20. The `studytime` attribute represents categories of weekly study time
rather than actual hours. UCI source codes such as `1`, `2`, `3`, and `4` must
not be reported or analyzed as exact hours per week; they remain categorical
values.

## Delivered Work

Sprint 2 established the Flask application foundation, SQLite database,
models, templates, navigation, and configuration. Sprint 3 delivered
authentication, role-based authorization, and educator account management.
Sprint 4 delivered managed setup/start/stop workflows, host-PC deployment,
trusted-LAN access, manual backup, and recovery procedures. Sprint 5
completed the core student-data upload and validation workflow. Sprint 6
completed Dataset Management. Sprint 7 delivered the Academic Analytics
Dashboard with summaries, charts, comparisons, and interactive filters.
Sprint 8 delivered secure filtered CSV export with server-side filtering,
dataset authorization, missing-value preservation, and formula-injection
protection.
Sprint 9 completed end-to-end, LAN/multi-user, security, regression, usability,
defect-retest, and release-readiness verification.

Analytics must preserve the distinction that UCI `studytime` values are
categorical weekly-study ranges, not measured hours.

## Project Documentation

-   [MVP Scope and Requirements
    Specification](docs/MVP_Scope_and_Requirements.md) --- approved
    features, technology stack, dataset, development plan, team
    responsibilities, and acceptance criteria.
-   [Sprint 3 --- Authentication and Educator Account
    Management](docs/Sprint_3_Authentication.md) --- authentication,
    authorization, educator management, and verification.
-   [Sprint 4 --- Setup and
    Deployment](docs/Sprint_4_Setup_Deployment.md) --- detailed setup,
    lifecycle scripts, LAN access, backup and recovery, verification
-   [Sprint 5 --- CSV Upload and Data
    Validation](docs/Sprint_5_CSV_Upload_Data_Validation.md) --- completed
    upload, validation, preview, exclusion, and transactional import workflow
    evidence, and known limitations.
-   [Sprint 6 --- Dataset
    Management](docs/Sprint_6_Dataset_Management.md) --- completed dataset
    listing, dashboard cohorts, metadata, record views, selection, import
    information, testing evidence, and handoff to Sprint 7.
-   [Sprint 7 --- Academic
    Analytics](docs/Sprint_7_Academic_Analytics.md) --- dashboard analytics,
    charts, interactive filters, and verification evidence.
-   [Sprint 8 --- Filtered Analytics Export and Integration
    Testing](docs/Sprint_8_Filtered_Analytics_Export_Integration_Testing.md) ---
    secure CSV export, integration, security, regression testing, and final
    review evidence.
-   [Sprint 9 --- Testing and Quality
    Assurance](docs/Sprint_9_Testing_and_Quality_Assurance.md) --- end-to-end,
    LAN and multi-user verification, security checks, regression testing,
    defect retesting, documentation review, and release-readiness decision.
-   [Developer Administration](docs/Developer_Administration.md) --- separate
    local Developer access, maintenance tooling, security phases, tests, and
    acceptance evidence.

## Current Status

Authentication, authorization, educator management, setup, first-run
Administrator setup, lifecycle scripts, manual database backup and
recovery, the Sprint 5 CSV workflow, and Sprint 6 Dataset Management are
implemented. Sprint 6 includes institution-scoped dataset listing, dashboard
cohorts and KPIs, metadata and record views, server-validated active dataset
selection, and stored import information. Sprint 7 adds the overview-first
Academic Analytics Dashboard, charts, assessment comparisons, interactive
filters, and verification evidence. Sprint 8 adds the filtered CSV export
workflow and security/regression evidence. Sprint 9 verified same-LAN access
from separate Windows and Android client sessions, role enforcement, and host
shutdown behavior. Separate Windows-user setup, cross-network access, and
production deployment remain unverified. Automated backup scheduling is not
implemented.

**Security note:** Keep the backup folder restricted to authorized
users. Its effective access permissions have not been exhaustively
verified, so do not use real institutional data until storage and access
controls have been reviewed.

## Team

**Project Title:** Student Academic Performance Analytics

**Team Members:**

- Sadeeya Fathima
- Noor Mifra Nadeem
- Shariya Amber

**Course:** BCD586 --- Mini Project
