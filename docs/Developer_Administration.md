# EduAnalytics --- Developer Administration

**Document type:** Engineering and maintenance specification\
**Version:** 1.0 --- Proposed implementation baseline\
**Status:** Design baseline finalized for post-MVP implementation\
**Applies to:** Local development installations of EduAnalytics

------------------------------------------------------------------------

## 1. Purpose

This document defines the Developer role and its supporting tools for
EduAnalytics. It is intended for people who clone the public repository
and need controlled access to inspect, maintain, troubleshoot, and reset
their own development installation.

Developer Administration is an optional engineering and maintenance
extension. It is **not part of the frozen academic MVP**, is not
required for institutional use, and must not delay the academic MVP
milestones.

The implementation must extend the existing Flask application,
authentication system, SQLAlchemy models, and database. It must not
create a separate application or authentication system.

### Goals

-   Introduce a third role: Developer.
-   Give Developers the approved Administrator capabilities plus
    additional technical permissions.
-   Provide controlled database inspection and CRUD through a protected
    web interface.
-   Provide a local Python script for Developer account provisioning
    without shared credentials.
-   Provide a safe full-database reset and reinitialization procedure.
-   Reuse the existing backup and recovery implementation.
-   Keep Developer functionality unavailable in normal institution
    installations.
-   Preserve existing Administrator and Educator behaviour.

### Out of scope

-   Shared or default usable Developer credentials.
-   Developer access in normal institution deployments.
-   Arbitrary SQL execution or a browser-based SQL terminal.
-   Schema editing through the web interface.
-   Remote or LAN-based Developer administration.
-   A separate application, API service, or database.
-   Automatic Developer account creation during ordinary setup.
-   Changes to academic MVP acceptance criteria.

## 2. Design principles

1.  **Development-only:** Developer tools are for local development, not
    routine institutional operation.
2.  **Disabled by default:** Installing or starting EduAnalytics must
    not enable Developer tools automatically.
3.  **Least privilege:** Every Developer operation must be explicitly
    authorized.
4.  **Server-side enforcement:** Hiding buttons is not access control;
    every route and service must check permissions.
5.  **Controlled CRUD:** Use validated application services and
    SQLAlchemy models. Do not expose arbitrary SQL.
6.  **Recoverability:** Destructive maintenance must have a verified
    recovery path.
7.  **Auditability:** Sensitive actions must be traceable without
    logging credentials or unnecessary student data.
8.  **Compatibility:** Existing Admin and Educator accounts and
    workflows must continue to work.
9.  **Reuse:** Extend existing setup, authentication, database, backup,
    recovery, and logging mechanisms.
10. **Explicit operation:** Account creation and full database reset are
    local operator actions, not ordinary browser workflows.

## 3. Roles and permissions

EduAnalytics will have three roles:

-   **Administrator:** Manages institutional use of the application and
    educator accounts.
-   **Educator:** Uses permitted academic data and analytics features.
-   **Developer:** Maintains a development installation and receives the
    approved Administrator capabilities plus additional technical
    permissions.

A Developer is not simply an institutional Administrator with a
different label.

### 3.1 Permission matrix

This is the target permission model. Inspect existing Admin and Educator
permissions before implementation; do not silently change their current
behaviour.

  --------------------------------------------------------------------------
  Capability             Administrator           Educator          Developer
  ----------------- ------------------ ------------------ ------------------
  Login and logout                 Yes                Yes                Yes

  Use academic                Existing           Existing                Yes
  upload workflow           permission         permission 

  View academic               Existing           Existing                Yes
  analytics                 permission         permission 

  Manage educator                  Yes                 No                Yes
  accounts                                                

  View all            Existing/limited                 No                Yes
  application users                                       

  Manage              Existing/limited                 No                Yes
  non-Developer                                           
  accounts                                                

  Create Developer                  No                 No                 No
  accounts in web                                         
  UI                                                      

  Change own role                   No                 No                 No

  Inspect approved                  No                 No                Yes
  database tables                                         

  Controlled CRUD                   No                 No                Yes
  on approved                                             
  records                                                 

  View database                     No                 No                Yes
  health                                                  

  View application                  No                 No                Yes
  diagnostics                                             

  View Developer                    No                 No                Yes
  audit events                                            

  Initiate full                     No                 No                 No
  reset from web UI                                       

  Run local                         No                 No       Yes, locally
  database reset                                          
  utility                                                 

  Use existing                Existing                 No                Yes
  backup/recovery           permission                    
  tools                                                   
  --------------------------------------------------------------------------

"Developer inherits Administrator capabilities" means the Developer
receives the capabilities explicitly approved for the Administrator
role, plus the additional Developer permissions listed here. It does not
mean bypassing all security checks.

