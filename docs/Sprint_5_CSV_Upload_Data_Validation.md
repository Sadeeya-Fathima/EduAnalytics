# Sprint 5 - CSV Upload & Data Validation

**Project:** EduAnalytics  
**Sprint focus:** Core data workflow  
**Sprint objective:** Enable authenticated educators and administrators to upload a student dataset, preview its contents, validate the data, and safely import valid student records into SQLite.

**Status:** Complete - upload, validation, server-side preview storage, transactional import, exclusion, field semantics, size limiting, rollback verification, import-token protection, regression tests, live database verification, manual end-to-end verification, and responsive UI review completed

**Closed:** 30 October 2026

Sprint 5 is formally closed. Follow-up work belongs to the next sprint and must not change the completed upload, validation, and import acceptance scope without a new requirement.

## 1. Sprint objective

Sprint 5 connects the existing authentication and database foundation to the core EduAnalytics data workflow. Authorized users will be able to upload a canonical CSV file, review a preview, understand validation errors, and import the dataset safely.

The sprint is limited to CSV ingestion and validation. Analytics dashboards, predictive models, arbitrary column mapping, and cross-dataset comparisons remain outside this sprint.

## 2. Proposed deliverables

- Dynamic CSV upload interface for Administrators and Educators.
- Guided three-step upload workflow.
- Dataset-details form completed before file selection.
- Downloadable dataset-specific CSV template.
- Combined configured-state workflow card with progress indicators and contextual actions.
- Backend CSV upload endpoint with header and row validation.
- Validation result and full preview display for uploaded records.
- Row-level validation feedback in the preview table, including a Remarks column and highlighted invalid cells.
- Per-row success/error remarks and `Do not Upload` exclusion checkboxes, including a select-all control.
- File-type, file-size, encoding, and readability checks.
- Preview of uploaded rows before import.
- Validation against the canonical schema:

  ```text
  student_name,g1,g2,g3,studytime,absences
  ```

- Required-field checks.
- Numeric validation for grades and optional numeric fields.
- Grade-range validation using the dataset grade scale.
- Non-negative whole-number validation for `absences`.
- Clear row-level validation errors.
- Explicit handling of valid and invalid rows before import.
- Transactional database imports with rollback on failure.
- Protection against accidental duplicate submissions.
- Automated tests for successful imports and important failure cases.

## 3. Existing project dependencies

The following project components already support this sprint:

- `app/models.py` contains `Dataset`, `StudentRecord`, and `UploadError`.
- `app/auth/decorators.py` provides role-based authorization.
- Flask-Login protects authenticated routes.
- Flask-WTF provides CSRF protection.
- SQLite foreign-key enforcement is enabled in `app/extensions.py`.
- The `tests/` directory contains the existing regression-test structure.

## 4. Dynamic CSV contract

The database keeps stable internal fields:

```text
student_name,g1,g2,g3,studytime,absences
```

The visible CSV headers are generated from the dataset metadata. Teachers may configure the display labels for G1, G2, and G3, while EduAnalytics maps those headers to the stable internal fields.

| Column | Required | Validation |
|---|---:|---|
| Student Name | Yes | Non-empty student display name or pseudonymous label. |
| G1 label | No | Teacher-defined header mapped to `g1`; numeric when supplied. |
| G2 label | No | Teacher-defined header mapped to `g2`; numeric when supplied. |
| G3 label | Yes | Teacher-defined header mapped to `g3`; numeric and within the grade scale. |
| Study Time | No | Non-negative number representing average or typical hours per week for the subject. |
| Absences | No | Non-negative whole number representing days absent from the relevant subject or class during the reporting period. |

Blank optional values must be stored as `NULL`/`None`, not as zero. Missing data must remain distinguishable from a measured value of zero.

The dataset metadata must record the applicable grade-scale maximum. The initial UCI Student Performance workflow uses a 0-20 grade scale.

G1 and G2 remain nullable database fields when their labels are empty and their CSV columns are omitted. G3 and Student Name are always required. Grade labels must be unique and must not collide with `Student Name`, `Study Time`, or `Absences`.

## 5. Supported dataset sources

EduAnalytics will support two dataset sources through the same canonical template:

1. **UCI-based research data** converted from the original UCI source format.
2. **Institutional data** prepared by teachers or administrators using the canonical EduAnalytics CSV template.

