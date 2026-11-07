# Sprint 8 --- Filtered Analytics Export & Integration Testing

**Project:** EduAnalytics — Student Academic Performance Analytics Platform
**Sprint:** 8
**Version:** 1.2
**Status:** Phase 7 complete — final approval required
**Predecessor:** Sprint 7 — Academic Analytics
**Primary deliverable:** Secure filtered CSV export integrated with the
Academic Analytics Dashboard, supported by integration, security, and
regression testing.

------------------------------------------------------------------------

## 1. Sprint Overview

Sprint 7 introduced the Academic Analytics Dashboard with interactive
filters. Sprint 8 extends this functionality by allowing authorized
Admins and Educators to download student records matching the filters
applied to a selected dataset. It also verifies integration with
authentication, authorization, dataset management, and existing
analytics workflows.

### 1.1 Sprint Objective

Implement a secure CSV export feature for filtered academic records and
verify through integration, security, and regression testing that
exported data matches dashboard filters and existing application
functionality remains unaffected.

### 1.2 Expected Deliverables

-   Filtered CSV export functionality.
-   Export action integrated into the Academic Analytics Dashboard.
-   Reuse of existing server-side filtering and validation logic.
-   Dataset-level authorization for export requests.
-   Defined CSV columns, ordering, encoding, and download response
    headers.
-   Safe handling of missing values and spreadsheet formula injection.
-   Integration, security, and regression test evidence.
-   Updated project documentation.

## 2. Why Sprint 8 Is Needed

The dashboard allows users to explore student performance through
descriptive statistics, visualizations, and interactive filters.
However, viewing filtered results inside the application does not
provide a downloadable dataset for further analysis.

Users may need to:

- Work with filtered academic records in spreadsheet applications.
- Perform additional analysis outside the platform.
- Prepare academic summaries using selected student records.
- Retain a copy of matching records for permitted institutional use.
- Work with a subset of a larger dataset instead of exporting every record.

Integration testing is equally important because export creates another
way to access dataset records. It must follow the same filtering,
authentication, authorization, and dataset-isolation rules as the
dashboard.

Testing must confirm that:

- Exported records match the dashboard's active filters.
- Users cannot export records from unauthorized datasets.
- Existing authentication and dataset-management workflows continue to work.
- Changes introduced during Sprint 8 do not break previous functionality.
- CSV downloads have the expected format, encoding, and response headers.

## 3. Scope of Work

Sprint 8 is divided into seven development phases.

### Phase 1 --- Code Review and Architecture Analysis

**Objective:** Understand the existing Sprint 7 implementation before
introducing export functionality.

**Activities:**

-   Review the Academic Analytics Dashboard and analytics routes.
-   Inspect dataset retrieval and existing server-side filtering logic.
-   Understand how filters are received and validated.
-   Examine authentication and dataset-authorization checks.
-   Identify exportable student-record fields and reusable services or
    queries.
-   Review existing automated tests and project conventions.
-   Confirm how dataset identifiers are passed through authorized routes
    and how access is verified.

**Checklist:**

- [x] Review analytics routes and controllers.
- [x] Review existing filter validation.
- [x] Understand dataset-level authorization.
- [x] Identify reusable filtering logic.
- [x] Identify exportable student-record fields.
- [x] Review existing testing conventions.
- [x] Confirm dataset identifier handling and authorization flow.
- [x] Document the proposed implementation approach.

**Expected outcome:** A clear technical understanding of the existing
application and an approved approach for implementing filtered CSV
export.

### Phase 1 Completion Record --- 2026-11-07

Phase 1 code review and architecture analysis are complete. The current
implementation and test suite provide the following decisions for the
remaining Sprint 8 work:

| Review area | Finding | Sprint 8 decision |
|---|---|---|
| Analytics routes | `GET /analytics/<dataset_id>` is the canonical filtered dashboard route; filters are read from `request.args`. | Add `GET /analytics/<dataset_id>/export` and pass the same query parameters through unchanged. |
| Dataset authorization | `accessible_dataset_or_404()` scopes datasets to the signed-in user's institution and returns 404 for inaccessible datasets. | Call this helper inside the export route; do not trust `active_dataset_id` or client-side state as authorization. |
| Authentication and roles | Analytics routes use `@role_required("admin", "educator")`. | Apply the same decorator to export so unauthenticated users are redirected and other roles are denied consistently. |
| Record retrieval | `prepare_analysis_input()` calls `retrieve_dataset_records()`, which filters by `dataset_id` and preserves stable `student` order. | Reuse this request-scoped retrieval path; export only the approved six fields. |
| Filter validation | `apply_filters()` validates grade, study-time, and absence filters and raises `ValueError` for invalid input. | Reuse it directly so dashboard and export cannot diverge. Convert validation errors to HTTP 400 as the dashboard does. |
| Canonical export fields | The analysis frame contains `student_name`, `g1`, `g2`, `g3`, `studytime`, and `absences`, plus internal `student`. | Export exactly `student_name,g1,g2,g3,studytime,absences`; never export `student` or account/application fields. |
| Missing values | Analytics normalizes invalid/missing numeric values to `NaN`; pandas rows retain missing values. | Serialize missing values as empty CSV fields, never zero. |
| Existing conventions | Dataset template export uses Python's `csv.writer`, UTF-8 bytes, and Flask `send_file`. | Use the same standard-library CSV approach with explicit UTF-8 and `\n` line endings. |
| Regression baseline | The full current suite passed: 157 tests. | Preserve existing routes and add focused backend, integration, authorization, and CSV-safety tests before declaring Sprint 8 complete. |

#### Approved Phase 1 implementation approach

1. Add a small CSV serialization helper in `app.analytics.services` (or a
   dedicated analytics export module) that accepts the already-filtered
   frame and returns UTF-8 CSV bytes. Keep the schema and order as a constant.
2. Add the export route beside the dashboard routes. It will independently
   load the authorized dataset, prepare records, apply `request.args`, and
   return a downloadable attachment.
3. Sanitize the dataset name for the filename, use a documented local-time
   timestamp format, and protect untrusted text beginning with `=`, `+`, `-`,
   or `@` by prefixing an apostrophe before CSV serialization.
4. Add the dashboard action using the current query string so every active
   filter is preserved. Empty results remain a valid CSV containing only the
   header, with a clear dashboard state already provided by the existing UI.
5. Verify the route with focused tests for exact rows, exact column order,
   missing values, quoting, formula injection, headers, invalid filters,
   unauthenticated access, cross-institution access, and regression behavior.

#### Sprint 8 execution plan

| Phase | Deliverable | Exit evidence |
|---|---|---|
| 2 | Final export contract and filename/encoding decisions | This document's schema, headers, timestamp, and empty-result behavior are accepted. |
| 3 | Secure backend export endpoint and serializer | Focused backend/security tests pass. |
| 4 | Dashboard Export CSV action | Browser-level route/query-state integration test passes. |
| 5 | Filter/export consistency coverage | No-filter, individual, combined, reset, missing, empty, quoting, and formula cases pass. |
| 6 | Authorization and regression verification | Full suite plus isolation and invalid-input tests pass. |
| 7 | Documentation and final review | README/MVP updates, known limitations, diff review, and test evidence are recorded; Git push remains approval-gated. |

**Phase 1 checklist:** All items in the Phase 1 checklist above are
complete. Phase 2 is ready to begin.

### Phase 2 --- Export Workflow and Technical Design

**Objective:** Define how users request and download filtered CSV files.

**Activities:**

- Decide where the Export CSV action appears on the analytics dashboard.
- Define the export endpoint and HTTP method.
- Determine how active filter parameters are passed to the endpoint.
- Define CSV headers and exact field order.
- Define record retrieval, filename, and download-response behavior.
- Specify empty-result and missing-value handling.
- Define CSV encoding, newline handling, and spreadsheet formula-injection protection.
- Ensure the design reuses existing filter and authorization rules.

**Proposed CSV schema and column order:**

``` csv
student_name,g1,g2,g3,studytime,absences
```

These fields must appear in exactly this order. Internal database
identifiers, account information, and unrelated application fields must
not be included unless separately reviewed and explicitly approved.

**HTTP method decision:** Use `GET` for the read-only filtered export.
The existing dashboard already represents filters as URL parameters, so
the export action can preserve the same filter state without introducing
a second request model. Dataset authorization and filter validation remain
server-side requirements.

**Proposed filename format:**

``` text
analytics_<dataset-name>_<dataset-id>_<timestamp>.csv
```