### 3.2 User-management restrictions

-   Passwords must never be displayed or retrieved.
-   Password changes must use the existing password-hashing mechanism.
-   A Developer cannot change their own role through the web interface.
-   A Developer cannot deactivate or delete their own account through
    the web interface.
-   The last active Developer account cannot be deleted or deactivated
    through the web interface.
-   The web interface cannot create additional Developer accounts.
-   Developer provisioning must use the local CLI script.
-   Prefer account deactivation over deletion where foreign-key
    relationships or audit requirements make deletion unsafe.
-   Role changes must be validated and audit logged.

## 4. Development-only availability

Developer functionality must be disabled by default and available only
in an explicitly configured development installation.

### 4.1 Configuration

Use settings equivalent to:

  -------------------------------------------------------------------------------------
  Setting                               Default                 Purpose
  ------------------------------------- ----------------------- -----------------------
  `EDUANALYTICS_DEV_TOOLS_ENABLED`      `false`                 Enables Developer
                                                                functionality

  `EDUANALYTICS_DEV_TOOLS_LOCAL_ONLY`   `true`                  Restricts Developer web
                                                                access to local-host
                                                                requests

  `EDUANALYTICS_ENV`                    Existing project        Identifies installation
                                        default; must not imply environment
                                        development             
  -------------------------------------------------------------------------------------

The exact configuration mechanism must follow existing project
conventions. Do not introduce a competing configuration system.

### 4.2 Enablement rules

-   Developer tools are disabled unless explicitly enabled.
-   A Developer account existing in the database does not enable
    Developer tools.
-   Ordinary `setup.ps1` and normal startup defaults must not enable
    Developer tools.
-   The provisioning script must refuse to create an account unless the
    installation is explicitly configured for development and Developer
    tools are enabled.
-   Production or institution installations must deny Developer access
    even if a Developer role exists in the database.
-   Local-only access must use a carefully reviewed host/IP policy. Do
    not trust arbitrary forwarded headers unless a trusted proxy is
    explicitly configured.
-   When disabled, all Developer routes and services must deny access,
    including direct URL requests.
-   Configuration documentation must not expose secrets.

### 4.3 LAN behaviour

The regular application may continue to support institution-LAN access.
Developer tools must not become available to LAN clients merely because
the main application listens on `0.0.0.0`.

Initial implementation is local-host only. Remote Developer access
requires a separate requirement and security review.

## 5. Developer account provisioning

### 5.1 Command

Create a local CLI script:

``` powershell
python scripts/create_dev_account.py
```

The script is public source code, but each installation creates its own
credentials. Never commit a working default username, password, password
hash, or reusable credential.

### 5.2 Script requirements

The script must:

1.  Load the existing Flask application factory and configuration.
2.  Verify the installation is explicitly configured for development.
3.  Verify Developer tools are enabled.
4.  Verify the database is available and initialized, or instruct the
    operator to run normal setup first.
5.  Prompt for a username.
6.  Prompt for a password and confirmation using `getpass`, without
    echoing it.
7.  Apply the project's password policy.
8.  Check username uniqueness.
9.  Refuse to overwrite or silently modify an existing account.
10. Hash the password using the application's established mechanism.
11. Create the account in a transaction.
12. Assign the supported Developer role value.
13. Report success without printing credentials or hashes.
14. Return a useful non-zero exit status on failure.

### 5.3 Restrictions

-   Do not create a Developer account automatically during normal setup.
-   Do not add a shared default password to README or source code.
-   Do not accept passwords as command-line arguments.
-   Do not log credentials.
-   Do not make the script a general-purpose role-escalation utility.
-   If a Developer account already exists, require a separately designed
    recovery procedure rather than silently changing it.

### 5.4 Expected experience

``` text
EduAnalytics — Developer Account Setup

Checking development configuration...
Checking database...

Username: developer
Password: ********
Confirm password: ********

Developer account created successfully.
You can now sign in to your local EduAnalytics development installation.
```

Exact messages may vary, but no secret may be displayed.

## 6. Developer interface

### 6.1 Route namespace

Use a dedicated route prefix: `/developer/`.

Proposed routes:

  ----------------------------------------------------------------------------------------
  Route                                                Purpose
  ---------------------------------------------------- -----------------------------------
  `/developer/`                                        Developer dashboard

  `/developer/users`                                   User inspection and permitted
                                                       management

  `/developer/database`                                Database overview

  `/developer/database/tables`                         Approved table listing

  `/developer/database/records/<resource>`             Paginated record browsing

  `/developer/database/records/<resource>/<id>/edit`   Edit an approved record

  `/developer/backups`                                 Backup and recovery
                                                       information/actions

  `/developer/diagnostics`                             Application diagnostics

  `/developer/audit-log`                               Developer audit events

  `/developer/maintenance`                             Maintenance guidance and status
  ----------------------------------------------------------------------------------------

