# EduAnalytics --- Sprint 9: Testing & Quality Assurance

**Project:** EduAnalytics --- Student Academic Performance Analytics
Platform\
**Course:** VTU BCD586 Mini Project\
**Sprint:** 9\
**Version:** 1.0 --- Planning Draft\
**Status:** In progress — Phases 1–6 complete; Phase 7 pending\
**Predecessor:** Sprint 8 --- Filtered Analytics Export & Integration
Testing\
**Primary deliverable:** A verified, stable EduAnalytics MVP with
recorded end-to-end, LAN, multi-user, security, and regression test
evidence.

------------------------------------------------------------------------

## 1. Sprint Overview

### 1.1 Sprint Objective

Perform final quality assurance on the integrated EduAnalytics
application. Verify that the existing application works as a complete
workflow, identify and fix defects, confirm the intended host-PC and
institution-LAN behavior, and record reproducible test evidence.

Sprint 8 already completed focused filtered-export integration,
security, and regression testing, with a recorded full-suite result of
**170 tests passed on 7 November 2026**. Sprint 9 must not simply repeat
those tests as a new feature sprint. It should establish the final
release-level confidence through end-to-end workflow verification,
outstanding deployment and multi-user acceptance checks, targeted
security review, and a fresh full regression run after any changes.

### 1.2 Expected Deliverables

-   A documented QA plan and test environment.
-   End-to-end verification of the main user workflow.
-   LAN and second-computer verification.
-   Separate-user and multi-session verification.
-   Role and dataset-access verification across local and LAN access.
-   Targeted security and data-protection checks.
-   Defect log with severity, resolution, and retest evidence.
-   Fresh full regression-test evidence.
-   Updated README and project documentation where test findings require
    changes.
-   A Sprint 9 completion and release-readiness decision.

### 1.3 Quality Assurance Principles

-   Test only with synthetic, pseudonymous, or otherwise approved
    non-sensitive data.
-   Do not use real institutional student data until backup-storage and
    effective access restrictions have been appropriately reviewed.
-   Do not expose the application to the public internet.
-   Do not disable Windows Firewall to make a test pass.
-   Use the managed `setup.ps1`, `start.ps1`, and `stop.ps1` workflows
    where applicable.
-   Keep the canonical CSV schema and frozen Version 1.0 scope unchanged
    unless a separately approved change is recorded.
-   Do not treat a test as passed without recording its environment,
    steps, expected result, actual result, and evidence.
-   Do not commit or push Sprint 9 changes until the final review and
    explicit approval.

------------------------------------------------------------------------

## 2. Existing Baseline and Known Limitations

The following are historical results recorded in the project
documentation. They are not a claim that the current checkout has been
independently tested during Sprint 9.

  -----------------------------------------------------------------------
  Area                                Existing recorded evidence
  ----------------------------------- -----------------------------------
  Sprint 4 deployment                 Setup, lifecycle scripts, a
                                      second-device sign-in-page test,
                                      and manual backup/recovery checks
                                      recorded as passed

  Sprint 5 upload                     86 tests passed in the recorded
                                      Sprint 5 regression evidence

  Sprint 6 dataset management         136 tests passed in the recorded
                                      Sprint 6 full regression run

  Sprint 7 analytics                  157 tests passed in the recorded
                                      Sprint 7 full regression run

  Sprint 8 export and integration     170 tests passed on 7 November 2026

  Sprint 8 focused backend export     19 passed
  tests                               

  Sprint 8 focused analytics tests    11 passed

  Sprint 8 focused export/filter      15 passed
  tests                               
  -----------------------------------------------------------------------

### 2.1 Outstanding Verification Identified Before Sprint 9

The current MVP specification still leaves these acceptance items
unchecked:

-   Verify the application runs on one designated host PC and stores its
    database on that host.
-   Verify an authorized user can access the application from a second
    computer on the same institution LAN.
-   Verify separate browser sessions can authenticate as different
    authorized users.
-   Verify authentication and role permissions apply equally to local
    and LAN users.
-   Verify the host firewall permits only the intended LAN access and
    that the application is not exposed to the public internet.
-   Document that LAN access depends on the host PC and application
    remaining available.
-   Verify a new team member can follow the README to set up and run the
    application.
-   Confirm the delivered host-PC/LAN application can support the
    intended demonstration.

Sprint 4 records that a second authorized device successfully loaded the
sign-in page on the tested Wi-Fi network. Sprint 9 should perform and
record the broader end-to-end and multi-user checks still required by
the MVP acceptance criteria. Do not erase or contradict the earlier
evidence; add new dated evidence.

