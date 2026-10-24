# Sprint 3 --- Authentication and Educator Account Management

**Project:** EduAnalytics --- Student Academic Performance Analytics
Platform\
**Sprint:** Sprint 3\
**Area:** Authentication, authorization, educator account management,
and related security controls\
**Last updated:** 24 October 2026

## 1. Sprint overview

Sprint 3 established the authentication and access-control foundation
for EduAnalytics. The goal was to let users sign in securely, restrict
functionality according to their roles, and allow administrators to
create and manage educator accounts.

The sprint also added a basic authenticated home page and logout
workflow. The educator-management interface was restyled while
preserving the existing backend routes and form field names.

This sprint provides the account and access foundation needed before
building the platform's main academic-data workflows. It does **not**
mean the academic analytics features are complete.

### Objectives

-   Authenticate users with a user ID and password.
-   Store password hashes rather than plaintext passwords.
-   Restrict protected pages to authenticated users.
-   Restrict educator-management operations to administrators.
-   Allow administrators to create educator accounts.
-   Allow administrators to activate and deactivate educator accounts.
-   Reject inactive accounts at login and prevent deactivated users from
    continuing to use an existing session on subsequent requests.
-   Protect form submissions with CSRF tokens.
-   Require a configured Flask secret key.
-   Provide a home page and logout control.
-   Verify the implementation with automated tests and manual browser
    checks.

## 2. Scope and status summary

  -----------------------------------------------------------------------------
  Work area                 Status                  Evidence / notes
  ------------------------- ----------------------- ---------------------------
  Login and credential      Completed and tested    Tests cover valid login and
  verification                                      rejected credentials.

  Password hashing          Implemented and tested  Account creation uses
                                                    `generate_password_hash`;
                                                    login uses
                                                    `check_password_hash`.

  Inactive-account login    Completed and tested    Automated test covers
  rejection                                         inactive-account login
                                                    rejection.

  Protected home page       Implemented and         `/` requires login and
                            manually verified       renders `home.html`.

  Logout workflow           Implemented and         CSRF-protected POST form
                            manually verified       redirects to login with a
                                                    success message.

  Role-based authorization  Implemented and tested  Administrator-only educator
                                                    management; unauthorized
                                                    educator access returns
                                                    403.

  Educator account creation Implemented and tested  Validates required fields,
                                                    password length and
                                                    confirmation, institution,
                                                    duplicate user ID, and
                                                    duplicate email.

  Educator                  Implemented and tested  Status changes use a POST
  activation/deactivation                           route and appear in the
                                                    table.

  CSRF protection           Implemented and tested  Global protection is enabled;
                                                    route-specific failure tests
                                                    cover educator creation and
                                                    status changes.

  Missing secret-key        Implemented and         Startup raises
  protection                manually verified       `RuntimeError` when
                                                    `SECRET_KEY` is absent.

  SQLite foreign-key        Implemented             SQLAlchemy connection event
  enforcement                                       enables
                                                    `PRAGMA foreign_keys=ON`.

  Educator-management UI    Implemented and         Responsive styling, cards,
                            visually checked        form layout, status badges,
                                                    and action buttons.

  Automated regression      Passing                 Latest recorded full run:
  suite                                             **39 passed**.

  Local/LAN verification    Partially verified      Non-debug Waitress run and
                                                    second-device home Wi-Fi
                                                    access were verified.
                                                    Institution firewall review
                                                    remains pending.

  Academic import and       Future work / outside   CSV import, validation,
  analytics                 completed scope         dashboards, charts, and
                                                    exports remain future
                                                    features.
  -----------------------------------------------------------------------------

"Completed" means implemented with the verification evidence noted
above. It does not imply a formal security audit or production-readiness
review.

## 3. Architecture and relevant files

The application uses Flask, Flask-Login, Flask-WTF CSRF protection,
Flask-SQLAlchemy, SQLite, and Werkzeug password-hashing utilities.

  --------------------------------------------------------------------------
  File                                   Responsibility
  -------------------------------------- -----------------------------------
  `app/__init__.py`                      Application factory, configuration,
                                         extension initialization, blueprint
                                         registration, table creation,
                                         protected home route.

  `app/extensions.py`                    SQLAlchemy and Flask-Login
                                         initialization; SQLite foreign-key
                                         enforcement.

  `app/models.py`                        Database models including
                                         `Institution` and `User`.

  `app/auth/__init__.py`                 Authentication blueprint with
                                         `/auth` prefix.

  `app/auth/routes.py`                   Login and logout routes.

  `app/auth/decorators.py`               `role_required` authorization
                                         decorator.

  `app/admin/__init__.py`                Administration blueprint with
                                         `/admin` prefix.

  `app/admin/routes.py`                  Educator listing, creation, and
                                         status changes.

  `app/templates/auth/login.html`        Login interface.

  `app/templates/home.html`              Authenticated home page and logout
                                         form.

  `app/templates/admin/educators.html`   Educator creation form, educator
                                         table, status indicators,
                                         activation/deactivation controls.

  `scripts/initialize_database.py`       Initial institution and
                                         administrator setup.

  `tests/test_auth.py`                   Login, inactive-account, CSRF, and
                                         logout tests.

  `tests/test_authorization.py`          Authorization, educator creation,
                                         and status tests.

  `tests/test_database_models.py`        Database-model tests.

  `tests/test_app.py`                    Application-level tests.
  --------------------------------------------------------------------------