Adapt routes to the repository's existing Flask blueprint conventions.

### 6.2 Dashboard

Display useful, non-secret technical information:

-   Application name and version, if available.
-   Environment and Developer-tools enabled/disabled state.
-   Database connection status.
-   Database file size and safe display of its location.
-   Database table count.
-   Total users, datasets, and student records.
-   Latest verified backup information, if available.
-   Database integrity status and check time.
-   Links to permitted maintenance tools.

The dashboard is read-only. Never expose secret keys, passwords,
password hashes, session cookies, tokens, or sensitive environment
variables.

### 6.3 Navigation

Developer navigation must be separate from normal Admin and Educator
navigation. Only authorized Developers should see it. Backend
authorization remains mandatory regardless of what the interface
displays.

## 7. Database explorer and controlled CRUD

### 7.1 General approach

Use application-level operations implemented through SQLAlchemy models
and validated service functions.

Do not provide:

-   An arbitrary SQL editor.
-   Unrestricted table or schema modification.
-   Direct execution of user-supplied SQL.
-   Unbounded record dumps.
-   Access to password hashes or secret fields.

### 7.2 Initial resource permissions

This is a proposed starting point. Confirm actual model fields,
relationships, constraints, and existing behaviour before implementing
each operation.

  ------------------------------------------------------------------------
  Resource              Read          Create         Update         Delete
  ----------- -------------- --------------- -------------- --------------
  Users        Yes, redacted            Yes,   Yes, guarded     Restricted
                               non-Developer                
                                       roles                

  Datasets               Yes      Controlled     Controlled     Restricted

  Student                Yes      Controlled     Controlled Yes, confirmed
  Records                                                   

  Upload       Yes, redacted         Through             No     Restricted
  Errors                         application                
                                    workflow                
  ------------------------------------------------------------------------

### 7.3 CRUD safeguards

Every operation must:

1.  Require an authenticated Developer.
2.  Check that Developer tools are enabled and the request is
    local-only.
3.  Validate the resource against a server-side allowlist.
4.  Load records through SQLAlchemy rather than accepting arbitrary
    table names or SQL fragments.
5.  Validate submitted fields against explicit editable-field
    allowlists.
6.  Apply the same data rules as the corresponding application workflow
    wherever possible.
7.  Preserve foreign-key relationships and database constraints.
8.  Use transactions and handle failures safely.
9.  Require confirmation for destructive changes.
10. Write an audit event after the operation outcome is known.

Use pagination and reasonable page sizes. Redact sensitive fields from
record views and logs.

### 7.4 Dataset and student-record consistency

Student records must remain scoped to their parent dataset. A Developer
must not move a record to an unrelated dataset by changing a hidden form
value.

Dataset-specific grade limits and assessment metadata must be respected.
Missing values must remain distinguishable from zero.

Do not alter the established student-record primary-key strategy or
schema without a separate migration decision.

## 8. Backup and recovery integration

EduAnalytics already has database backup and recovery functionality.
Reuse it rather than creating a second backup system.

Developer tools may:

-   View available backup metadata.
-   Create a manual backup using the existing backup service.
-   Verify backup integrity.
-   Restore a selected backup using the existing recovery procedure.
-   Display backup and recovery outcomes.

Requirements:

-   Backups remain outside the Git repository.
-   The configured backup location is shown clearly to the local
    operator.
-   Backup files are not exposed for unrestricted download through the
    web interface.
-   Backup access is restricted to authorized local operating-system
    users.
-   A backup is verified before it is treated as a valid safety backup.
-   Restore follows the existing safe recovery procedure, including
    stopping application activity where required.
-   Reset must not automatically delete existing backup or rollback
    files.

## 9. Full database reset and reinitialization

### 9.1 Reset method

A full reset must use a local maintenance script, not an ordinary
browser request.

Proposed command:

``` powershell
.\stop.ps1
python scripts/reset_database.py
```

The script must refuse to proceed if it cannot establish that the
application is stopped and the database is not in use. Process detection
must be designed and tested for the supported Windows environment.

### 9.2 Reset procedure

The script must:

1.  Confirm the installation is explicitly configured for development.
2.  Confirm Developer tools are enabled.
3.  Confirm the operator is running the command locally.
4.  Identify the exact database path from application configuration.
5.  Display institution and record counts where safely available.
6.  Create a safety backup using the existing backup implementation.
7.  Verify the safety backup.
8.  Require the exact confirmation phrase `RESET DATABASE`.
9.  Ensure no application or other process is using the database.
10. Recreate the schema using the approved application initialization
    mechanism.
11. Apply normal database initialization.
12. Run a database integrity check.
13. Verify required tables and relationships.
14. Verify that application data tables contain no institution, user,
    dataset, student-record, or upload-error data.
15. Report success only after all verification steps pass.

### 9.3 Preservation rules

  Item                                   Expected result
  -------------------------------------- -----------------
  Administrator accounts                 Removed
  Educator accounts                      Removed
  Developer accounts                     Removed
  Institution registration               Removed
  Datasets                               Removed
  Student records                        Removed
  Upload error records                   Removed
  Database schema                        Recreated
  Application secret-key configuration   Preserved
  Python environment and dependencies    Preserved
  Source code and repository files       Preserved
  Existing backup files                  Preserved

Derive the exact tables from implemented models and initialization code.
Do not assume dropping every table is safe.

### 9.4 First-run setup

After successful reset:

-   The application behaves as a fresh installation.
-   First-run institution registration and initial Administrator setup
    are available.
-   The Developer account is removed because it is stored in the reset
    database.
-   To use Developer tools again, the operator completes the required
    setup, enables development configuration, and runs the Developer
    provisioning script.
-   Application secret-key configuration and the external backup
    directory remain intact.

### 9.5 Failure and recovery

-   Never report success before schema and integrity verification pass.
-   If reset fails, preserve the safety backup.
-   Show a clear error and the safety-backup location.
-   Do not automatically delete or overwrite the safety backup.
-   Document recovery using the existing restore procedure.
-   Do not leave the application appearing ready with a partial or
    invalid schema.

## 10. Diagnostics

The Developer diagnostics page may show:

-   Python version.
-   EduAnalytics version or Git revision, if available.
-   Flask and relevant dependency versions.
-   Database connectivity.
-   SQLite integrity-check result.
-   Required-table presence.
-   Backup-directory availability and basic status.
-   Recent application errors, with sensitive values redacted.

Do not display secret keys, passwords or hashes, session cookies or
tokens, full environment dumps, unredacted personal or academic records,
or unnecessary sensitive filesystem paths.

Diagnostics must not execute arbitrary shell commands or Python code
submitted through the browser.

## 11. Audit logging

Sensitive Developer operations must be recorded.

### Events

-   Developer account provisioning.
-   User creation, update, activation, deactivation, and deletion
    attempts.
-   Role changes.
-   Dataset and student-record create/update/delete operations.
-   Backup creation and verification.
-   Backup restoration.
-   Database reset attempts and outcomes.
-   Access-denied events for protected Developer operations.

### Audit fields

  Field              Meaning
  ------------------ -----------------------------------------------------
  Actor              User ID or local operator identity, where available
  Action             Operation performed
  Resource           Affected resource or table
  Record reference   Affected record identifier, where applicable
  Timestamp          Date and time
  Outcome            Success or failure
  Context            Minimal non-sensitive explanation

Never record passwords, password hashes, secret keys, session tokens, or
complete student records.

A full reset removes database-resident audit records. The reset utility
must therefore write a minimal reset event to a local maintenance log
stored outside the database and outside the repository. This log must
not contain credentials or sensitive academic data. It is a local
operational record, not a centrally managed audit service.

## 12. Proposed application structure

Adapt this structure to the repository's actual conventions when
implementation begins:

``` text
EduAnalytics/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   ├── datasets/
│   ├── analytics/
│   └── developer/
│       ├── __init__.py
│       ├── routes.py
│       ├── permissions.py
│       ├── forms.py
│       ├── services.py
│       └── templates/
│           ├── dashboard.html
│           ├── users.html
│           ├── database.html
│           ├── records.html
│           ├── backups.html
│           ├── diagnostics.html
│           ├── audit_log.html
│           └── maintenance.html
├── scripts/
│   ├── create_dev_account.py
│   └── reset_database.py
├── tests/
│   └── developer/
│       ├── test_configuration.py
│       ├── test_permissions.py
│       ├── test_account_creation.py
│       ├── test_database_crud.py
│       ├── test_backup_integration.py
│       ├── test_reset.py
│       └── test_audit_log.py
└── docs/
    └── Developer_Administration.md
```