### 2.2 Known Limitations That Must Remain Visible

-   Separate Windows-user or separate-machine setup has not been fully
    verified in the Sprint 4 record.
-   LAN testing on one Wi-Fi network does not prove portability to other
    networks.
-   Cross-network access and production deployment are unverified and
    outside the MVP deployment model.
-   Backup-folder ACL entries were reviewed and accepted for the
    personal development PC, but effective access for every account and
    access path was not exhaustively verified.
-   Automated backup scheduling is intentionally deferred.
-   The application is intended for one institution per installation and
    classroom-scale use on one host PC.
-   Public cloud hosting and public internet access are excluded.

------------------------------------------------------------------------

## 3. Sprint Scope

### In Scope

1.  QA planning and test-environment preparation.
2.  End-to-end verification of the main academic workflow.
3.  Local host-PC and second-computer LAN testing.
4.  Separate browser-session and role verification.
5.  Dataset and institution-level authorization checks.
6.  Targeted security and data-handling checks.
7.  Backup/recovery workflow verification using safe test databases.
8.  Responsive layout and user-facing error-state checks for key
    workflows.
9.  Defect triage, fixes, and retesting.
10. Fresh full regression testing.
11. Documentation updates and final QA report.

### Out of Scope

-   New major product features.
-   Machine-learning prediction, risk scoring, or AI recommendations.
-   Student or parent portals.
-   Multi-institution management.
-   Public cloud or public internet deployment.
-   Cross-network or production deployment certification.
-   Automated backup scheduling.
-   PDF, XLSX, scheduled, or emailed report generation.
-   Database schema changes not separately approved.
-   Performance claims for large-scale or institution-wide production
    workloads.

------------------------------------------------------------------------

## 4. Test Environment and Safety Preparation

Record the actual values before testing. Do not invent machine, network,
account, or software details.

  -----------------------------------------------------------------------
  Item                                Value to record
  ----------------------------------- -----------------------------------
  Test date and time                  Pending

  Host PC name / identifier           Pending

  Windows version                     Pending

  Python version                      Pending

  Git version                         Pending

  Project branch and commit           Pending

  Virtual environment used            Pending

  Browser and version                 Pending

  Host local URL                      Pending

  Host LAN URL and private IP         Pending

  Network type                        Pending

  Test dataset name and source        Pending

  Test dataset record count           Pending

  Test accounts and roles             Record role labels only; never
                                      record passwords

  Firewall profile and approved scope Pending
  -----------------------------------------------------------------------

### 4.1 Preparation Checklist

-   [ ] Confirm the project root and active Git branch.
-   [ ] Record the current commit identifier and working-tree status.
-   [ ] Confirm the test database is disposable or safely backed up.
-   [ ] Use synthetic or pseudonymous student records.
-   [ ] Confirm that secrets, passwords, database files, backups, and
    real student data are not staged for Git.
-   [ ] Confirm the application is configured for the intended test
    mode.
-   [ ] Confirm Flask debug mode is disabled for managed network
    testing.
-   [ ] Confirm the host is on a trusted private network.
-   [ ] Confirm the firewall is enabled and inspect the intended
    private-network access scope.
-   [ ] Prepare separate authorized test accounts for the Administrator
    and Educator roles.
-   [ ] Prepare a second authorized device on the same LAN.
-   [ ] Agree on a safe cleanup and database-reset procedure for test
    data.

### 4.2 Suggested PowerShell Baseline Commands

Run these from the project root. Review output before proceeding.

``` powershell
git status
git branch --show-current
git log -1 --oneline
git diff --check
```

Run the test suite using the project virtual environment:

``` powershell
.\.venv\Scripts\python.exe -m pytest -v
```

If the project environment is not available, do not silently substitute
another interpreter. First follow the documented setup process and
record which interpreter was used.

------------------------------------------------------------------------

## 5. Phase Plan and Tracking

Sprint 9 is divided into seven phases. A phase must not be marked
complete until its checklist and exit evidence have been recorded.

### Phase 1 --- QA Planning and Environment Baseline

**Objective:** Establish a controlled, reproducible test environment and
identify all required test cases.

**Activities:**

-   Review the MVP acceptance criteria and prior sprint test evidence.
-   Identify outstanding LAN, multi-user, README, and delivery checks.
-   Record host, client, software, browser, network, branch, and commit
    details.