The application will not automatically map arbitrary institutional spreadsheets. Institutional users must convert their source files to the approved template before upload. This keeps validation, testing, and analytics consistent while allowing the system to work with real school data.

## 6. UCI dataset handling

The UCI source files use semicolon-separated fields and must be converted before upload.

- Convert the source file to the canonical comma-separated format.
- Map `G1`, `G2`, and `G3` to `g1`, `g2`, and `g3`.
- Generate pseudonymous labels such as `Student 001`.
- Preserve the 0-20 grade scale.
- Map `absences` where available.
- Do not interpret UCI categorical `studytime` codes as actual hours. Leave canonical `studytime` blank unless a separately approved conversion is introduced. UCI data is treated as standard institutional-format data after conversion; the application does not auto-detect UCI files.
- Reject the original semicolon-delimited file with a clear delimiter or header message if it is uploaded directly.

## 7. Guided three-step workflow

### Step 1 - Enter dataset details and grade labels

The Administrator or Educator opens **Upload Dataset** and completes the dataset-details form before selecting a file.

The form includes:

- Dataset name.
- Academic year.
- Class, semester, or section when applicable.
- Subject or examination when applicable.
- Grade-scale maximum.
- Optional G1 label.
- Optional G2 label.
- Required G3 label.

The application records the uploader and upload timestamp automatically. These values must not be taken from user-editable form fields.

### Step 2 - Generate headers and download the CSV template

The upload page should provide a clear **Download CSV Template** button. The template must contain the generated headers in the same order shown in the preview. For example:

```csv
Student Name,Internal 1,Internal 2,Final Exam,Study Time,Absences
```

The project may provide an optional example row in the template or a separate sample CSV. The example must be clearly identified as illustrative and must not be imported accidentally as real institutional data.

The user fills in the template using Excel or another spreadsheet application, preserves the headers, and saves the completed file as CSV.

### Step 3 - Upload, validate, and confirm

The user selects the completed CSV. EduAnalytics then:

1. Checks the file and generated headers.
2. Parses and validates the rows.
3. Displays a preview and clear row-level errors.
4. Shows the user whether the file is ready for import.
5. Imports the data only after explicit confirmation.

Invalid files must not be partially imported. The initial implementation should block confirmation when validation errors exist and require the user to correct and upload the file again.

The final import operation must revalidate the uploaded data. The application must not trust a client-provided preview result or dataset identifier.

### Current configured-state interface

After the metadata form is submitted successfully:

- The metadata form is hidden.
- The generated preview is shown in a single workflow section.
- A progress indicator shows `Upload -> Verified -> Complete`.
- The available actions are shown in the workflow toolbar:
  - Edit dataset details.
  - Download CSV template.
  - Upload file.
  - Confirm, disabled until validation succeeds and enabled for a valid preview.
- The preview table remains the main content of the configured state.
- Repeated structure headings and a separate upload panel are not displayed.
- `Student Name *`, G3, and any configured G1/G2 labels receive red required markers in the preview and required markers in the downloaded template headers. If G1 or G2 is not configured, its column is omitted. `Study Time` and `Absences` remain unmarked and do not display optional text.
- Generated columns are rebuilt from the current session metadata on each page load, preventing stale browser-session headers from reappearing.
- The preview table preserves complete headers with horizontal scrolling when the available viewport is narrow.
- Authenticated application pages use the shared `dashboard.css` navigation styling, with Educator Management visible to Administrators.

The upload file action selects the CSV for the next validation stage. The Import / Confirm action must remain unavailable until backend validation has completed successfully.

```text
Enter dataset details
    -> download canonical CSV template
    -> complete CSV outside EduAnalytics
    -> select completed CSV
    -> validate and preview
    -> confirm import
    -> create Dataset and StudentRecords in one transaction
    -> commit completely or roll back everything
```

## 8. Proposed routes and modules

Suggested routes:

```text
GET  /datasets
GET  /datasets/upload
POST /datasets/upload
GET  /datasets/template
POST /datasets/upload/csv
GET  /datasets/upload/preview
POST /datasets/upload/confirm
```

`POST /datasets/upload/csv` receives the selected file, validates the generated headers and supported values, and renders validation results with a preview of the uploaded records. A validated preview can be explicitly confirmed through the same protected endpoint; confirmation creates the dataset and selected student records in one transaction.