### Component responsibilities

  -----------------------------------------------------------------------
  Component                           Responsibility
  ----------------------------------- -----------------------------------
  `developer/routes.py`               Developer web routes

  `developer/permissions.py`          Centralized role and environment
                                      checks

  `developer/forms.py`                Validated forms and confirmation
                                      inputs

  `developer/services.py`             Controlled database operations and
                                      maintenance integration

  `create_dev_account.py`             Local Developer account
                                      provisioning

  `reset_database.py`                 Offline full database reset

  `tests/developer/`                  Developer-specific security and
                                      behaviour tests
  -----------------------------------------------------------------------

Do not duplicate existing models, authentication logic, database
initialization, or backup code.

## 13. Testing requirements

Developer Administration must have its own automated tests and must also
run the existing application regression suite.

### 13.1 Configuration and access

-   Developer tools are disabled by default.
-   A Developer account alone does not enable Developer tools.
-   Non-development installations deny Developer access.
-   Local-only restrictions reject non-local requests.
-   Educators cannot access Developer routes.
-   Administrators cannot access Developer routes unless a separately
    approved permission is introduced.
-   A Developer can access permitted routes only when all configuration
    conditions are met.
-   Direct URL access is protected by backend checks.

### 13.2 Account provisioning

-   Valid local provisioning creates a Developer account.
-   Password input is not echoed.
-   Passwords are stored as hashes.
-   Duplicate usernames are rejected.
-   Existing accounts are not silently modified.
-   Provisioning is rejected when Developer tools are disabled.
-   Provisioning is rejected outside a development installation.
-   Failed account creation leaves no partial user record.

### 13.3 CRUD

-   Only approved resources can be accessed.
-   Only allowlisted fields can be modified.
-   Invalid values are rejected.
-   Foreign-key relationships remain valid.
-   Student records remain associated with their parent dataset.
-   Sensitive fields are redacted.
-   Transactions roll back after failures.
-   Successful and failed sensitive operations are audited.

### 13.4 Reset

Use an isolated temporary test database. Never run reset tests against a
developer's real working database.

-   Reset refuses to run outside a development installation.
-   Reset refuses to run when Developer tools are disabled.
-   Reset refuses to proceed when the database is in use.
-   Reset creates and verifies a safety backup.
-   Reset requires the exact confirmation phrase.
-   Reset recreates the required schema.
-   Reset removes application records and accounts.
-   Reset preserves application secret-key configuration.
-   Reset preserves existing backup files.
-   Reset verifies database integrity.
-   A failed reset preserves the safety backup and reports failure.
-   First-run setup is available after successful reset.

### 13.5 Regression

Verify that:

-   Administrator login and logout still work.
-   Educator login and logout still work.
-   Existing role restrictions remain unchanged.
-   CSV upload and validation still work.
-   Dataset records and relationships remain correct.
-   Backup and recovery still work.
-   Setup and startup scripts still work.
-   Normal authorized LAN access is unaffected.
-   Developer tools remain unavailable to normal institution
    installations.

## 14. Phased implementation plan

Developer Administration is a separate development workstream. It is not
Sprint 6 and must not be added to the MVP scope or acceptance criteria.
The workstream must be completed before `Sprint 6 --- Dataset Management`
begins, subject to the project's agreed release and testing decisions.

Implement one phase at a time in a small, reviewable change. Do not begin
the next phase until the current phase's completion gate has passed.

### 14.1 Phase status rules

Each phase must have one of these statuses in this document:

-   **Not started** --- no implementation work has been accepted.
-   **In progress** --- implementation is underway; acceptance is not yet
    complete.
-   **Complete** --- deliverables, tests, security review, and documentation
    update for the phase are complete.
-   **Blocked** --- work cannot continue without an explicit decision or
    external dependency. Record the reason and required action.

The phase status, implementation notes, test evidence, and known issues must
be updated in this document after each phase. A phase must not be marked
complete merely because its code exists.

### 14.2 Phase D0 --- Workstream preparation

**Status:** Not started

**Objective:** Establish the implementation boundary and a reproducible
baseline before changing application behaviour.

**Deliverables:**

1. Confirm that this workstream is separate from Sprint 6 and the frozen MVP.
2. Record the current Administrator and Educator permissions.
3. Record the current models, relationships, setup flow, database path,
   backup path, and recovery procedure.
4. Confirm the supported Python and Windows environment.
5. Restore the project's test command and record a clean baseline result.
6. Confirm that no shared Developer credentials exist in source or docs.

**Tests and review:** Existing application tests pass before implementation
begins, or all baseline failures are documented with an owner and reason.

**Completion gate:** The repository architecture, test baseline, and scope
boundary are documented; no application behavior has been changed.

### 14.3 Phase D1 --- Configuration and centralized authorization

**Status:** Not started

**Objective:** Add secure, disabled-by-default gates for all Developer
functionality.