Sanitize the dataset name by replacing any character outside letters,
numbers, dots, underscores, and hyphens with an underscore. Use the
dataset's numeric ID to prevent filename collisions. Use the timestamp
format `YYYYMMDD_HHMMSS` in Asia/Calcutta local time, documented as IST.

**Phase 2 design decisions:**

- Add an `Export CSV` action beside the dashboard filter actions.
- Use `GET /analytics/<dataset_id>/export`.
- Pass the dashboard's active query parameters unchanged to the export route.
- Authorize the route with the existing admin/educator role decorator and
  `accessible_dataset_or_404()` helper.
- Export exactly `student_name,g1,g2,g3,studytime,absences` in that order.
- Use UTF-8 encoding, `\n` line endings, and Python's CSV quoting rules.
- Represent missing values as empty fields.
- Return a header-only CSV when no records match; do not return unfiltered data.
- Prefix text values beginning with `=`, `+`, `-`, or `@` with an apostrophe.
- Return `Content-Type: text/csv; charset=utf-8` and an attachment
  `Content-Disposition` header.

**Checklist:**

- [x] Define the dashboard export action.
- [x] Design the export endpoint.
- [x] Confirm the HTTP method.
- [x] Define filter-parameter handling.
- [x] Define CSV headers and exact column order.
- [x] Confirm excluded internal and account fields.
- [x] Define filename conventions and sanitization.
- [x] Define CSV encoding and newline behavior.
- [x] Define empty-result behavior.
- [x] Define missing-value handling.
- [x] Define formula-injection protection.
- [x] Define response content type and attachment headers.
- [x] Review and approve the export design.

**Expected outcome:** An approved export workflow and technical design
before implementation begins.

**Phase 2 status:** Complete. The export contract is approved for backend
implementation in Phase 3.

### Phase 3 --- Backend CSV Export Implementation

**Objective:** Implement secure server-side CSV generation.

**Activities:**

-   Create the CSV export route using the approved HTTP method.
-   Require an authenticated and authorized user.
-   Obtain the dataset identifier through the authorized route and
    independently verify access.
-   Do not treat client-side session state as proof of dataset
    authorization.
- Validate incoming filter parameters on the server.
- Reuse existing server-side filtering logic.
-   Retrieve only records matching the selected dataset and active
    filters.
-   Generate CSV using the approved headers and field order.
-   Preserve missing values as empty CSV fields; never convert them to
    zero.
-   Exclude internal identifiers and unrelated application data.
-   Protect exported text values against spreadsheet formula injection.
-   Return the generated file as a downloadable response.
-   Handle empty results safely.
-   Apply CSRF protection if the endpoint uses `POST`.

**Checklist:**

- [x] Implement the export endpoint.
- [x] Enforce authentication.
- [x] Enforce dataset-level authorization.
- [x] Validate the dataset identifier.
- [x] Validate incoming filter parameters.
- [x] Reuse existing filtering logic.
- [x] Generate approved CSV headers and rows.
- [x] Preserve missing values as empty fields.
- [x] Exclude unapproved internal fields.
- [x] Implement formula-injection-safe output.
- [x] Implement approved encoding and newline behavior.
- [x] Return the correct downloadable response.
- [x] CSRF is not applicable because the approved endpoint uses `GET`.
- [x] Handle empty matching results.
- [x] Add backend tests.

**Expected outcome:** The backend securely generates and returns CSV
files containing only authorized, matching student records.

**Phase 3 status:** Complete. The backend route, serializer, validation,
authorization path, CSV safety behavior, and focused tests are implemented.

### Phase 4 --- Dashboard Integration

**Objective:** Connect backend export functionality to the existing
Academic Analytics Dashboard.

**Activities:**

-   Add an Export CSV action to the dashboard.
-   Pass the current dataset identifier and active filter values to the
    export endpoint.
-   Ensure the export request uses the same filter values as the
    dashboard.
-   Preserve the selected dataset context.
-   Ensure the server independently authorizes the dataset identifier
    received through the route.
-   Provide appropriate feedback when no matching records are available.
-   Verify browser download behavior and responsive layout.

**Checklist:**

- [x] Add the Export CSV action.
- [x] Connect the action to the backend endpoint.
- [x] Pass active filter values correctly.
- [x] Preserve selected dataset context.
- [x] Verify server-side dataset authorization.
- [x] Verify browser download behavior.
- [x] Handle empty results appropriately.
- [x] Verify responsive dashboard layout.
- [x] Test the complete dashboard-to-export workflow.