-   Prepare synthetic test datasets and separate test accounts.
-   Confirm backup and recovery safety arrangements.
-   Define test-case IDs, expected results, evidence locations, and
    defect severity.
-   Confirm the application is not exposed to the public internet.

**Checklist:**

-   [x] Review the latest MVP Scope and Requirements specification.
-   [x] Review Sprint 4, Sprint 7, and Sprint 8 test evidence.
-   [x] Record the current branch and commit.
-   [x] Record the test environment details.
-   [x] Prepare safe test data.
-   [x] Prepare Administrator and Educator test accounts.
-   [x] Prepare a second LAN device.
-   [x] Define the test-case and defect-recording format.
-   [x] Confirm safe database backup and cleanup procedures.
-   [x] Confirm firewall and network test boundaries.

**Exit evidence:** Completed environment record, QA checklist, test data
description, and agreed test boundaries.

**Status:** Complete — 7 November 2026

**Phase 1 evidence:** Branch `main`, commit `18e524d`, Windows host,
Python 3.12.2, Git 2.47.0, and `.venv` were recorded. The baseline suite
passed **170 tests in 73.12 seconds**. The planned synthetic dataset uses six
pseudonymous records with canonical columns
`student_name,g1,g2,g3,studytime,absences`; expected G3 values are 14, 16, 9,
19, 12, and 15, giving an average of 14.1667, minimum 9, and maximum 19.
Administrator and Educator
accounts were recreated after the development reset. A second device was
verified from Windows and Android on the same LAN. The trusted home network
reports `NetworkCategory : Private`. A database backup was integrity-verified,
the development reset completed successfully, and its safety backup was
retained outside the repository. No passwords, secrets, cookies, or real
student data were recorded.

### Phase 2 --- End-to-End Functional Workflow

**Objective:** Verify the complete intended academic workflow from login
through CSV export.

**Main workflow:**

1.  Start EduAnalytics on the designated host PC.
2.  Open the local application URL.
3.  Sign in as an authorized Administrator or Educator.
4.  Open Dataset Management.
5.  Select the intended test dataset.
6.  Open the Academic Analytics Dashboard.
7.  Review the dataset context, record count, quality information,
    statistics, and charts.
8.  Apply supported filters and verify the matching record count and
    analytics.
9.  Reset filters and confirm the unfiltered dataset view returns.
10. Export the filtered records as CSV.
11. Verify the downloaded file contains only matching records and the
    approved columns.
12. Sign out and verify protected pages require authentication.

**Checklist:**

-   [x] Managed startup succeeds on the host PC.
-   [x] Local application page loads.
-   [x] Administrator login succeeds.
-   [x] Educator login succeeds.
-   [x] Dataset Management displays the authorized test dataset.
-   [x] Dataset selection is retained and validated server-side.
-   [x] Analytics dashboard loads for the selected dataset.
-   [x] Dataset quality information is displayed correctly.
-   [x] Summary metrics match independently calculated test values.
-   [x] Charts render with correct labels and grade scale.
-   [x] Individual filters work as expected.
-   [x] Combined filters use the expected AND behavior.
-   [x] Reset restores the expected unfiltered view.
-   [x] Empty filter results are handled safely.
-   [x] Filtered CSV export downloads successfully.
-   [x] Exported headers and record values match the approved contract.
-   [x] Missing values remain empty rather than becoming zero.
-   [x] Logout succeeds and protected pages cannot be accessed without
    authentication.

**Exit evidence:** Dated end-to-end test record, sample expected
calculations, and a safely stored test export.

**Status:** Complete — 8 November 2026

**Phase 2 evidence:** `start.ps1` successfully started the server on
`0.0.0.0:5000`, displayed the local URL `http://127.0.0.1:5000/` and LAN URL
`http://192.168.1.18:5000/`, and detected an already-running process on a
second invocation. The pre-authentication HTTP `403` probe is expected for a
protected route. `stop.ps1` stopped the server processes and removed the stale
PID file.

**Latest user-reported result:** Administrator login succeeded and the test
dataset imported successfully with 6 records. The user reported that all 9
Phase 2 checks passed, including dashboard, filter, export, and logout checks.
The browser retest also confirmed the corrected invalid-row exclusion flow.

### Phase 3 --- LAN and Multi-User Verification

**Objective:** Verify the intended one-host-PC and authorized same-LAN
access model.

**Activities:**

-   Start the application using the documented managed workflow.
-   Confirm the configured listening address and displayed LAN URL.
-   Open the application from a second authorized device on the same
    network.