**Deliverables:**

1. Add the development-environment and Developer-tools configuration values
   using existing project conventions.
2. Default Developer tools to disabled.
3. Add the `developer` role value without changing existing role values.
4. Add centralized checks for environment, enablement, active Developer
   status, and local-only requests.
5. Define the approved Administrator capabilities inherited by Developers.
6. Keep Developer-only capabilities separate from Administrator access.

**Tests:** Disabled-by-default, non-development denial, local-only denial,
Educator denial, Administrator denial for Developer-only routes, and direct
URL protection.

**Completion gate:** Every future Developer route and service has a
centralized authorization path, and existing Admin/Educator tests remain
green.

### 14.4 Phase D2 --- Local Developer account provisioning

**Status:** Not started

**Objective:** Provide secure per-installation Developer account creation.

**Deliverables:**

1. Implement `python scripts/create_dev_account.py`.
2. Load the existing application factory and database configuration.
3. Refuse execution unless the installation is explicitly configured for
   development and Developer tools are enabled.
4. Prompt for credentials with `getpass` and enforce the existing password
   policy.
5. Reject duplicate usernames and existing accounts without modifying them.
6. Hash the password through the established application mechanism.
7. Commit transactionally and return useful non-zero failure statuses.
8. Never print or log passwords, hashes, or reusable credentials.

**Tests:** Successful creation, duplicate rejection, disabled-tool rejection,
non-development rejection, password-hash verification, no-echo input, and
rollback after failure.

**Completion gate:** A fresh development installation can create exactly the
intended Developer account through the local CLI without exposing secrets.

### 14.5 Phase D3 --- Developer blueprint and protected dashboard

**Status:** Not started

**Objective:** Introduce a separate Developer web area with safe operational
visibility.

**Deliverables:**

1. Add the `app/developer/` blueprint and `/developer/` route namespace.
2. Implement the Developer dashboard.
3. Add separate Developer navigation visible only to authorized Developers.
4. Display safe environment, database, table-count, record-count, and
   integrity information.
5. Redact secrets, password hashes, tokens, and unnecessary personal or
   academic data.

**Tests:** Authorized Developer access, denial for all other roles, disabled
configuration denial, local-only denial, safe output checks, and dashboard
failure handling.

**Completion gate:** The dashboard is useful for local maintenance while
revealing no protected secrets or unrestricted records.

### 14.6 Phase D4 --- Read-only database explorer

**Status:** Not started

**Objective:** Provide safe inspection of approved resources before allowing
mutations.

**Deliverables:**

1. Implement explicit resource definitions for Users, Institutions,
   Datasets, Student Records, and Upload Errors.
2. Add paginated listing and record views.
3. Define display fields and redacted fields per resource.
4. Reject arbitrary table names, SQL fragments, and unbounded dumps.
5. Preserve dataset/student-record scoping in all views.

**Tests:** Resource allowlist, pagination, redaction, relationship scoping,
unauthorized access, and malformed-resource rejection.

**Completion gate:** Developers can inspect approved data without arbitrary SQL
or accidental exposure of sensitive fields.

### 14.7 Phase D5 --- Audit logging foundation

**Status:** Not started

**Objective:** Make sensitive Developer activity traceable before enabling
mutating operations.

**Deliverables:**

1. Add the audit event model/service or approved equivalent.
2. Record actor, action, resource, record reference, timestamp, outcome, and
   minimal context.
3. Redact credentials, hashes, secrets, tokens, and complete student data.
4. Define the external maintenance-log format for reset events.
5. Add audit handling for both successful and failed protected operations.

**Tests:** Event creation, failure events, redaction, actor attribution,
transaction behavior, and reset-log safety.

**Completion gate:** The application can account for sensitive Developer
operations without creating a second source of sensitive data.

### 14.8 Phase D6 --- Controlled CRUD services

**Status:** Not started

**Objective:** Add narrowly scoped, validated maintenance operations.

**Deliverables:**

1. Implement server-side resource and editable-field allowlists.
2. Add permitted user-management operations for non-Developer accounts.
3. Add controlled Dataset and StudentRecord updates.
4. Keep UploadError operations read-only unless a later decision approves
   otherwise.
5. Require confirmation for destructive actions.
6. Use SQLAlchemy services, transactions, validation, and audit events.
7. Prevent student records from being moved to unrelated datasets.

**Tests:** Valid and invalid field updates, relationship preservation,
transaction rollback, deletion safeguards, self-account restrictions,
redaction, and success/failure audit events.

**Completion gate:** Every supported mutation is allowlisted, validated,
recoverable, and covered by security tests.