Invalid uploaded values are preserved in the preview, highlighted in red, and explained in the same row under `Remarks`. File-level errors, such as mismatched headers or unreadable encoding, are displayed in the validation panel when no row-level table can be produced.

Valid rows display `Ready to import` in green. Invalid rows display their validation messages in red. The `Do Not Upload` column is the first column of the uploaded-data preview and uses red emphasis. It is not included in the static example preview. The `Remarks` column is also shown only for uploaded data. Users can select individual rows or all rows with `Do Not Upload`; selected row numbers are submitted with the future confirmation/import action and will be excluded from persistence.

When validation fails, the Upload file action changes to a red `Retry` action. Retry clears the previous validation result before the user selects another CSV. The validated preview remains available after refresh until confirmation, retry, edit, or logout so the user can explicitly confirm the import. Uploaded files themselves are not persisted in the page session. Preview rows are held in temporary server-side storage; the browser session stores only a small preview/import token, avoiding oversized session cookies. Row-level errors are shown only in the table's `Remarks` column to avoid duplicate messages. The static example table is hidden while an uploaded-data preview is displayed.

Logout clears the temporary dataset metadata and validation preview from the session. The upload page also sends no-cache headers so stale POST responses are not reused by the browser. After successful confirmation, a dedicated `Import complete` state shows the dataset name, source filename, imported record count, and actions to import another dataset or return to the dashboard; the metadata form is not shown in that state.

The Upload file action opens the native picker. After the user clicks `Open`, the file input calls the form's `requestSubmit()` method, which submits the file to the validation endpoint and renders the validated rows without requiring a second validation click.

Suggested package structure:

```text
app/
└── datasets/
    ├── __init__.py
    ├── routes.py
    ├── forms.py
    ├── validation.py
    └── services.py
```

Responsibilities:

- `routes.py`: authentication, authorization, upload workflow, and responses.
- `forms.py`: upload and dataset metadata forms.
- `validation.py`: CSV parsing, schema checks, and row-level validation.
- `services.py`: transactional creation of the dataset and student records.

The existing `Dataset` model stores the metadata required for this workflow. Description is intentionally excluded until the model supports it.

## 9. Authorization and security

- Only authenticated Administrators and Educators may access upload and import operations.
- Anonymous users must be redirected to login.
- Unsupported roles must receive HTTP 403.
- CSRF protection must apply to preview and import actions.
- Enforce a maximum upload size of 5 MiB per CSV file.
- Accept only supported CSV uploads.
- Do not expose raw parser, filesystem, or database errors to users.
- Do not store uploaded files permanently unless this is explicitly required later.

## 10. Duplicate-submission protection

The workflow should use a server-side upload/import token or equivalent mechanism.

- Generate a token for the preview/import attempt.
- Require the token for final confirmation.
- Invalidate it after successful import.
- Prevent browser refresh or double-click actions from importing the same dataset twice.
- Revalidate the data during final import.

## 11. Transaction and database behavior

The import must create the `Dataset` and its `StudentRecord` rows in one transaction.

