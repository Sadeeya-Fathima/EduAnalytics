# EduAnalytics — BCD586 Mini Project

## Final MVP Scope & Requirements Specification

**Version:** 1.0 — Frozen
**Project type:** VTU BCD586 Mini Project
**Team size:** 3 students
**Development timeline:** 8 weeks
**Status:** Approved baseline for implementation

---

## 1. Project Overview

### 1.1 Project Title

**EduAnalytics: Student Academic Performance Analytics Platform**

### 1.2 Problem Statement

Educational institutions collect student academic records, but manually examining spreadsheets makes it difficult to identify performance patterns, compare groups, and understand relationships between academic factors and final grades.

EduAnalytics will provide a web-based platform through which authorized institutional staff can upload student academic data, validate records, and explore performance through interactive dashboards and visualizations.

### 1.3 Project Objective

To develop a simple, secure, and user-friendly academic analytics application that converts structured student performance data into meaningful statistical summaries and visual insights.

### 1.4 Intended Users

- **Administrator:** Manages teacher accounts and oversees uploaded datasets.
- **Educator:** Uploads permitted datasets and analyzes academic performance.

The MVP is designed for a single institution and is intended for academic analysis, not automated decisions about students.

---

## 2. Frozen Technology Stack

| Layer            | Selected technology       |
| -------------------- | ------------------------- |
| Frontend             | HTML5, CSS3, JavaScript   |
| UI framework         | Bootstrap 5               |
| Data visualization   | Plotly.js                 |
| Backend              | Python with Flask         |
| Data processing      | Pandas and NumPy          |
| Database             | SQLite                    |
| Database integration | Flask-SQLAlchemy          |
| Authentication       | Flask-Login               |
| Password security    | Werkzeug password hashing |
| Testing              | pytest                    |
| Version control      | Git and GitHub            |

**Implementation rule:** Keep the application as a single Flask-based web application. Do not introduce React, a separate Node.js backend, PostgreSQL infrastructure, or a separate API framework during the MVP.

---

## 3. Frozen Dataset Decision and Standardized CSV Contract

### 3.1 Primary Dataset

Use the **UCI Student Performance dataset** as the initial source for academic analytics.

The implementation will begin with one agreed dataset file and a fixed, documented schema. The team must select and document whether the Mathematics (`student-mat.csv`) or Portuguese (`student-por.csv`) dataset is used for the first working demonstration.

### 3.2 Canonical CSV Format

All files uploaded through the MVP must follow one standardized, comma-separated CSV format. Source files such as the UCI dataset and educator-created spreadsheets must be converted to this format before upload. The application will not attempt to automatically map arbitrary spreadsheet column names.

The canonical header is:

```csv
student_name,g1,g2,g3,studytime,absences
```

The columns must appear in this order, using these exact lowercase names.

| Column | Required? | Meaning and validation |
|---|---|---|
| `student_name` | Yes | Student display name or pseudonymous label. Names do not have to be unique. |
| `g1` | No | First assessment grade. |
| `g2` | No | Second assessment grade. |
| `g3` | Yes | Final or primary grade used for the minimum dashboard metrics. |
| `studytime` | No | Study time in actual hours per week when that measurement is available. Do not treat a category code as an exact number of hours. |
| `absences` | No | Number of recorded absences; must be a non-negative whole number when supplied. |

Example (illustrative values only):

```csv
student_name,g1,g2,g3,studytime,absences
Student 001,10,12,13,3,4
Student 002,14,15,16,5,2
Student 003,,9,10,2,6
```

Rules:
- `student_name` and `g3` are required. `g1`, `g2`, `studytime`, and `absences` may be blank.
- The application generates an internal unique `student_record_id`; the CSV does not supply the database primary key.
- Student names are labels, not unique identifiers. Duplicate names must not be rejected solely because they match.
- Grades must be numeric and fall within the grade scale configured for that dataset, such as 0–20 or 0–100. The dataset's scale must be visible in the interface.
- `g1`, `g2`, and `g3` are stable internal field names. Dataset metadata stores user-facing assessment labels (`g1_label`, `g2_label`, `g3_label`), for example “First Internal”, “Second Internal”, and “Final Exam”. Labels may differ by dataset; the underlying CSV column names do not.
- A dataset represents one subject and one defined class/section and academic context for MVP purposes. If source data mixes subjects, prepare separate subject datasets rather than combining them into one dataset.
- Store relevant dataset metadata, including dataset name, source filename, uploader, subject, department when known, class/section when known, academic year when known, grade-scale maximum, assessment labels, import status, record count, and upload timestamp. Unknown metadata must remain unknown rather than being invented.
- Users may upload multiple datasets and analyze each dataset independently. Advanced side-by-side comparison or merging of multiple datasets remains out of scope.
- Use a comma as the canonical delimiter. The application should provide clear validation feedback for an incorrect delimiter or malformed header.