### 14.9 Phase D7 --- Backup and recovery integration

**Status:** Not started

**Objective:** Reuse and expose existing backup/recovery behavior safely.

**Deliverables:**

1. Extract shared backup/recovery services where needed.
2. Reuse the existing verified backup implementation.
3. Display backup metadata and verification outcomes.
4. Permit only authorized local Developer operations.
5. Do not expose backup files for unrestricted web download.
6. Preserve external backup storage and rollback behavior.

**Tests:** Backup creation, verification, metadata display, restore safeguards,
failure handling, and compatibility with existing backup/recovery tests.

**Completion gate:** Developer integration uses the same trusted backup and
recovery path as the existing maintenance scripts.

### 14.10 Phase D8 --- Offline full database reset

**Status:** Not started

**Objective:** Provide a safe local reset and return the application to
first-run state.

**Deliverables:**

1. Implement `scripts/reset_database.py`.
2. Require development configuration and enabled Developer tools.
3. Resolve and display the exact database path.
4. Detect active application/database use on supported Windows setups.
5. Create and verify a safety backup before destructive work.
6. Require the exact confirmation phrase `RESET DATABASE`.
7. Recreate the schema using the approved initialization mechanism.
8. Verify integrity, required tables, empty application data, preserved
   configuration, and preserved external backups.
9. Preserve the safety backup after success or failure.
10. Write a minimal external maintenance event.

**Tests:** Refusal outside development, refusal when enabled flag is false,
active-process refusal, safety-backup verification, confirmation handling,
successful reset, failed reset recovery, schema verification, and first-run
setup availability.

**Completion gate:** Reset is proven against isolated temporary databases and
never against a real working installation during automated testing.

### 14.11 Phase D9 --- Diagnostics and complete Developer audit interface

**Status:** Not started

**Objective:** Complete the operational maintenance experience without
exposing sensitive internals.

**Deliverables:**

1. Add diagnostics for Python, application version, dependencies, database,
   required tables, backups, and recent redacted errors.
2. Add the protected Developer audit-log view.
3. Add maintenance guidance and status screens where useful.
4. Confirm that no browser-submitted shell command or Python execution is
   possible.

**Tests:** Safe diagnostics output, redaction, audit filtering, denial of
   arbitrary execution, and error handling.

**Completion gate:** Diagnostics and audit information are actionable for
   local development while remaining bounded and non-secret.

### 14.12 Phase D10 --- Security, regression, and acceptance verification

**Status:** Not started

**Objective:** Verify the complete workstream without regressing the core
   application.

**Deliverables:**

1. Run all Developer-specific tests.
2. Run the complete existing application regression suite.
3. Verify Administrator and Educator login and workflows.
4. Verify CSV upload, validation, backup, recovery, setup, and startup.
5. Verify Developer tools are unavailable in normal institution settings.
6. Review all acceptance criteria DEV-01 through DEV-21.
7. Record known limitations and unresolved risks.

**Completion gate:** All Must criteria pass, or any exception is explicitly
approved and documented before the workstream is declared complete.

### 14.13 Phase D11 --- Documentation and handoff

**Status:** Not started

**Objective:** Publish operational documentation only after implementation
and verification are complete.

**Deliverables:**

1. Update this document with final phase statuses and test evidence.
2. Update the root `README.md` with only implemented and tested commands,
   routes, configuration, backup, recovery, and reset behavior.
3. Confirm that no shared/default credentials are documented.
4. Confirm that institution deployments are explicitly warned not to enable
   Developer tools.
5. Review the final diff and repository status.
6. Commit the completed work and push it to the configured GitHub repository
   only after user review and approval.

**Completion gate:** Documentation matches the shipped behavior exactly and
the final changes are reviewed before publication.

### 14.14 Phase update protocol

After completing each phase:

1. Run the phase-specific tests and the relevant regression tests.
2. Review the implementation against that phase's deliverables.
3. Update the phase status from **In progress** to **Complete** only when its
   completion gate passes.
4. Add a concise implementation note, test command, result, and any known
   limitations below the phase or in the project change record.
5. Do not update `README.md` with unfinished functionality.
6. Do not push to GitHub until the complete workstream has passed Phase D10,
   Phase D11 documentation review, and explicit user approval.

Do not implement all phases in one large change. Keep the integrated
application working throughout the workstream.

## 15. README documentation requirements

After implementation, update the root `README.md` with a concise
Developer section explaining:

-   Developer tools are optional and intended only for local development
    installations.