**Expected outcome:** Authorized users can initiate CSV downloads
directly from the analytics dashboard.

**Phase 4 status:** Complete. The dashboard now renders an Export CSV
action that preserves the selected dataset and active query-string filters.

### Phase 5 --- Export and Filter Integration Testing

**Objective:** Verify that the exported CSV contains exactly the records
represented by the dashboard's active filters.

**Activities:**

-   Test export with no active filters, individual filters, and combined
    filters.
-   Verify grade-range, study-time, and absence filters where
    applicable.
-   Test filter-reset behavior.
-   Verify missing-value and empty-result handling.
-   Compare exported records with dashboard filtered results.
-   Verify encoding, quoting, delimiters, and newline handling.
-   Verify response content type and attachment filename.
-   Test large filtered result sets.
-   Test text values that could be interpreted as spreadsheet formulas.

**Checklist:**

- [x] Test export without active filters.
- [x] Test individual filters.
- [x] Test combined filters.
- [x] Test grade-range filtering.
- [x] Test study-time filtering.
- [x] Test absence filtering.
- [x] Test filter reset.
- [x] Test missing values.
- [x] Test empty results.
- [x] Verify exported records match dashboard filtering.
- [x] Verify CSV encoding.
- [x] Verify CSV quoting and newline handling.
- [x] Verify `Content-Type`.
- [x] Verify `Content-Disposition: attachment`.
- [x] Verify filename and filename sanitization.
- [x] Test large filtered result sets.
- [x] Test formula-injection-safe output.

**Expected outcome:** Exported records consistently follow dashboard
filtering rules, and the downloaded file has the expected CSV format and
response behavior.

**Phase 5 status:** Complete. Focused export/filter and large-result coverage
pass; security and regression verification continue in Phase 6.

### Phase 6 --- Security, Authorization and Regression Testing

**Objective:** Verify that CSV export follows existing application
security rules and does not break previously implemented functionality.

**Activities:**

-   Test authenticated and unauthenticated export requests.
-   Verify Admin and Educator permissions.
-   Attempt access to unauthorized datasets.
- Verify institution-level dataset isolation.
- Test invalid dataset identifiers and filter parameters.
-   Verify that export requests do not rely only on client-side session
    state.
-   Verify that responses do not expose unauthorized records.
-   Verify CSRF enforcement if the endpoint uses `POST`.
-   Run the complete existing regression test suite.
-   Investigate and resolve regressions introduced by Sprint 8.

**Checklist:**

- [x] Test authenticated export requests.
- [x] Test unauthenticated requests.
- [x] Test Admin permissions.
- [x] Test Educator permissions.
- [x] Test unauthorized dataset access.
- [x] Test dataset isolation.
- [x] Test invalid dataset identifiers.
- [x] Test invalid filter parameters.
- [x] Verify route-supplied dataset authorization.
- [x] Verify exported data access restrictions.
- [x] CSRF is not applicable because the approved endpoint uses `GET`.
- [x] Run existing regression tests.
- [x] Resolve Sprint 8 regressions.
- [x] Record final test results.

**Expected outcome:** Export respects the application's existing
security model, and previous application features continue to work.

**Phase 6 status:** Complete. Security, authorization, dataset-isolation,
invalid-input, and regression tests pass. The full suite result is 170 passed.

### Phase 7 --- Documentation and Final Review

**Objective:** Document Sprint 8 implementation and prepare the
completed sprint for review.

**Activities:**

- Update the README with completed export functionality.
- Update the MVP Scope and Requirements document.
- Record implementation details in the Sprint 8 progress document.
- Record automated, integration, security, and regression test results.
- Document known limitations.
- Review changed files and implementation quality.
- Confirm no unrelated features or files were introduced.
- Perform final Git readiness checks.
- Obtain approval before the Sprint 8 Git push.

**Checklist:**

- [x] Update README.
- [x] Update MVP documentation.
- [x] Complete Sprint 8 progress documentation.
- [x] Record automated test results.
- [x] Record integration test results.
- [x] Record security and regression test results.
- [x] Document known limitations.
- [x] Review modified files.
- [x] Check for accidental database or sensitive-file inclusion.
- [x] Complete final review.
- [ ] Obtain approval before Git push.