## 4. Authentication implementation

### 4.1 Login

The login page is available at `/auth/login` and accepts GET and POST
requests.

On POST, the application reads the user ID and password, looks up the
user, verifies the password hash, and rejects the request if the user
does not exist, the password is incorrect, or the account is not active.
Successful authentication uses Flask-Login and redirects to the home
page.

The login page uses a generic error message for invalid credentials or
inactive accounts:

> Invalid user ID or password, or account is inactive.

### 4.2 Password storage

Passwords are hashed using Werkzeug's `generate_password_hash` before
storage. Login uses `check_password_hash` to verify a submitted
password. Passwords should never be stored or logged in plaintext.

### 4.3 Inactive accounts and sessions

The login route rejects users whose status is not `active`. The project
also implemented and tested the behavior intended to prevent deactivated
users from continuing to use an existing authenticated session on later
requests. The automated suite includes authorization/status coverage,
and browser testing confirmed that an inactive educator could not log
in.

### 4.4 Logout

Logout is implemented at `POST /auth/logout`. The home page submits a
POST request with a CSRF token. Flask-Login clears the authenticated
session and the application redirects to the login page with a success
message.

The endpoint intentionally does not rely on GET. Users should use the
**Log out** button rather than navigating directly to `/auth/logout`.

### 4.5 Protected home page

The home page is available at `/` and is protected by `login_required`.
It renders `app/templates/home.html` and includes a logout form. It is
currently a minimal landing page; a role-specific dashboard or analytics
summary has not yet been implemented.

## 5. Authorization and roles

The `role_required(*allowed_roles)` decorator in
`app/auth/decorators.py` applies login protection and checks the
authenticated user's role. If the role is not allowed, the request is
rejected with HTTP `403 Forbidden`.

Administrator-only routes:

  ------------------------------------------------------------------------------------
  Route                                Method                  Purpose
  ------------------------------------ ----------------------- -----------------------
  `/admin/educators`                   GET                     Display educator
                                                               accounts and creation
                                                               form.

  `/admin/educators/create`            POST                    Create an educator
                                                               account.

  `/admin/educators/<userid>/status`   POST                    Activate or deactivate
                                                               an educator.
  ------------------------------------------------------------------------------------

Manual browser testing confirmed that an educator attempting to access
`/admin/educators` received 403. Automated authorization tests also
cover unauthorized access.

The status-change route checks that the target user exists and has the
educator role, and accepts only `active` or `inactive`. The form uses
POST and includes a CSRF token.

## 6. Educator account creation

The form contains:

-   User ID --- required.
-   First name --- required.
-   Last name --- required.
-   Email --- required.
-   Job title --- optional.
-   Institution --- required.
-   Initial password --- required.
-   Confirm password --- required.

Server-side validation checks required fields, minimum password length
of eight characters, password confirmation, institution validity, and
duplicate user IDs or email addresses. The password is hashed before
storage. Database commit failures are handled with rollback and a
user-facing error message.

`scripts/initialize_database.py` interactively creates the initial
institution and administrator account. It validates required fields and
password confirmation and stores a password hash. Do not rerun it
casually against an existing database; first inspect the current
database and understand the consequences.

Automated tests cover successful educator creation and invalid cases
including duplicate IDs/emails, mismatched passwords, invalid
institution selection, and educator access restrictions. Browser
screenshots showed two test educator records. They do not prove that
every possible validation case was manually exercised.

## 7. Security controls

### 7.1 Secret key

The application reads `SECRET_KEY` from the environment and raises
`RuntimeError` if no key is configured. A manual command removed the key
from a Python process and confirmed that startup failed as expected.

The key is read from the `SECRET_KEY` environment variable. Follow the README's Windows instructions to persist it in the user environment for future sessions. Deployment environments require their own secure secret configuration. Never
commit a real secret key to source control or share it in
logs/screenshots.