### 3.3 Mapping the UCI Source Data

The UCI Student Performance source files use semicolon-separated fields and contain no real student names or student IDs in the documented dataset attributes. Before upload, convert the selected source file into the canonical CSV format:
- Map source `G1`, `G2`, and `G3` to `g1`, `g2`, and `g3`.
- Generate pseudonymous display labels such as `Student 001`, `Student 002`, and so on. These labels are for display only and must not be presented as verified real identities.
- Preserve the source grade scale: the UCI grades use a 0–20 scale.
- The UCI `studytime` field is a categorical code representing weekly study-time ranges, not an exact number of hours. Do not import those codes into canonical `studytime` as if they were hours. For UCI-derived data, leave canonical `studytime` blank unless a separate, clearly named category field is deliberately approved for a future schema version.
- Map `absences` to the canonical `absences` field where available.
- Record the selected UCI file and the conversion approach in the project documentation.

### 3.4 Initial Academic Variables

- `G1`: First-period grade
- `G2`: Second-period grade
- `G3`: Final grade
- `studytime`: Weekly study-time category
- `absences`: Number of absences recorded in the source dataset

The dashboard will treat `G3` as the final-grade measure, on the dataset's 0–20 scale.

### 3.5 Data Handling Rules

- Validate uploaded data against the canonical schema and the selected dataset's metadata.
- Reject or clearly report missing required columns, invalid data types, out-of-range grades, and invalid absence values.
- Preview the uploaded file before import and show understandable validation errors.
- Do not silently create a partial or misleading dataset after failed validation.
- Do not invent student identities, attendance records, or missing values.
- Distinguish unavailable data from a measured value of zero.
- Keep source data and imported records traceable to their dataset upload.

General-purpose support for arbitrary school spreadsheets is not required. Files must be converted to the canonical format before upload.

---

## 4. Final Scope: Included Features

### Module 1 — Authentication and Access Control

1. Login and logout functionality.
2. Two roles: Administrator and Educator.
3. Secure password hashing; plaintext passwords must not be stored.
4. Protected routes requiring authentication.
5. Role-based authorization for administrative functions.
6. Administrator-controlled creation and activation of teacher accounts.

**Expected outcome:** Only authorized users can access the appropriate application features.

### Module 2 — CSV Upload and Validation

1. Upload academic data in CSV format.
2. Preview the uploaded file before import.
3. Validate required columns, data types, missing values, and applicable value ranges.
4. Display understandable validation errors.
5. Import valid records into the database.
6. Prevent failed validation from silently creating a partial or misleading dataset.
7. Display import success or failure information.

**Expected outcome:** Users can identify data issues before relying on dashboard results.

### Module 3 — Dataset Management

1. Store imported datasets and their student records in SQLite.
2. Display available datasets and basic upload metadata.
3. Select a dataset for analysis.
4. Maintain an upload/import history.
5. Record relevant validation and import outcomes.

**Expected outcome:** Users can identify which dataset is being analyzed and trace it to its upload.

### Module 4 — Academic Analytics Dashboard

Provide summary statistics and interactive visualizations based on the selected dataset.

**Minimum dashboard indicators**

- Number of valid student records
- Average final grade (`G3`)
- Highest and lowest final grades
- Grade distribution

**Minimum visualizations**

- Distribution of final grades
- Comparison of `G1`, `G2`, and `G3`
- Final-grade patterns by study-time category
- Final-grade patterns by absence count or clearly defined absence groups

**Interactive analysis**

- Filter the displayed data using supported fields.
- Update summary metrics and charts to reflect the active filters.
- Compare relevant student groups.
- Explore relationships between selected academic variables.

All statistics and charts must be derived from the selected dataset and active filters. Charts must use accurate labels, units, and legends where applicable.

### Module 5 — Filtered Analytics Export

1. Export the records matching the current dashboard filters as a CSV file.
2. Include the relevant column headers.
3. Ensure the exported records match the selected dataset and applied filters.
4. Include a clear indication of the dataset and filter context in the export or accompanying report metadata.

The frozen MVP export format is **CSV**. PDF report generation and automated scheduled reports are not included.

### Module 6 — Testing and Documentation

1. Test authentication and role permissions.
2. Test CSV validation and import behaviour.
3. Test analytical calculations against known sample values.
4. Test dashboard filters and export consistency.
5. Provide installation and execution instructions.
6. Document the dataset schema and limitations.
7. Prepare a demonstration workflow and project report.

---

## 5. Core Functional Requirements