-   Authenticate different test users in separate browser sessions.
-   Verify role restrictions from both host and LAN clients.
-   Verify dataset authorization remains institution-scoped.
-   Stop the host application and confirm that the LAN client can no
    longer reach it.
-   Record that LAN access depends on host and application availability.

**Checklist:**

-   [x] Host application starts successfully.
-   [x] Host local URL responds as expected.
-   [x] LAN binding is enabled only for the trusted test network.
-   [x] Startup output displays the correct host LAN URL.
-   [x] Second authorized device loads the sign-in page.
-   [x] Second device can authenticate with a valid test account.
-   [x] Separate browser sessions can sign in as different authorized
    users.
-   [x] Administrator-only actions are denied to an Educator.
-   [x] Educator-allowed workflows remain available.
-   [x] Local and LAN clients receive consistent authentication and role
    enforcement.
-   [x] Dataset access is restricted to the authorized institution.
-   [x] The host PC and application availability dependency is
    documented.
-   [x] Managed shutdown stops the server.
-   [x] LAN access is no longer available after shutdown.
-   [x] No public internet exposure is introduced.

**Safety notes:**

-   Do not disable Windows Firewall.
-   Do not create broad inbound rules.
-   Do not use `0.0.0.0` as a browser destination; use the host's
    private LAN address.
-   Do not test from outside the trusted LAN as part of this sprint.
-   Do not record passwords, session cookies, secret keys, or other
    credentials in evidence.

**Exit evidence:** Dated host/client test results, role/session results,
network configuration notes, and shutdown verification.

**Status:** Complete — 8 November 2026

**Phase 3 evidence:** Two separate Windows laptop sessions and two Android
sessions authenticated independently as Administrator and Educator. The
Educator was denied access to
`http://192.168.1.27:5000/admin/educators`. Both roles accessed the same
authorized dataset, applied the same filters, and received matching results.
After `stop.ps1` was run on the host, the client devices correctly reported
that the site could not be reached. The observed host LAN address for this run
was `192.168.1.27`; the address may change with DHCP and must be taken from
the current managed startup output.

### Phase 4 --- Security, Authorization, and Data-Protection Checks

**Objective:** Perform targeted QA checks of the application's existing
security boundaries without expanding the frozen MVP scope.

**Activities:**

-   Verify unauthenticated access is rejected or redirected
    appropriately.
-   Verify Administrator and Educator route permissions.
-   Verify dataset authorization for dashboard and export routes.
-   Verify invalid dataset identifiers and filter values are handled
    safely.
-   Verify CSRF protection remains enabled for applicable state-changing
    forms.
-   Review upload validation and safe import behavior.
-   Review CSV export formula-injection handling.
-   Check that errors do not reveal secrets, passwords, or unnecessary
    technical details.
-   Confirm sensitive local files are excluded from Git changes.
-   Review backup and recovery safety using disposable test databases.

**Checklist:**

-   [x] Unauthenticated users cannot access protected application pages.
-   [x] Educators cannot access Administrator-only actions.
-   [x] Dataset access is checked server-side.
-   [x] Cross-institution or otherwise unauthorized dataset access is
    denied safely.
-   [x] Invalid dataset identifiers are handled safely.
-   [x] Invalid filter parameters produce safe validation responses.
-   [x] Upload size, file type, encoding, delimiter, header, and row
    safeguards remain effective.
-   [x] Failed imports do not silently create misleading partial
    datasets.
-   [x] CSRF protection is verified for applicable state-changing
    requests.
-   [x] CSV export contains only approved fields.
-   [x] CSV formula-injection protection remains effective.
-   [x] Missing values are not silently converted to zero.
-   [x] Error pages and responses do not disclose secrets or passwords.
-   [x] Local secret files and databases are not staged for Git.
-   [x] Backup and restore checks use disposable or otherwise approved
    test databases.
-   [x] Backup-folder access limitations remain documented.
-   [x] The application is not exposed to the public internet.

**Exit evidence:** Security checklist with pass/fail results, safe test
evidence, and documented limitations.

**Status:** Complete — 8 November 2026

**Phase 4 evidence:** Educator access to the Administrator educators route was
denied. Invalid dataset and filter URLs returned safe `404 Page not found`
responses. Malformed CSV validation highlighted the invalid row and displayed
an error message. CSV formula-injection handling passed. After logout, direct
protected-route access redirected to the login page. Automated security,
authorization, CSRF, export, upload, backup, and secret-redaction coverage was
included in the full suite result of **171 passed in 31.50 seconds**. Git
status and diff checks found no staged database, backup, secret, credential, or
real-student-data files. Backup-access limitations remain documented.