```python
try:
    create_dataset()
    create_student_records()
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

If any record fails to import, the dataset and all student records from that attempt must be rolled back. `record_count` should reflect the number of successfully committed records.

`StudentRecord.student` remains the primary key as decided for this project. Each dataset supplies distinct student-key values; the field name and model design are not changed as part of Sprint 5.

## 12. Row-level error format

Each validation error should identify:

- CSV row number.
- Column name, when applicable.
- Received value, when safe to display.
- Clear explanation of the problem.

Example:

```text
Row 7, column `absences`: expected a non-negative whole number; received `-2`.
```

## 13. Recommended implementation order

| Phase | Task | Priority |
|---|---|---|
| 1 | Review models, authentication, and role permissions | First |
| 2 | Define upload workflow and canonical schema | High |
| 3 | Implement file checks, parsing, preview, and validation | High |
| 4 | Implement transactional import and duplicate-submission protection | High |
| 5 | Add row-level error reporting and user feedback | High |
| 6 | Add automated tests and complete workflow verification | High |

## 14. Acceptance criteria

Sprint 5 is complete when:

- Authorized Administrators and Educators can upload supported CSV files.
- Users can enter dataset details before selecting a file.
- Users can download the canonical CSV template.
- Users can preview the uploaded data before importing it.
- Missing columns, invalid values, out-of-range grades, malformed files, and invalid absence values are handled clearly.
- Users can identify invalid rows and understand why they failed validation.
- Valid records are stored correctly in SQLite.
- A failed import produces no partial database writes.
- Duplicate confirmation does not create duplicate records.
- Unauthorized users cannot access upload or import operations.
- Automated tests cover successful imports and important failure cases.

## 15. Test plan

Add tests covering at least:

- Authenticated Educator access.
- Authenticated Administrator access.
- Anonymous access rejection.
- Unsupported-role rejection.
- Valid CSV preview.
- Dataset-details submission and automatic uploader/timestamp recording.
- Canonical template download and header verification.
- Successful import and correct record values.
- Missing required headers.
- Incorrect header names or order.
- Missing `student_name` or `g3`.
- Invalid numeric values.
- Grades outside the configured range.
- Negative or decimal absences.
- Empty files.
- Malformed CSV files.
- Invalid encoding.
- Oversized files.
- Semicolon-delimited UCI source files.
- Database rollback after a simulated import failure.
- Duplicate confirmation protection.
- Confirmation imports only non-excluded rows and clears the temporary workflow after success.
- Each validated preview receives a one-time server-side import token. Confirmation requires the token and successful import clears it with the preview, preventing replayed confirmations.
- CSV parsing rejects malformed quoting, invalid UTF-8, semicolon-delimited UCI source files, fields over 255 characters, and files over 10,000 student rows. The application enforces a 5 MiB request limit.
- Files exceeding 5 MiB receive a user-facing upload-page error explaining the limit instead of an unhandled server error.
- Study Time accepts non-negative hours per week; Absences accepts non-negative whole absence days. Blank optional values remain `NULL`.
- Every upload is treated as standard institutional-format data; UCI files must be converted before upload and are not auto-detected.

### Current automated coverage

`tests/test_dataset_upload.py` now verifies the pre-import workflow for both authorized roles and failure paths, including:

- Dynamic G1/G2 label inclusion and omission, required header markers, and template header order.
- Missing G3, invalid grade scales, duplicate grade labels, and reserved-label validation.
- Mixed valid and invalid rows, preservation of uploaded values, invalid-cell highlighting, row-level `Remarks`, and the `Do Not Upload` select-all control.
- Empty files, unsupported file extensions, header mismatches, retry/reset behavior, refresh clearing, and the guarantee that preview-only uploads do not create database records.

The upload suite passes `22 tests`, including all-row exclusion, zero-valid-row blocking, and confirmation-token replay protection. The complete regression run passed when grouped: upload (`20 passed` before the final two behavior tests), restore (`10 passed`), and the remaining application/authentication/authorization/database/setup/backup tests (`56 passed`) for `86 passed` total; the final upload behavior additions also pass. The live database was manually verified after importing `UCI Student Performance`: one `Dataset` row has `import_status = complete` and `record_count = 395`, and `student_records` contains 395 rows for that dataset. Manual import behavior was verified for successful import, partial exclusion, all-row exclusion, zero valid rows, and token replay. Final responsive UI review covered desktop, mobile portrait, and mobile landscape layouts.

## 16. Scope boundaries

This sprint does not include:

- Analytics dashboards.
- Plotly charts.
- Predictive models.
- Arbitrary column mapping.
- Arbitrary spreadsheet support or uncontrolled column mapping. Mapping is limited to teacher-defined labels generated from the metadata form.
- PDF reports.
- Advanced cross-dataset comparisons.
- Scheduled imports or reports.

## 17. Sprint risks and decisions

### Risks

- Accidentally importing partial data.
- Treating blank optional values as zero.
- Treating UCI `studytime` category codes as hours.
- Trusting preview data without revalidation.
- Duplicate submissions caused by browser retries or double-clicks.
- Loading unnecessarily large files into memory.

### Decisions

- The canonical schema is fixed for the first implementation.
- Visible CSV headers are dynamic, while internal database fields remain stable.
- The metadata and generated column mapping are stored temporarily in the Flask session until the upload workflow is completed.
- Both UCI-based and institutional datasets are supported through the same canonical template.
- Institutional source files must be converted to the canonical template before upload.
- Invalid rows block the initial all-or-nothing import workflow.
- `StudentRecord.student` remains the primary key and field name.
- Each dataset is analyzed independently.
- UCI semicolon-delimited source files must be converted before upload.