### 7.2 CSRF protection

Flask-WTF `CSRFProtect` is initialized globally. Login, logout,
educator-creation, and status-change forms include hidden CSRF tokens.
Tests cover missing-token rejection on login, alongside application and
authorization checks.

Automated regression tests explicitly verify that educator creation and
status-change requests without valid CSRF tokens are rejected.

### 7.3 Password handling

Password hashes are stored instead of plaintext passwords.
Administrators should not be able to retrieve an existing password. If
password reset is added later, it should set a new password through a
controlled workflow.

### 7.4 Database constraints

SQLite foreign-key enforcement is enabled on database connections.
Database integrity and migration strategy should be reviewed before
deployment with shared institutional data.

### 7.5 Development server

The app was run during development with Flask's debug server. The debug
server is for local development, not deployment. Before allowing other
computers to connect, disable debug mode and choose a suitable server
configuration.

## 8. Educator-management interface improvements

The original template used mostly default browser styling. The page was
restyled without changing its backend routes or form field names.

The updated interface includes:

-   EduAnalytics administration header.
-   Clear page heading and supporting text.
-   White cards on a light background.
-   Two-column form on wider screens and a single-column layout on
    narrow screens.
-   Consistent inputs, labels, focus indicators, and buttons.
-   Category-styled flash messages.
-   Scrollable table wrapper for narrow screens.
-   Active/inactive status badges.
-   Separate styles for Activate and Deactivate actions.
-   Empty states for missing institutions or educator records.

The shared base.html template provides a common page structure. Home-page and educator-management styles have been extracted into static/style.css and static/admin.css, respectively. This provides a more maintainable foundation as additional pages are added.

## 9. Testing and verification

### 9.1 Latest automated test result

Command:

```powershell
python -m pytest -q
```

Latest recorded result in this document:

```text
39 passed
```

The test count is a snapshot and may change as the project evolves. Run
the full suite again after any code changes before final submission.

### 9.2 Coverage recorded during the sprint

The suite includes tests for login-page loading, valid login, invalid
password rejection, inactive-account login rejection, missing CSRF token
on login, logout, protected-page redirects, role-based restrictions,
educator creation and validation, duplicate IDs/emails, institution
validation, status changes, invalid status values, and
application/database behavior.

The exact test count may change as the project evolves; `39 passed` is
the latest result recorded in this document, not a permanent acceptance
criterion.

### 9.3 Manual browser checks

The following flows were observed:

-   Administrator login succeeded.
-   The administrator could open educator management.
-   An educator received `403 Forbidden` on the administrator-only page.
-   An educator was deactivated and could not log in.
-   The home page displayed a Log out button.
-   Clicking Log out redirected to login with a success message.
-   The styled educator list displayed status badges and matching
    Activate/Deactivate actions.

A separate non-debug Waitress run was verified locally, and the login
page was accessed from a second device on the same home Wi-Fi network.
The institution network and its firewall policy have not been verified.
These checks are not a formal penetration test or a complete
cross-browser/mobile-device test.

## 10. Pending Actions — Sprint 3 Closure

This section lists only the work that is still unresolved before Sprint 3 can
be closed. Completed checks and implementation tasks are documented above
and are deliberately not repeated here.

### Pending Action 1: Network portability and access restrictions

- [ ] **Verify network portability and document network access limitations.**
    - The PC's current Wi-Fi IPv4 address was identified as `192.168.1.5`.
    - The README documents how to identify the active adapter's IPv4 address
      and use it in the Waitress startup command.
    - A second device previously accessed the login page over the same home
      Wi-Fi network.
    - No new firewall exception was required for that home-network test.
    - When the PC connects to another network, identify the new active
      adapter's IPv4 address and use it in the Waitress command.
    - Access from other devices depends on the network allowing device-to-device
      connections and the applicable firewall policy.
    - Do not disable Windows Firewall or change firewall rules merely to
      make the application accessible.
    - Closure evidence: test access from a second device on another trusted
      network, or document the specific network restriction if access fails.

### Pending Action 2: Database backup restoration test