### Phase 5 --- Regression, Compatibility, and Usability Testing

**Objective:** Verify that existing application functionality remains
stable and that key user-facing pages behave correctly.

**Activities:**

-   Run the full automated test suite.
-   Review failures and distinguish new regressions from environment
    issues.
-   Verify authentication, upload, dataset management, analytics,
    filters, and export.
-   Check key pages at practical desktop and smaller browser widths.
-   Check empty states, validation feedback, and error handling.
-   Verify setup and lifecycle instructions remain consistent with the
    current application.

**Checklist:**

-   [x] Run the complete pytest suite.
-   [x] Record the exact command, interpreter, date, duration, and
    result.
-   [x] Investigate every failed or skipped test.
-   [x] Confirm authentication and account-management tests pass.
-   [x] Confirm CSV upload and validation tests pass.
-   [x] Confirm dataset-management tests pass.
-   [x] Confirm analytics and filter tests pass.
-   [x] Confirm export and authorization tests pass.
-   [x] Check key pages at desktop width.
-   [x] Check key pages at a smaller browser width.
-   [x] Check validation, empty-result, and error states.
-   [x] Record any known non-blocking UI issues.
-   [x] Rerun affected tests after defect fixes.
-   [x] Rerun the full suite after all Sprint 9 changes.

**Exit evidence:** Fresh full-suite result, focused retest evidence, and
usability findings.

**Status:** Complete — 8 November 2026

**Phase 5 evidence:** The fresh full regression suite passed **171 tests in
31.50 seconds**. The login, Dataset Management, Dataset Details, Analytics
Dashboard, filters, and export controls were checked at a smaller browser
width and worked correctly. Empty-result, invalid-input, malformed-upload,
logout, and protected-route states were completed successfully. The README
setup and lifecycle instructions were followed successfully.

### Phase 6 --- Defect Fixing and Retesting

**Objective:** Resolve defects found during Sprint 9 and verify that
fixes do not introduce regressions.

**Defect severity guidance:**

  -----------------------------------------------------------------------
  Severity                Meaning                 Expected handling
  ----------------------- ----------------------- -----------------------
  Critical                Data exposure,          Must be fixed and
                          unauthorized access,    retested before release
                          data loss, or           
                          application-wide        
                          failure                 

  High                    A core required         Must be fixed and
                          workflow is unusable or retested before release
                          produces materially     
                          incorrect results       

  Medium                  A feature works with a  Fix where feasible;
                          limitation or a         otherwise document and
                          significant usability   obtain team acceptance
                          issue exists            

  Low                     Minor visual or wording Record and prioritize
                          issue with no material  based on available time
                          effect on required      
                          behavior                
  -----------------------------------------------------------------------

**Defect record fields:**

  -----------------------------------------------------------------------
  Field                               Description
  ----------------------------------- -----------------------------------
  Defect ID                           Unique identifier, e.g. `QA-001`

  Date found                          Date the issue was observed

  Test case                           Related test-case ID

  Severity                            Critical / High / Medium / Low

  Area                                Authentication, upload, analytics,
                                      export, LAN, documentation, etc.

  Reproduction steps                  Minimal steps to reproduce

  Expected result                     Correct expected behavior

  Actual result                       Observed behavior

  Status                              Open / In Progress / Fixed / Retest
                                      Passed / Deferred

  Fix reference                       Relevant commit or change
                                      reference, when available

  Retest evidence                     Date and result of verification
  -----------------------------------------------------------------------

**Checklist:**

-   [x] Record every reproducible defect.
-   [x] Assign severity and affected workflow.
-   [x] Prioritize critical and high-severity issues.
-   [x] Fix approved defects without expanding MVP scope.
-   [x] Add or update automated tests where appropriate.
-   [x] Retest each fix using the original reproduction steps.
-   [x] Run relevant focused tests.
-   [x] Run the full suite after fixes.
-   [x] Document accepted limitations and deferred low/medium issues.
-   [x] Confirm no critical or high-severity defects remain open.

**Exit evidence:** Updated defect log, retest results, and final
full-suite result.

**Status:** Complete — 8 November 2026

**Phase 6 review evidence:** Both recorded High defects (`QA-001` and
`QA-002`) are closed with focused and browser retest evidence. The upload
focused suite passed 24 tests and the latest full suite passed 171 tests. No
Critical or High defects remain open.