| ID    | Requirement                                                                           | Priority |
| ----- | ------------------------------------------------------------------------------------- | -------- |
| FR-01 | Users can log in and log out securely.                                                | Must     |
| FR-02 | The system enforces administrator and teacher roles.                                  | Must     |
| FR-03 | Administrators can create and activate teacher accounts.                              | Must     |
| FR-04 | Authorized users can upload and preview CSV files.                                    | Must     |
| FR-05 | The system validates the expected schema and record values.                           | Must     |
| FR-06 | Users receive understandable validation and import feedback.                          | Must     |
| FR-07 | Valid datasets and records are stored and selectable.                                 | Must     |
| FR-08 | Users can view upload/import history.                                                 | Must     |
| FR-09 | The dashboard calculates academic summary statistics.                                 | Must     |
| FR-10 | The dashboard displays the specified charts and group comparisons.                    | Must     |
| FR-11 | Dashboard filters update the displayed analytics.                                     | Must     |
| FR-12 | Users can export filtered records as CSV.                                             | Must     |
| FR-13 | The application handles expected errors without exposing sensitive technical details. | Must     |
| FR-14 | The project includes tests and reproducible setup documentation.                      | Must     |

---

## 6. Non-Functional Requirements

### Security

- Hash passwords before storage.
- Protect authenticated and administrator-only routes.
- Validate and sanitize user-supplied input.
- Use safe database query practices.
- Configure session and secret-key settings appropriately.
- Avoid exposing passwords or unnecessary personal information in logs or exports.

### Correctness

- Calculate statistics from the actual imported records.
- Apply filters consistently to metrics, charts, and exports.
- Handle empty datasets and invalid uploads gracefully.
- Document the grade scale and data limitations.

### Usability

- Use a clear, responsive Bootstrap interface.
- Provide meaningful success, warning, and error messages.
- Label charts and filters clearly.
- Keep the main workflow understandable to users with basic computer skills.

### Maintainability

- Separate routes, data processing, database models, and templates.
- Keep analytics calculations reusable and independently testable.
- Use Git for source control and integrate changes regularly.

### Performance

- The MVP should handle the selected UCI dataset and reasonably sized classroom CSV files on a typical student development computer.
- The system is not required to support institution-wide production traffic or very large datasets.

---

## 7. Proposed Database Structure

The initial SQLite schema will use the following logical entities:

1. **Users** — login credentials, role, account status, and relevant timestamps.
2. **Datasets** — dataset name, source or filename, upload metadata, and import status.
3. **Student Records** — academic attributes and a reference to the parent dataset.
4. **Upload Errors** — validation issues and import error details, where applicable.

An institution table is not required for the single-institution MVP unless the implementation demonstrates a clear need. Multiple-institution management is explicitly excluded.

Database field definitions and relationships must be finalized before the main implementation begins.

---

## 8. Explicit Exclusions

The following features are **not part of Version 1.0**:

- Machine-learning grade prediction or risk classification
- AI-generated recommendations or automated interventions
- Student and parent login portals
- Real-time attendance tracking
- ERP or learning-management-system integrations
- Email verification and password-reset workflows
- Multi-institution or multi-college management
- Arbitrary spreadsheet mapping and support for every school data format
- Mobile applications
- Cloud-scale deployment and infrastructure
- Separate microservices or backend frameworks
- PDF report generation and scheduled report delivery
- Comparing multiple academic terms or datasets as a separate advanced feature
- Administrator-driven dataset deletion as a dedicated feature
- Advanced predictive modelling, complex statistical inference, or automated decisions about students

A feature being technically possible does not make it part of the frozen scope.

---

## 9. Eight-Week Development Plan

### Week 1 — Planning and Setup

- Freeze requirements and dataset schema.
- Create the GitHub repository and Flask project structure.
- Set up the database and initial templates.
- Agree on team responsibilities and coding conventions.

**Milestone:** Application starts locally and the initial database is available.

### Week 2 — Authentication

- Implement login and logout.
- Implement role checks and protected routes.
- Add administrator-controlled teacher account management.

**Milestone:** Both roles can authenticate and access only their permitted functions.

### Week 3 — CSV Ingestion

- Implement upload and preview.
- Add schema and value validation.
- Display validation errors and import results.

**Milestone:** A valid CSV can be imported, and an invalid CSV produces useful feedback.

### Week 4 — Database and Dataset Management

- Finalize dataset and student-record models.
- Store and retrieve imported records.
- Implement dataset selection and import history.

**Milestone:** Users can select an imported dataset for analysis.

### Week 5 — Analytics

- Implement tested statistical calculations.
- Build the initial dashboard metrics.
- Add the minimum required charts.

**Milestone:** The dashboard shows verified results from the selected dataset.

### Week 6 — Filters and Export

- Implement interactive dashboard filters.
- Ensure metrics and charts update consistently.
- Implement filtered CSV export.