- [x] **Test restoration of the database backup in a separate location.**
    - Backup used: `backups/eduanalytics_20261024_142054.db`.
    - Backup passed SQLite `PRAGMA integrity_check` (`ok`).
    - Created `backups/restore_test/eduanalytics_restore_test.db`
      without overwriting the working database.
    - Restored copy passed `PRAGMA integrity_check` (`ok`).
    - All five expected tables were present, and row counts matched
      the original database: institution (1), users (3), datasets (0),
      student_records (0), and upload_errors (0).
    - Institution record and user IDs/statuses were readable.
    - Created a separate disposable app-test copy:
      `backups/restore_test/eduanalytics_app_test.db`.
    - `create_app()` initialized successfully against the disposable
      copy; table counts remained unchanged and integrity was `ok`.
    - The original working database was not used for the app test.
    - [x] Created an additional database backup outside the project directory.
        - Backup filename: `eduanalytics_20261024_142054.db`.
        - Backup location: a separate local folder named `EduAnalytics_Backups`.
        - File size: 32,768 bytes.
        - SQLite `PRAGMA integrity_check` returned `ok`.
        - Access-restriction permissions still need verification before
          storing real institutional data.
    - Before real institutional data is used, obtain approval from the
      responsible project or institutional administrator.

### User experience and maintainability

The following implementation and usability checks have been completed or explicitly deferred where they depend on future pages.
Logout controls for future authenticated pages remain deferred until those
pages are implemented.

- [x] Created `base.html`, migrated `home.html` to use it, and extracted
      home and educator page styles into `static/style.css` and
      `static/admin.css`, respectively.
    - Verified the home page and logout behavior.
    - Verified educator page styling.
    - Regression tests passed: 39 tests.
- [ ] Add logout controls to future authenticated pages.
    - Deferred until additional authenticated pages are implemented.
- [x] Added and tested a confirmation prompt before deactivating an educator.
    - Clicking Cancel leaves the educator's status unchanged.
    - Clicking OK submits the request and deactivates the educator.
- [x] Verify keyboard navigation and responsive behavior on a narrow
      viewport.
    - Verified Tab navigation and visible keyboard focus indicators on the
      Educator Management page.
    - Checked the Educator Management layout at a viewport width of 375 px.
    - Confirmed that the layout and controls remained usable during the check.
    - Scope: this is a manual check of the Educator Management page, not a
      complete cross-browser or mobile-device test.

Academic import, analytics, charts, exports, and role-specific dashboards
are future platform features and are not Sprint 3 closure actions.

## 11. Acceptance criteria and final status

The following implementation and verification criteria have evidence
recorded in this document:

- [x] Users can sign in with valid credentials; invalid credentials and
      inactive accounts are rejected.
- [x] Passwords are stored as hashes.
- [x] Protected pages require authentication.
- [x] Administrator-only educator management is role-protected.
- [x] Administrators can create educator accounts with server-side
      validation.
- [x] Administrators can activate and deactivate educator accounts.
- [x] CSRF protection is enabled, and route-specific failure tests cover
      educator creation and status-change requests.
- [x] Missing `SECRET_KEY` prevents application startup.
- [x] Home page and logout workflow work in the browser.
- [x] Educator-management interface has been restyled.
- [x] Latest recorded full test suite passes: **39 passed**.
- [x] Non-debug Waitress runtime was verified locally.
- [x] A second device accessed the login page over the same home Wi-Fi.
- [x] SQLite database location and a backup were confirmed; both passed
      `PRAGMA integrity_check`.
- [ ] Network portability and access limitations are verified or documented
      as described in Section 10.1.
- [x] Database backup restoration was tested in a separate test location
      as described in Section 10.2.
- [x] User-experience and maintainability checklist items in Section 10.3
      are completed or explicitly deferred where they depend on future pages.

Sprint 3 is ready for closure when the remaining network portability
action and outside-project backup prerequisite are resolved, and the
user-experience and maintainability items are completed or explicitly
deferred. This checklist is not a formal security audit or a claim of
production readiness.

## 12. Rerunning checks

From the project root with the virtual environment activated:

``` powershell
python -m pytest -q
```

To check whether the current PowerShell session has a secret key
configured without revealing its value:

``` powershell
python -c "import os; print('SECRET_KEY configured:', bool(os.environ.get('SECRET_KEY')))"
```

Do not print or paste the actual key.

The previously used local-development command was:

``` powershell
python -m flask --app app:create_app run --debug
```

**Do not use the debug command for shared or production deployment.**
Deployment requires a separate configuration step.

## 13. Sprint outcome

Sprint 3 established the authentication and authorization foundation for
EduAnalytics, including password hashing, CSRF protection, role checks,
account-status handling, secret-key validation, logout, and administrator
workflows for educator account management.

The latest recorded full test suite passed **39 tests**. Local non-debug
Waitress operation and access from a second device on the same home Wi-Fi
were verified. Database backup restoration and application initialization
against a disposable database copy succeeded. An additional backup was
created outside the project directory and passed SQLite integrity checks.
Network portability verification remains outstanding, and backup access
permissions must be verified before storing real institutional data.

This is a development milestone, not a declaration that the application
has undergone a formal security audit or is production-ready.