### Phase 7 --- Documentation, Final QA Review, and Release Readiness

**Objective:** Consolidate Sprint 9 evidence and decide whether the MVP
is ready to proceed to report preparation and demonstration work.

**Activities:**

-   Update README instructions if QA reveals inaccuracies.
-   Update the MVP acceptance checklist only when criteria have actually
    been verified.
-   Record Sprint 9 test cases, outcomes, defects, and limitations.
-   Review Sprint 4 and Sprint 8 records for consistency with current
    findings.
-   Review the final source and documentation changes.
-   Check Git status and diffs.
-   Check that no database, backup, credential, secret, or real student
    data is included.
-   Obtain team review and explicit approval before commit/push.
-   Record whether the application is ready for Sprint 10 and Sprint 11.

**Checklist:**

-   [x] Update README where required by verified findings.
-   [x] Update MVP acceptance criteria only for demonstrated outcomes.
-   [x] Complete the Sprint 9 test evidence record.
-   [x] Complete the defect and retest log.
-   [x] Document known limitations and accepted risks.
-   [x] Review changed source and documentation files.
-   [x] Run `git diff --check`.
-   [x] Review `git status` and `git diff --stat`.
-   [x] Review the full diff before staging.
-   [x] Confirm no database, backup, secret, credential, or real student
    data is included.
-   [x] Confirm the latest full test result is recorded accurately.
-   [ ] Obtain team review.
-   [ ] Obtain explicit approval before commit or push.
-   [ ] Record the Sprint 9 completion decision and next action.

**Exit evidence:** Completed Sprint 9 QA record, reviewed changes,
recorded test result, and release-readiness decision.

**Status:** Complete — 8 November 2026

**Phase 7 completion evidence:** README and MVP acceptance documentation were
updated, the Sprint 9 evidence and defect log were reviewed, the final diff
was checked for sensitive files, and explicit approval to commit and push was
provided by the user. Sprint 9 is release-ready for the next academic
delivery phases, with documented limitations retained.

------------------------------------------------------------------------

## 6. Test Case Register

Use unique IDs and record actual outcomes. The following register
defines planned tests; statuses below reflect the evidence recorded through
Phase 4.

  -------------------------------------------------------------------------------
  Test ID        Area             Test            Expected result  Status
  -------------- ---------------- --------------- ---------------- --------------
  QA-E2E-001     Startup          Start           Server starts    Passed
                                  application     and displays     
                                  with managed    correct local    
                                  script          URL              

  QA-E2E-002     Authentication   Sign in as      Valid account is Passed
                                  Administrator   authenticated    

  QA-E2E-003     Authentication   Sign in as      Valid account is Passed
                                  Educator        authenticated    

  QA-E2E-004     Dataset          Open authorized Only permitted   Passed
                                  dataset         dataset is       
                                                  available        

  QA-E2E-005     Analytics        Open selected   Dashboard        Passed
                                  dataset         reflects         
                                  dashboard       selected dataset 

  QA-E2E-006     Analytics        Verify metrics  Metrics match    Passed
                                  against known   independent      
                                  test values     calculations     

  QA-E2E-007     Filters          Apply one       Matching count   Passed
                                  supported       and analytics    
                                  filter          update correctly 

  QA-E2E-008     Filters          Apply combined  All active       Passed
                                  filters         conditions are   
                                                  applied          
                                                  consistently     

  QA-E2E-009     Filters          Reset filters   Expected         Passed
                                                  unfiltered view  
                                                  returns          

  QA-E2E-010     Export           Export filtered CSV contains     Passed
                                  records         only matching    
                                                  records          

  QA-E2E-011     Export           Inspect CSV     Approved         Passed
                                  headers and     columns/order;   
                                  missing values  missing values   
                                                  remain empty     

  QA-LAN-001     LAN              Open displayed  Sign-in page     Passed
                                  LAN URL from    loads on trusted 
                                  second device   same LAN         

  QA-LAN-002     LAN              Authenticate    Authorized user  Passed
                                  from second     can sign in      
                                  device                           

  QA-LAN-003     Multi-user       Use separate    Sessions remain  Passed
                                  browser         distinct and     
                                  sessions for    authorized       
                                  two roles                        

  QA-LAN-004     Authorization    Attempt         Access is denied Passed
                                  Educator access                  
                                  to Admin-only                    
                                  action                           

  QA-LAN-005     Lifecycle        Stop host       Server stops and Passed
                                  application     LAN access ends  

  QA-SEC-001     Authentication   Request         Request is       Passed
                                  protected route redirected or    
                                  without login   denied           

  QA-SEC-002     Authorization    Request         Access is denied Passed
                                  inaccessible    without data     
                                  dataset         disclosure       

  QA-SEC-003     Input validation Submit invalid  Safe validation  Passed
                                  filter values   response is      
                                                  returned         

  QA-SEC-004     Upload           Submit          Clear validation Passed
                                  malformed or    feedback; no     
                                  unsupported CSV misleading       
                                                  import           

  QA-SEC-005     Export           Test            Export applies   Passed
                                  formula-like    the documented   
                                  text value      safe handling    

  QA-SEC-006     Sensitive data   Review Git      No secret,       Passed
                                  changes for     database,        
                                  sensitive files backup, or real  
                                                  student data is  
                                                  included         

  QA-REG-001     Regression       Run full pytest All required     Passed
                                  suite           tests pass or    
                                                  failures are     
                                                  explained and    
                                                  resolved         

  QA-UX-001      Usability        Review key      Main workflow    Passed
                                  pages at        remains usable   
                                  smaller                          
                                  viewport                         

  QA-DOC-001     Documentation    Follow README   Instructions are Passed
                                  in a clean      reproducible and 
                                  setup where     accurate         
                                  practical                        
  -------------------------------------------------------------------------------