**Milestone:** Filtered analytics and exported records agree.

### Week 7 — Integration and Testing

- Integrate all modules.
- Test role permissions, upload failures, calculations, filters, and exports.
- Fix defects and improve error handling.

**Milestone:** The full workflow operates end to end.

### Week 8 — Finalization

- Complete regression testing.
- Finalize the README, report, and setup instructions.
- Prepare sample data and a demonstration.
- Freeze the release and record known limitations.

**Milestone:** A reproducible, tested MVP is ready for academic demonstration.

---

## 10. Team Responsibilities

### Member 1 — Data Processing and Analytics

- Dataset understanding and data dictionary
- Pandas validation and preprocessing
- Statistical calculations
- Dashboard metrics and chart correctness
- Analytical test cases

### Member 2 — Backend and Database

- Flask application structure
- Authentication and role authorization
- SQLAlchemy models and SQLite integration
- Upload/import routes and dataset history
- Security and backend tests

### Member 3 — Frontend and Dashboard UX

- Bootstrap layout and navigation
- Login and upload interfaces
- Dashboard layout, filters, and Plotly.js visualizations
- Export interface and usability improvements
- User-facing documentation and demonstration preparation

**Shared responsibilities:** Git integration, code review, end-to-end testing, debugging, final report, and presentation.

Responsibilities may overlap, but each module must have one clearly accountable owner.

---

## 11. Acceptance Criteria

The MVP is considered complete only when the following criteria are demonstrated.

### A. Authentication

- [ ] Administrator and teacher users can log in and log out.
- [ ] Passwords are stored as secure hashes, not plaintext.
- [ ] Unauthenticated users cannot access protected application pages.
- [ ] A teacher cannot perform administrator-only actions.
- [ ] Administrators can create and activate teacher accounts.

### B. Upload and Validation

- [ ] A valid CSV matching the agreed schema can be previewed and imported.
- [ ] A file missing a required column is rejected with a clear explanation.
- [ ] Invalid data types and applicable invalid values are reported.
- [ ] Import failures do not silently create misleading partial datasets.
- [ ] Upload outcomes and relevant validation errors are recorded or displayed.

### C. Dataset Management

- [ ] Imported datasets appear in the dataset list.
- [ ] A user can select a dataset for analysis.
- [ ] The dashboard uses the selected dataset rather than unrelated records.
- [ ] Upload history shows sufficient information to identify each import.

### D. Analytics

- [ ] The record count matches the valid records in the selected dataset.
- [ ] Average, minimum, and maximum final grades match independently verified calculations.
- [ ] Grade-distribution and academic-comparison charts render correctly.
- [ ] Study-time and absence analyses use the actual available source fields.
- [ ] Filters update metrics and visualizations consistently.
- [ ] Empty results and missing data are handled without application crashes.
- [ ] Chart titles, axes, and grade scale are understandable.

### E. Export

- [ ] A user can export filtered records as a CSV file.
- [ ] The export contains the expected headers and only the matching records.
- [ ] Export results are consistent with the selected dataset and active filters.
- [ ] The exported file opens in a standard spreadsheet application.

### F. Quality and Delivery

- [ ] Core authentication, validation, analytics, filter, and export tests pass.
- [ ] The main workflow can be demonstrated from login through CSV upload, dashboard analysis, and export.
- [ ] A new team member can follow the README to set up and run the application.
- [ ] The project report documents the architecture, dataset, tests, limitations, and future enhancements.
- [ ] The delivered application runs locally without requiring excluded infrastructure.

**Release rule:** Any failed Must requirement must be fixed or explicitly documented as an unresolved blocker before the team declares the MVP complete.

---

## 12. Scope-Control Rules

1. Version 1.0 is the agreed implementation baseline.
2. No new major feature is added without team agreement and an assessment of its effect on the eight-week schedule.
3. Required features take priority over optional polish.
4. The team must maintain a working integrated version throughout development.
5. At least the final two weeks are reserved for integration, testing, documentation, and demonstration preparation.
6. Any feature deferred from the frozen scope belongs in a future-enhancement list, not the MVP backlog.

---

## 13. Final Definition of Done

EduAnalytics Version 1.0 is complete when an authorized administrator or teacher can log in, upload and validate the agreed UCI-format academic CSV, select the imported dataset, explore correct and interactive academic summaries, filter the results, export matching records as CSV, and complete the workflow without critical errors.

The deliverable must include source code, database setup, test evidence, installation instructions, the project report, and a working demonstration.

**Final decision:** Build the smallest complete, secure, and testable academic analytics platform first. Predictive features, extra integrations, and advanced reporting remain future work.

**Specification status: FROZEN — VERSION 1.0**