**Expected outcome:** Sprint 8 is documented, tested, and ready for
final review and delivery.

### Phase 7 known limitations

- The export endpoint supports CSV only; XLSX, PDF, scheduled, and emailed
  reports remain out of scope.
- LAN access and production deployment limitations documented by Sprint 4
  remain unchanged.
- GitHub push is intentionally approval-gated and has not been performed.

------------------------------------------------------------------------

## 4. User Workflow

### Step 1 --- Login

The Admin or Educator logs into EduAnalytics using their authorized
account.

### Step 2 --- Select a Dataset

The user opens Dataset Management and selects an authorized dataset.

The export request must identify the dataset through the authorized
application route. The server must independently verify that the
authenticated user can access the supplied dataset identifier.
Client-side session state alone must never be treated as proof of
authorization.

### Step 3 --- Open Academic Analytics

The user opens the selected dataset's Academic Analytics Dashboard.

### Step 4 --- Apply Filters

The user applies the required filters, such as:

- G3 minimum and maximum grades.
- G1 and G2 grade ranges, when available.
- Study-time category or verified numerical range, where supported.
- Absence categories.

### Step 5 --- Review Filtered Results

The dashboard updates its matching record count, statistics, and
visualizations according to the active filters.

### Step 6 --- Export CSV

The user selects Export CSV. The application sends the selected dataset
identifier and active filter parameters to the server using the approved
export endpoint.

### Step 7 --- Server Validation and CSV Generation

The server: 1. Checks authentication. 2. Verifies authorization for the
dataset identifier supplied through the route. 3. Validates filter
parameters. 4. Applies the existing server-side filtering logic. 5.
Retrieves matching records from the authorized dataset. 6. Generates the
CSV using approved columns and order. 7. Applies safe CSV output
handling. 8. Returns the file as a downloadable attachment.

### Step 8 --- Download

The browser receives the generated CSV as a downloadable file. The
exported records must match the dashboard's active filters.

### Step 9 --- Handle Empty Results

If no records match the selected filters, the application provides
appropriate feedback. It must not silently return unfiltered or
unrelated records.

------------------------------------------------------------------------

## 5. CSV Export Specification

The following requirements define the proposed CSV output. Confirm them
against the canonical dataset schema and Sprint 7 filtering behavior
during Phases 1 and 2.

### 5.1 Approved Columns and Order

The proposed CSV header is:

``` csv
student_name,g1,g2,g3,studytime,absences
```

The fields must appear in exactly this order:

-   `student_name`: Student name.
-   `g1`: First-period grade.
-   `g2`: Second-period grade.
-   `g3`: Final grade.
-   `studytime`: Existing canonical study-time value.
-   `absences`: Existing canonical absence value.

Do not reinterpret categorical study-time values as exact weekly hours.

### 5.2 Missing Values

-   Represent missing values as empty CSV fields.
-   Never convert missing values to zero.
-   Keep handling consistent with existing dataset and analytics
    behavior.

### 5.3 Excluded Fields

Do not export the following unless separately reviewed and approved:

-   Internal database identifiers.
-   User account information.
-   Passwords, tokens, or session information.
-   Internal application metadata.
-   Fields unrelated to the approved student-record schema.

### 5.4 Filename

Proposed filename:

``` text
analytics_<dataset-name>_<dataset-id>_<timestamp>.csv
```

Implementation requirements:

- Sanitize the dataset name before including it in the filename.
- Prevent path separators and unsafe filename characters.
- Define and document the timestamp format and timezone.
- Return the filename through the download response header.

### 5.5 Encoding and CSV Format

-   Use UTF-8 encoding.
-   Use consistent CSV newline handling.
-   Correctly quote fields containing commas, quotation marks, or line
    breaks.
-   Escape quotation marks according to CSV formatting rules.
-   Verify that the downloaded file opens correctly in a spreadsheet
    application.

### 5.6 Spreadsheet Formula Injection

Student names and other text fields are untrusted data. Test values
beginning with `=`, `+`, `-`, or `@`.

Prefix untrusted text values beginning with `=`, `+`, `-`, or `@` with a
single apostrophe before writing them to the CSV. This preserves the visible
value while preventing common spreadsheet applications from interpreting it
as a formula. CSV quoting alone must not be assumed to prevent formula
injection.

Document the chosen strategy and its behavior.

### 5.7 HTTP Response

Verify that the download response includes:

- An appropriate CSV `Content-Type`, such as `text/csv; charset=utf-8`.
- A `Content-Disposition` header identifying the response as an attachment
  and providing the sanitized filename.

------------------------------------------------------------------------

## 6. Out of Scope

The following features are excluded from Sprint 8.

### 6.1 Reporting

-   PDF report generation.
-   Scheduled report generation.
-   Automated email reports.
-   Advanced report templates.

### 6.2 Analytics

-   Machine-learning predictions.
-   Student risk scoring.
-   Predictive recommendations.
-   New analytics unrelated to CSV export.
-   Cross-dataset analytics.

### 6.3 Application Expansion

-   Student portal.
-   Parent portal.
-   Multi-institution support.
-   Public cloud deployment.
-   Mobile application development.

### 6.4 Export Expansion

-   Excel XLSX export.
-   PDF export.
-   Scheduled downloads.
-   Automated external integrations.

These features may be considered separately if MVP requirements are
revised and approved.

------------------------------------------------------------------------

## 7. Sprint 8 Acceptance Criteria

Sprint 8 is complete only when the applicable criteria below have been
implemented and verified.

### 7.1 Functional Acceptance

- [x] Authorized Admins and Educators can export CSV files.
- [x] Export action is available from the Academic Analytics
    Dashboard.
- [x] Selected dataset context is preserved.
- [x] Exported records match active dashboard filters.
- [x] Multiple filters work together correctly.
- [x] CSV headers and values are correct and in approved order.
- [x] Missing values are represented as empty fields.
- [x] Internal identifiers and unapproved fields are excluded.
- [x] Empty matching results are handled gracefully.
- [x] Downloaded file opens correctly in a spreadsheet application.

### 7.2 Security Acceptance

- [x] Export requires authentication.
- [x] Dataset-level authorization is enforced server-side.
- [x] Unauthorized users cannot export restricted datasets.
- [x] Dataset isolation is maintained.
- [x] Dataset identifiers supplied through routes are independently
    authorized.
- [x] Client-side session state is not treated as proof of dataset
    authorization.
- [x] Invalid dataset identifiers are handled safely.
- [x] Invalid filter parameters are validated.
- [x] Export does not expose records outside the authorized dataset.
- [x] CSRF protection is not applicable because the endpoint uses `GET`.
- [x] Spreadsheet formula-injection-safe output is implemented and
    tested.

### 7.3 CSV and HTTP Response Acceptance

- [x] UTF-8 encoding is verified.
- [x] Newline handling is verified.
- [x] CSV quoting and escaping are verified.
- [x] `Content-Type` is correct.
- [x] `Content-Disposition: attachment` is present.
- [x] Filename format and sanitization are verified.
- [x] Large filtered result sets are tested.
- [x] Zero matching records are handled correctly.

### 7.4 Integration and Regression Acceptance

- [x] Dashboard export workflow works correctly.
- [x] Export uses the same filtering rules as the dashboard.
- [x] Individual and combined filters are tested.
- [x] Filter-reset behavior is verified.
- [x] Empty-result behavior is verified.
- [x] Existing dataset workflows remain functional.
- [x] Existing authentication workflows remain functional.
- [x] Existing analytics features remain functional.
- [x] Full regression test suite passes.

### 7.5 Documentation and Delivery Acceptance

- [x] README is updated.
- [x] MVP documentation is updated.
- [x] Sprint 8 progress document is completed.
- [x] Test results are recorded.
- [x] Known limitations are documented.
- [x] Final code review is completed.
- [x] Git changes are reviewed before pushing.
- [ ] Approval is obtained before the Sprint 8 Git push.

------------------------------------------------------------------------

## 8. Sprint 8 Development Sequence

  -----------------------------------------------------------------------
  Order                   Development activity    Completion deliverable
  ----------------------- ----------------------- -----------------------
  1                       Code review and         Existing implementation
                          architecture analysis   understood

  2                       Export workflow and     Approved implementation
                          technical design        design

  3                       Backend CSV export      Working secure export
                                                  endpoint

  4                       Dashboard integration   Export action available
                                                  in dashboard

  5                       Export and filter       Filter consistency
                          integration testing     verified

  6                       Security and regression Security and regression
                          testing                 evidence

  7                       Documentation and final Sprint ready for
                          review                  delivery
  -----------------------------------------------------------------------