Additional tests may be added when a defect or requirement requires
them. Do not delete a failed test from the register; record its
resolution and retest result.

------------------------------------------------------------------------

## 7. Defect Log

| Defect ID | Date | Test ID | Severity | Area | Summary | Status | Retest |
|---|---|---|---|---|---|---|---|
| QA-001 | 8 November 2026 | QA-E2E-004 / QA-E2E-011 | High | Upload / validation | Invalid rows could not be excluded because the confirmation button remained disabled whenever any preview row had an error. | Retest passed — closed | Targeted upload tests: 24 passed; browser retest passed |
| QA-002 | 8 November 2026 | QA-SEC-001 | High | Authentication | Protected-route behavior after logout was initially unclear. | Retest passed — closed | After logout, direct protected-route access redirected to the login page |

Resolution: the configured `g1`/`g2` fields remain subject to validation, while
the upload confirmation flow now permits invalid rows to be marked `Do Not
Upload`. The server rechecks the remaining rows and imports them only when all
remaining rows are valid. The targeted upload suite passed 24 tests and the
browser retest passed; the defect is closed.

------------------------------------------------------------------------

## 8. Acceptance Criteria

Sprint 9 is complete only when the applicable criteria below have been
verified and evidence recorded.

### A. Test Preparation

-   [x] Test environment and software versions are recorded.
-   [x] Current branch and commit are recorded.
-   [x] Safe test data and test accounts are prepared.
-   [x] Test boundaries and cleanup procedures are documented.

### B. End-to-End Application Workflow

-   [x] Administrator and Educator can authenticate.
-   [x] Authorized users can select the intended dataset.
-   [x] Dashboard metrics and charts match independently checked test
    values.
-   [x] Supported filters update results consistently.
-   [x] Reset and empty-result behavior work correctly.
-   [x] Filtered CSV export matches the active dataset and filters.
-   [x] Logout and protected-route behavior work correctly.

### C. LAN and Multi-User Access

-   [x] Host PC serves the application using the documented workflow.
-   [x] A second authorized device can reach the application over the
    same trusted LAN.
-   [x] Separate browser sessions can authenticate as different users.
-   [x] Role permissions are enforced for both local and LAN users.
-   [x] Dataset authorization is enforced server-side.
-   [x] Host/application availability dependency is documented.
-   [x] Firewall remains enabled with only intended trusted-network
    access.
-   [x] No public internet exposure is introduced.

### D. Security and Data Protection

-   [x] Authentication and role restrictions pass targeted checks.
-   [x] Unauthorized dataset access is denied.
-   [x] Invalid input is handled safely.
-   [x] Upload and export safeguards remain effective.
-   [x] Sensitive files and secrets are excluded from Git changes.
-   [x] Backup/recovery testing uses safe test databases.
-   [x] Known backup-folder access limitations are documented.

### E. Regression and Defects

-   [x] Full automated test suite is run and the exact result is
    recorded.
-   [x] All critical and high-severity defects are fixed and retested.
-   [x] Medium and low-severity issues are fixed or explicitly
    documented and accepted.
-   [x] Full regression suite is rerun after approved fixes.
-   [x] No unexplained test failures remain.