-   Developer tools are disabled by default.
-   How to enable development configuration.
-   How to run `python scripts/create_dev_account.py`.
-   How to sign in locally.
-   What Developer tools can do.
-   How to run the safe reset utility.
-   Where backups are stored and how to recover.
-   No shared/default credentials are provided.
-   Developer access must not be enabled on institution deployments.

The README must describe only functionality that has actually been
implemented and tested. Do not publish instructions for unfinished
commands or screens. This document is the detailed specification; README
instructions should be shorter and operational.

## 16. Acceptance criteria

The Developer extension is complete only when all Must requirements
below have been implemented and verified.

  -----------------------------------------------------------------------
  ID                      Acceptance criterion    Priority
  ----------------------- ----------------------- -----------------------
  DEV-01                  Developer tools are     Must
                          disabled by default     

  DEV-02                  Developer tools are     Must
                          available only in an    
                          explicitly configured   
                          development             
                          installation            

  DEV-03                  Local-only Developer    Must
                          web access is enforced  

  DEV-04                  A Developer account can Must
                          be created using the    
                          local Python script     

  DEV-05                  Developer credentials   Must
                          are securely hashed     

  DEV-06                  No shared usable        Must
                          default credentials are 
                          committed               

  DEV-07                  Only Developers can     Must
                          access Developer routes 
                          when enabled            

  DEV-08                  Developers receive the  Must
                          approved Administrator  
                          capabilities            

  DEV-09                  Developers can inspect  Must
                          approved database       
                          resources               

  DEV-10                  Controlled CRUD         Must
                          validates fields and    
                          preserves relationships 

  DEV-11                  Sensitive fields are    Must
                          redacted                

  DEV-12                  Sensitive Developer     Must
                          operations are audit    
                          logged                  

  DEV-13                  Existing backup and     Must
                          recovery mechanisms are 
                          reused                  

  DEV-14                  Full reset requires a   Must
                          verified safety backup  
                          and explicit            
                          confirmation            

  DEV-15                  Full reset recreates    Must
                          the schema and verifies 
                          database integrity      

  DEV-16                  Successful reset        Must
                          returns the application 
                          to first-run setup      

  DEV-17                  Reset preserves         Must
                          application             
                          configuration and       
                          backup files            

  DEV-18                  Existing Admin and      Must
                          Educator workflows      
                          continue working        

  DEV-19                  Developer functionality Must
                          is unavailable in       
                          normal institution      
                          deployments             

  DEV-20                  Developer security and  Must
                          regression tests pass   

  DEV-21                  README and maintenance  Must
                          documentation reflect   
                          implemented behaviour   
  -----------------------------------------------------------------------

A feature is not complete merely because its interface exists. It must
be implemented, tested, and verified.

## 17. Risks and mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  Developer tools enabled in an       Disabled-by-default configuration
  institution installation            and environment checks

  LAN users reach Developer tools     Local-only enforcement and backend
                                      authorization

  Shared credentials become public    Per-installation CLI provisioning;
                                      no default password

  CRUD damages relationships          SQLAlchemy services, allowlists,
                                      validation, transactions

  Sensitive data appears in console   Field redaction, pagination, access
                                      checks

  Reset destroys useful data          Verified backup, explicit
                                      confirmation, offline reset

  Reset runs while application is     Stop and process-use checks before
  active                              database replacement

  Existing roles break                Compatibility and regression tests

  Maintenance logs expose private     Minimal event fields and redaction
  data                                

  Developer work delays academic MVP  Separate post-MVP milestone
  -----------------------------------------------------------------------

## 18. Change control

This specification is the design baseline for the Developer
Administration extension. Record and review design changes before
implementation.

Any proposal to enable Developer tools on institution deployments, allow
remote Developer access, add arbitrary SQL execution, or change reset
behaviour requires a separate security and scope review.

The frozen academic MVP remains governed by
`MVP_Scope_and_Requirements.md`. Developer Administration must not be
added to that document's MVP acceptance criteria.

## 19. Final design decision

The agreed design is:

-   A third role named **Developer**.
-   Developer inherits the approved Administrator capabilities.
-   Additional controlled database inspection and CRUD.
-   Development installations only.
-   Developer tools disabled by default.
-   Local-only web access by default.
-   Developer accounts created only through a local Python CLI.
-   No shared default credentials.
-   No arbitrary SQL console.
-   Full database reset through a local maintenance script.
-   Verified safety backup before reset.
-   Existing backup and recovery mechanisms reused.
-   Separate audit logging and acceptance criteria.
-   Implementation after the academic MVP is complete.
-   README updated only when functionality is implemented and verified.

**Status:** Design baseline finalized for future implementation. No
Developer Administration functionality is implied to exist until the
implementation roadmap and acceptance criteria have been completed.