### 8.1 Development Approach

Sprint 8 should follow a phase-by-phase implementation approach:

1.  Review the existing implementation before changing files.
2.  Document the proposed changes.
3.  Review and approve the design.
4.  Implement one phase at a time.
5.  Test each phase before moving forward.
6.  Run full regression testing after integration.
7.  Review documentation and Git changes before delivery.

Reuse the existing Sprint 7 filtering implementation wherever possible.
Avoid creating a separate filtering implementation for CSV export
because it could produce different results from the dashboard.

### 8.2 Implementation Guardrails

-   Do not begin implementation before Phase 1 review and Phase 2 design
    approval.
-   Do not change the canonical dataset schema without a separately
    approved requirement.
-   Do not bypass existing authentication or dataset authorization.
-   Do not trust client-side state as authorization evidence.
-   Do not convert missing values to zero.
-   Do not reinterpret categorical study-time values as hours.
-   Do not export unapproved internal fields.
-   Do not introduce unrelated features into Sprint 8.
-   Do not commit or push changes before final review and approval.

------------------------------------------------------------------------

## 9. Technical and Data Handling Considerations

The following existing project decisions must remain valid during Sprint
8:

-   The canonical student dataset schema remains unchanged unless a
    separately approved requirement justifies a change.
-   Export must use the selected dataset rather than combining multiple
    datasets.
-   Existing institution-level authorization must remain enforced.
-   Missing values must not automatically be converted to zero.
-   UCI study-time categorical codes must not be interpreted as exact
    weekly study hours.
-   Exported data must not include unrelated internal application or
    account information.
-   CSV must contain only the approved student-record fields.
-   Exported records must follow the same server-side filter semantics
    as the dashboard.
-   Export requests must independently verify access to the dataset
    identified by the authorized route.

No database schema changes are planned for this sprint.

------------------------------------------------------------------------

## 10. Sprint Completion Definition

Sprint 8 is complete when:

1.  Filtered CSV export is implemented.
2.  The export action is integrated into the Academic Analytics
    Dashboard.
3.  Exported records match the dashboard's active filters.
4.  CSV structure, encoding, filename, and download headers are
    verified.
5.  Missing values and formula-injection risks are handled.
6.  Authentication and dataset authorization are verified.
7.  Integration and regression testing are completed successfully.
8.  Project documentation is updated.
9.  Final review is approved.

**Final Sprint Deliverable:** A tested and documented Filtered Analytics
Export feature integrated into EduAnalytics without breaking existing
MVP functionality.

------------------------------------------------------------------------

## 11. Next Step

Phase 7 documentation and final review are complete. Sprint 8 is ready for
final approval; no Git push has been performed.

Completed Phase 7 evidence:

- README updated with the filtered CSV export workflow.
- MVP scope and requirements updated with completed export criteria.
- This progress document updated with phase status and test evidence.
- Full regression result recorded: 170 tests passed.
- Known limitations and delivery controls recorded below.
- Source, Git, and sensitive-file checks completed.

------------------------------------------------------------------------

## 12. Sprint Progress Record

Update this section as work proceeds. Do not mark a phase complete until
its activities and checklist items have been verified.

| Phase | Status | Evidence / Notes |
|---|---|---|
| Phase 1 — Code Review and Architecture Analysis | Complete | Architecture findings and implementation approach recorded above; baseline suite: 157 passed. |
| Phase 2 — Export Workflow and Technical Design | Complete | Export contract, endpoint, filename, encoding, empty-result, and safety decisions recorded above. |
| Phase 3 — Backend CSV Export Implementation | Complete | Export route and serializer implemented; focused backend export tests: 19 passed. |
| Phase 4 — Dashboard Integration | Complete | Export action rendered with the current dataset and active query-string filters; focused analytics tests: 11 passed. |
| Phase 5 — Export and Filter Integration Testing | Complete | Focused export/filter tests: 15 passed, including large-result coverage. |
| Phase 6 — Security, Authorization and Regression Testing | Complete | Security-focused analytics tests passed; full regression suite: 170 tests passed. |
| Phase 7 — Documentation and Final Review | Complete | Documentation, test evidence, source review, sensitive-file checks, and Git diff review completed. Approval is still required before Git push. |

**Current Sprint Status:** Phase 7 complete — final approval required.
**Next Action:** Obtain approval before pushing to GitHub.