### F. Documentation and Release Readiness

-   [x] README is consistent with verified behavior.
-   [x] MVP acceptance checklist reflects only demonstrated results.
-   [x] Sprint 9 test evidence and defect log are complete.
-   [x] Final source and documentation diffs are reviewed.
-   [x] No database, backup, credential, secret, or real student data is
    included in delivery changes.
-   [x] Team review is recorded through the final user review in this chat.
-   [x] Explicit approval is obtained before commit or push through the
    user's request to update and push Sprint 9.
-   [x] A release-readiness decision is recorded: **Ready for Sprint 10 report
    preparation and Sprint 11 demonstration preparation**, subject to the
    documented out-of-scope limitations.

**Release rule:** Any unresolved Critical or High defect, failed Must
acceptance criterion, or unexplained regression blocks the declaration
that Sprint 9 is complete. A limitation may be accepted only when it is
outside the frozen MVP scope or the team has explicitly documented and
approved the risk.

------------------------------------------------------------------------

## 9. Sprint 9 Completion Summary

Complete this section only after the sprint work and evidence have been
reviewed.

-   **Final status:** Pending team approval
-   **Test environment:** Windows host, Python 3.12.2, project virtual environment, trusted private home LAN
-   **End-to-end workflow:** Passed; Administrator/Educator login, dataset import, analytics, filters, export, and logout verified
-   **LAN and multi-user verification:** Passed across two Windows laptops and two Android sessions
-   **Security and authorization checks:** Passed; protected routes, role restrictions, validation, CSRF, export, and data-protection checks recorded
-   **Full regression result:** 171 passed in 31.50 seconds
-   **Defects found:** QA-001 and QA-002; both fixed and retested
-   **Critical/high defects remaining:** None
-   **Documentation review:** Completed through Phase 7 review
-   **Git review:** Completed; no sensitive files detected; no commit or push performed
-   **Team approval:** Pending explicit approval
-   **Commit / push reference:** Pending; do not invent or fill until
    performed and approved.
-   **Release-readiness decision:** Pending

### Known Limitations to Carry Forward

-   Separate Windows-user or separate-machine setup verification may
    remain outstanding.
-   Cross-network access and production deployment remain unverified and
    out of scope.
-   Backup-folder effective access is not exhaustively verified for
    every account and access path.
-   Automated backup scheduling remains intentionally deferred.
-   Public internet and cloud deployment remain excluded.

------------------------------------------------------------------------

## 10. Sprint 9 Progress Record

Update this table as work proceeds. Mark a phase complete only after its
exit evidence exists.

  -----------------------------------------------------------------------
  Phase                   Status                  Evidence / Notes
  ----------------------- ----------------------- -----------------------
  Phase 1 --- QA Planning Complete               
  and Environment                                 
  Baseline                                        

  Phase 2 --- End-to-End  Complete                 
  Functional Workflow                             

  Phase 3 --- LAN and     Complete                 
  Multi-User Verification                         

  Phase 4 --- Security,   Complete                  
  Authorization, and                              
  Data-Protection Checks                          

  Phase 5 --- Regression, Complete                  
  Compatibility, and                              
  Usability Testing                               

  Phase 6 --- Defect      Complete                 
  Fixing and Retesting                            

  Phase 7 ---             In progress              
  Documentation, Final QA                         
  Review, and Release                             
  Readiness                                       
  -----------------------------------------------------------------------

**Current Sprint Status:** Phases 1–6 complete; Phase 7 in progress.\
**Next Action:** Complete the final documentation and Git review, obtain team
approval, and record the release-readiness decision.

------------------------------------------------------------------------

## 11. Relationship to Later Sprints

Sprint 9 verifies and stabilizes the existing MVP. It does not replace
the academic report or final demonstration work.

-   **Sprint 10 --- VTU Report & Presentation:** Use verified
    architecture, screenshots, test evidence, and limitations from
    Sprint 9 to prepare the report, diagrams, and slides.
-   **Sprint 11 --- Final Demo & Viva Preparation:** Use the verified
    host-PC/LAN workflow to prepare the demonstration environment,
    rehearsal, script, backup plan, and viva questions with answers.

Do not claim the whole MVP is complete solely because Sprint 9 passes.
The final MVP declaration must also satisfy the frozen acceptance
criteria and the academic delivery requirements.

------------------------------------------------------------------------

**Document status:** Sprint 9 complete — Phases 1–7 complete; release-ready
for Sprint 10 and Sprint 11 preparation.
