# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project that will help teachers and
administrators explore student academic performance through structured
data, analytics, and interactive dashboards.

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

### Planned

-   Academic performance summaries and interactive dashboards.
-   Charts, filters, and group comparisons.
-   Export of filtered records as CSV.
-   Import history.

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

### 6. Run automated tests

From the project root, run:

``` powershell
python -m pytest -v
```

The latest recorded full test run passed **66 tests** on 2026-10-28. The
restore-specific test suite passed **10 tests**. These are recorded
verification results, not a guarantee that every deployment environment
has been tested.

### 7. Access from another device on the same network

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
and analyzed independently.

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
rather than exact hours.

## Next Implementation

Sprint 5 completed the core student-data workflow. The next development
milestone is analytics:

1.  **Academic performance summaries** --- calculate useful summaries
    from imported records.
2.  **Dashboard and visualizations** --- add charts, filters, and
    student-group comparisons.
3.  **CSV export and import history** --- allow filtered results to be
    exported and keep a record of dataset imports.

These features remain planned and are not yet implemented as completed
functionality.

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

## Current Status

Authentication, authorization, educator management, setup, first-run
Administrator setup, lifecycle scripts, manual database backup and
recovery, and the Sprint 5 CSV workflow are implemented. Sprint 5 includes
automatic validation, full preview, row exclusion, transactional import,
duplicate-submission protection, and import-result feedback. Analytics,
filters, charts, export, and import history remain planned for a later
sprint. Separate-user/machine setup, cross-network access, and production
deployment remain unverified. Automated backup scheduling is not
implemented.

**Security note:** Keep the backup folder restricted to authorized
users. Its effective access permissions have not been exhaustively
verified, so do not use real institutional data until storage and access
controls have been reviewed.

## Team

**Project Title:** Student Academic Performance Analytics

**Team Members:** - Sadeeya Fathima - Noor Mifra Nadeem - Shariya Amber

**Course:** BCD586 --- Mini Project
