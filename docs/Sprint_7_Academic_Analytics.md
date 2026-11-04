# Sprint 7 — Academic Analytics Dashboard

**Project:** EduAnalytics — Student Academic Performance Analytics Platform  
**Sprint:** 7  
**Status:** Planned — Revised Draft  
**Document Version:** 1.1  
**Previous Sprint:** Sprint 6 — Dataset Management  
**Next Milestone:** Filtered Analytics Export  
**Revision Date:** 4 November 2026

> **Living document:** Update phase statuses, technical decisions, test evidence and known issues as Sprint 7 progresses. A task must only be marked complete after implementation and verification against the current project checkout.

---

## 1. Sprint Overview

### 1.1 Sprint Goal

Develop an Academic Analytics Dashboard that allows an authorized Administrator or Educator to analyse one selected, previously imported academic dataset.

The dashboard will provide:

- Dataset quality assessment.
- Descriptive academic statistics.
- Grade distribution analysis.
- Assessment comparisons.
- Study-time analysis.
- Absence analysis.
- Correlation analysis.
- Rule-based statistical findings.
- Interactive filters.
- Responsive visualizations.

All analysis must be derived from the selected dataset and its actual stored records.

### 1.2 Sprint Objective

Sprint 7 introduces the Data Science and Exploratory Data Analysis (EDA) layer of EduAnalytics.

The existing platform already provides authentication, CSV import, database storage, dataset management and active dataset selection.

Sprint 7 builds on those capabilities without replacing or unnecessarily modifying the completed workflows.

### 1.3 Sprint Scope Decision

The revised sprint allocation is:

| Capability | Sprint allocation |
|---|---|
| Dataset retrieval and preprocessing | Sprint 7 |
| Dataset quality assessment | Sprint 7 |
| Descriptive statistics | Sprint 7 |
| Grade distribution | Sprint 7 |
| Assessment comparison | Sprint 7 |
| Study-time and absence analysis | Sprint 7 |
| Correlation analysis | Sprint 7 |
| Rule-based statistical findings | Sprint 7 |
| Interactive filters | Sprint 7 |
| Filtered CSV export | Subsequent milestone |

**Scope revision:** Interactive filters, previously planned for the subsequent sprint, are now included in Sprint 7. Filtered CSV export remains outside Sprint 7.

The master roadmap and README must be updated to reflect this allocation.

---

## 2. Expected User Workflow

1. An authorized Administrator or Educator signs in.
2. The user opens Dataset Management.
3. The user selects one imported dataset.
4. The user opens Academic Analytics.
5. The server validates access to the selected dataset.
6. The application retrieves the selected dataset's records.
7. Records are prepared temporarily in memory.
8. The analytics service calculates statistics and EDA results.
9. The dashboard displays the calculated results.
10. The user applies interactive filters.
11. The dashboard recalculates the applicable metrics and visualizations.
12. The user resets filters or returns to Dataset Management.
13. The original SQLite records remain unchanged.

### 2.1 Dataset Independence

- Analyse one selected dataset at a time.
- Never combine records from separate datasets.
- Validate dataset authorization on every protected analytics request.
- Never trust a dataset identifier supplied by the browser without server-side validation.

### 2.2 Temporary Analysis

The original imported dataset remains permanently stored in SQLite.

Analysis uses temporary request-scoped objects:

| Information | Storage |
|---|---|
| Imported dataset | SQLite |
| Student academic records | SQLite |
| Dataset metadata | Existing database schema |
| Active dataset reference | Existing approved selection mechanism |
| Temporary DataFrame | Request memory |
| Statistical calculations | Request memory |
| Correlation results | Request memory |
| Chart data | Request memory |
| Filtered analysis results | Request memory |

Do not store complete student records, DataFrames or analytics results in Flask sessions or unprotected process-global variables.

Temporary analysis objects should become eligible for cleanup when the request finishes.

This design must remain safe with the existing Flask and Waitress configuration, including multiple workers.

---

## 3. Dataset Structure and Compatibility

### 3.1 Existing Canonical Schema

The frozen MVP specifies the following import schema:

`student_name,g1,g2,g3,studytime,absences`

| Field | Existing MVP requirement | Analysis use |
|---|---|---|
| student_name | Required identifier field | Display label, not a numerical variable |
| g1 | Optional | First assessment |
| g2 | Optional | Second assessment |
| g3 | Required | Primary final-grade variable |
| studytime | Optional | Study-time analysis |
| absences | Optional | Absence analysis |

### 3.2 Student Identifier Decision

**Planning decision:** Reuse the existing imported identifier field and database model. Do not change the database schema solely for Sprint 7.

The existing `student_name` field must be inspected during Phase 1.

Confirm:

- Its actual model field name.
- Whether the importer requires it.
- Whether UCI conversion generates display names or another identifier.
- Whether values are unique.

Use the existing database record primary key for internal record identity where necessary.

Do not assume that student names are unique. Treat display names as labels rather than numerical analysis variables.

### 3.3 Required and Optional Analysis Fields

Required for overall academic performance:

- Valid G3.

Optional:

- G1.
- G2.
- Study time.
- Absences.

An unavailable optional column must not prevent the overall G3 dashboard from operating.

### 3.4 Units and Metadata

The analysis must use the units established by verified dataset metadata.

- G1, G2 and G3 use the configured grade scale.
- Study time uses hours per week only when the source confirms actual hours.
- Absences use days only when the source confirms that unit.
- Unknown units must remain unknown.

**UCI limitation:** UCI Student Performance `studytime` values are categorical codes representing weekly study-time ranges. They are not exact hours.

When the imported dataset uses these codes:

- Treat them as categorical values.
- Display their category meaning when verified.
- Perform category-wise G3 analysis.
- Do not calculate average study hours or interpret category codes as exact hours.
- Do not calculate Pearson correlation using those codes as if they were exact hours.

### 3.5 Phase 1 Compatibility Verification

The following remain pending until the actual source code and stored data are inspected:

- [ ] Confirm the `StudentRecord` identifier field.
- [ ] Confirm the stored study-time representation.
- [ ] Confirm absence units and metadata.
- [ ] Confirm the configured grade scale.
- [ ] Confirm assessment-label storage.
- [ ] Confirm how missing values are represented.
- [ ] Confirm the current authorization rules.
- [ ] Confirm the existing charting library and JavaScript conventions.

No database schema change is approved by this document.

---

## 4. Data Eligibility and Preprocessing

### 4.1 Distinguish Import Rejection from Analysis Exclusion

Sprint 7 must not silently redefine Sprint 5 CSV validation or import behaviour.

Two different situations must be distinguished:

**Import rejection:** A CSV row that fails the existing import validation and is not stored as a valid imported record.

**Analysis exclusion:** A record already stored in SQLite but not eligible for a particular calculation because one or more required values are missing or invalid.

Sprint 7 is responsible for reporting analysis eligibility. It must not rewrite the completed importer.

### 4.2 Analysis-Specific Eligibility

Each analysis uses its own eligible records.

| Analysis | Required valid values |
|---|---|
| Overall academic statistics | G3 |
| Grade distribution | G3 |
| G1 statistics | G1 |
| G2 statistics | G2 |
| G3 statistics | G3 |
| G1–G3 individual comparison | Paired G1 and G3 |
| G2–G3 individual comparison | Paired G2 and G3 |
| Study-time group analysis | Study time and G3 |
| Study-time correlation | Paired numerical study time and G3 |
| Absence group analysis | Absences and G3 |
| Absence correlation | Paired absences and G3 |

A record with valid G3 but missing G1 remains eligible for overall G3 analysis.

A record with valid G3 but missing study time remains eligible for overall G3 analysis but is excluded from study-time analysis.

### 4.3 Data Quality Metrics

Calculate dataset-level quality information using the complete selected dataset.

Display:

- Total imported records available for analysis.
- Valid G3 records.
- Records excluded from G3 analysis.
- Missing G1 values.
- Missing G2 values.
- Missing G3 values.
- Missing study-time values, when the field exists.
- Missing absence values, when the field exists.

Also report invalid values where the stored data and model permit reliable identification.

Do not count import-rejected rows as stored records.

### 4.4 Missing Data Rules

- Missing values must not be replaced with zero.
- Missing optional values must not unnecessarily exclude valid G3 records.
- Each calculation must use its own eligible observations.
- Missing values must be excluded from calculations that require those values.
- Empty analysis results must be represented as unavailable, not as zero.
- The dashboard must explain when a section cannot be calculated.

---

## 5. Academic Analytics Requirements

The dashboard contains seven analytical sections.

### 5.1 Dataset Quality Assessment

**Purpose:** Understand the completeness and quality of the selected dataset.

Display:

| Metric | Definition |
|---|---|
| Total records | All imported records retrieved for the selected dataset |
| Valid G3 records | Records eligible for overall final-grade analysis |
| Excluded from G3 analysis | Stored records not eligible for G3 analysis |
| Missing G1 | Records without a usable G1 value |
| Missing G2 | Records without a usable G2 value |
| Missing G3 | Records without a usable G3 value |
| Missing study time | Records without usable study-time data |
| Missing absences | Records without usable absence data |

Dataset quality metrics always describe the complete selected dataset. They do not change when dashboard filters are applied.

### 5.2 Descriptive Statistics

**Purpose:** Present the overall academic performance of the selected student group.

Primary KPI cards:

1. Valid G3 count.
2. Average G3.
3. Highest G3.
4. Lowest G3.

Detailed statistics:

- Median G3.
- Population standard deviation.
- First quartile (Q1).
- Third quartile (Q3).

#### Statistical Conventions

| Calculation | Convention |
|---|---|
| Mean | Arithmetic mean |
| Median | Standard median |
| Minimum | Smallest valid observation |
| Maximum | Largest valid observation |
| Standard deviation | Population standard deviation, `ddof=0` |
| Quartiles | 25th and 75th percentiles using linear interpolation |
| Empty calculation | Unavailable value, not zero |

Population standard deviation is selected because the initial analysis treats the complete uploaded dataset as the group being described. If the project later treats the dataset as a sample of a wider population, that assumption must be reviewed.

The calculation method must remain consistent across the analytics service and tests.

### 5.3 Grade Distribution

**Purpose:** Understand the distribution of students across final-grade ranges.

Display:

- Grade distribution chart.
- Student count in each band.
- Percentage in each band.

For a configured 0–20 grade scale, use the following proposed project-defined bands:

| Interval | Label |
|---|---|
| 0 ≤ grade < 5 | Very low |
| 5 ≤ grade < 9 | Low |
| 9 ≤ grade < 13 | Moderate |
| 13 ≤ grade < 17 | Good |
| 17 ≤ grade ≤ 20 | High |

These are project-defined display categories, not official VTU classifications.

The interval definitions support decimal grades and do not overlap.

The grade scale remains authoritative. If a dataset uses a different scale, the bands must be adapted or explicitly configured rather than applying the 0–20 bands automatically.

Group percentage:

\[
\text{Percentage} =
\frac{\text{Students in group}}{\text{Valid G3 count}}\times100
\]

All group counts together must equal the valid G3 count.

### 5.4 Assessment Comparison

**Purpose:** Explore performance across G1, G2 and G3.

Display available assessment information:

- Valid count for each assessment.
- Average G1.
- Average G2.
- Average G3.
- Assessment comparison chart.
- Paired individual differences where applicable.

Mean difference between assessment averages:

\[
Mean(G3)-Mean(G1)
\]

Individual paired difference:

\[
d_i=G3_i-G1_i
\]

Calculate individual differences only for records with both valid G1 and G3 values.

The mean difference between assessment averages must not be described as the average individual student's improvement.

If an assessment column is unavailable, omit its calculations and chart series.

### 5.5 Study-Time Analysis

**Purpose:** Explore the relationship between study time and final academic performance.

When actual numerical study hours are available, display:

- Average study hours.
- Study-time group comparison.
- Student count in each group.
- Average G3 per group.
- Study-time versus G3 scatter plot.
- Pearson correlation, when computable.

Proposed project-defined groups for verified numerical hours:

| Group | Hours per week |
|---|---|
| Group 1 | 0–5 |
| Group 2 | Above 5–10 |
| Group 3 | Above 10–15 |
| Group 4 | Above 15 |

If study time is categorical, use category-wise performance comparisons instead.

Do not show exact-hour averages, numerical scatter plots or Pearson correlations for categorical codes.

### 5.6 Absence Analysis

**Purpose:** Explore the relationship between absence days and academic performance.

When absence values and units are verified, display:

- Average absence days.
- Absence group comparison.
- Student count per group.
- Average G3 per group.
- Absences versus G3 scatter plot.
- Pearson correlation, when computable.

Proposed project-defined groups:

| Group | Absence days |
|---|---|
| No absences | 0 |
| Low | 1–5 |
| Moderate | 6–10 |
| High | Above 10 |

Use paired valid observations for scatter plots and correlation.

### 5.7 Correlation Analysis

Pearson correlation is used for supported numerical variables.

\[
r=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\sigma_Y}
\]

#### Minimum Observation Rule

- Zero paired observations: unavailable.
- One paired observation: unavailable.
- Two paired observations: unavailable for project interpretation.
- Three or more paired observations: coefficient may be calculated and labelled exploratory.
- Zero variance in either variable: unavailable.

A result based on a small number of observations must not be presented as strong evidence.

Correlation describes linear association. It does not establish causation.

### 5.8 Rule-Based Statistical Findings

**Purpose:** Present concise observations generated from calculated results.

Findings must be deterministic and based on documented thresholds.

Proposed initial rules:

| Finding | Rule |
|---|---|
| Average final grade | Report the calculated mean when at least one valid G3 exists |
| Largest grade group | Report the band with the largest valid student count |
| Group performance difference | Mention a difference only when the group means differ by at least 1 grade point and both groups meet the minimum group count |
| Correlation finding | Generate a narrative only when at least 10 paired observations exist and the absolute Pearson coefficient is at least 0.30 |
| Insufficient data | Suppress the finding and explain that there are insufficient observations |

The minimum group count for narrative comparisons is 3.

Correlation findings:

- \(r \geq 0.30\): positive linear association.
- \(r \leq -0.30\): negative linear association.
- \(-0.30 < r < 0.30\): no notable linear association under the project's rule.

These are project interpretation thresholds, not universal statistical significance criteria.

Findings must not claim causation or make automated decisions about individual students.

No AI-generated recommendations or interventions are included.

---

## 6. Interactive Filters

Interactive filters are included in Sprint 7.

### 6.1 Supported Filters

| Filter | Availability |
|---|---|
| G3 range | Always |
| G1 range | When G1 exists |
| G2 range | When G2 exists |
| Study-time range/category | When usable study-time data exists |
| Absence range | When usable absence data exists |

### 6.2 Combined Filter Logic

When multiple filters are active, use **AND logic**.

A record must satisfy every active filter to be included in the filtered analysis.

For example:

- G3 between 10 and 20.
- Study-time category equal to a selected category.
- Absences between 0 and 5.

Only records satisfying all three conditions are included.

### 6.3 Missing Values During Filtering

- When no filter is active for a field, missing values in that field do not exclude a record from unrelated analysis.
- When a filter is active on a field, records with missing or invalid values for that field do not match the filter.
- Missing values must not be interpreted as zero.
- Selecting an assessment filter excludes records without a usable value for that assessment.

### 6.4 Dataset-Level and Filtered Metrics

Keep two concepts separate.

**Dataset-level quality:**

- Always calculated on the complete selected dataset.
- Does not change when filters are applied.
- Describes the original imported dataset.

**Filtered analysis:**

- Calculated on records matching all active filters.
- Updates applicable KPI cards, statistics, charts and findings.
- Displays the number of matching records.

### 6.5 Filter Behaviour

- All available filters must update the applicable analytics.
- Filter changes must not change the selected dataset.
- Reset Filters restores the unfiltered selected-dataset analysis.
- Empty results display a clear empty state.
- Filters must be validated on the server.
- Filtered analysis must never include another dataset's records.

Filtered CSV export is reserved for the subsequent milestone.

---

## 7. Dashboard Layout

Recommended page order:

| Order | Section | Display |
|---:|---|---|
| 1 | Header | Dashboard title, selected dataset and status |
| 2 | Dataset information | Subject, class, academic year and grade scale |
| 3 | Filters | Available interactive filters |
| 4 | Dataset quality | Total, valid, excluded and missing-value metrics |
| 5 | Academic overview | Four KPI cards |
| 6 | Detailed statistics | Median, standard deviation and quartiles |
| 7 | Grade distribution | Distribution chart and percentages |
| 8 | Assessment comparison | G1/G2/G3 comparison |
| 9 | Study-time analysis | Group analysis and applicable correlation |
| 10 | Absence analysis | Group analysis and applicable correlation |
| 11 | Statistical findings | Deterministic observations |

### 7.1 UI Requirements

- Reuse the existing Bootstrap interface and navigation.
- Use the existing charting library where suitable.
- Display responsive chart layouts.
- Stack charts vertically on narrow screens.
- Use accurate chart titles, axes, legends and units.
- Display the configured grade scale.
- Hide unavailable optional analysis sections.
- Provide loading, error and empty states.
- Provide a return action to Dataset Management.

---

## 8. Implementation Plan

Implement one phase at a time. Review the current code before changing models, routes, templates, services or dependencies.

| Phase | Work | Expected outcome | Status |
|---|---|---|---|
| 1. Code review and architecture | Inspect models, importer, authorization, selected dataset, metadata, dependencies and charting. Finalize compatibility and calculation decisions. | Approved implementation design. | Planned |
| 2. Dataset retrieval and preprocessing | Retrieve the selected dataset securely, prepare temporary analysis input and calculate quality metrics. | Tested analysis input and data-quality results. | Planned |
| 3. Descriptive statistics | Implement summary statistics and grade distribution. | Independently tested calculation service. | Planned |
| 4. Advanced EDA | Implement assessment comparisons, study-time analysis, absence analysis and correlations. | Tested analysis for available fields. | Planned |
| 5. Dashboard interface | Integrate KPI cards, detailed statistics, charts and findings. | Responsive Academic Analytics Dashboard. | Planned |
| 6. Interactive filters | Implement filters incrementally, combined AND behaviour and reset. | Consistent filtered analytics. | Planned |
| 7. Integration and verification | Run statistical, security, lifecycle, UI and regression tests. Update documentation. | Verified Sprint 7 release candidate. | Planned |

### 8.1 Phase Update Record

| Date | Phase | Changes made | Tests and results | Issues / next action |
|---|---|---|---|---|
| — | — | No Sprint 7 implementation recorded yet. | — | Begin Phase 1 code review. |

---

## 9. Proposed Technical Architecture

The analytics calculation logic must remain separate from Flask routes and HTML templates.

The following is a proposed logical organization, not a requirement to create one file for every function:

```text
app/
├── services/
│   ├── dataset_retrieval.py
│   ├── data_preprocessing.py
│   └── analytics_service.py
│
├── routes/
│   └── analytics.py
│
├── templates/
│   └── analytics/
│       └── dashboard.html
│
└── static/
    ├── css/
    │   └── analytics.css
    └── js/
        └── analytics.js
```

Use the existing project structure and naming conventions wherever possible.

### 9.1 Service Responsibilities

The analytics calculation layer should:

1. Receive validated selected-dataset context.
2. Retrieve records belonging only to that dataset.
3. Prepare temporary analysis data.
4. Calculate dataset quality.
5. Calculate descriptive statistics.
6. Calculate grade distributions.
7. Perform assessment comparisons.
8. Perform available study-time and absence analyses.
9. Calculate correlations where valid.
10. Apply validated filters.
11. Return structured results for visualization.

### 9.2 Dependencies

Inspect existing requirements before adding packages.

Potential libraries:

| Library | Purpose |
|---|---|
| Pandas | Tabular data processing |
| NumPy | Numerical calculations |
| SciPy | Additional statistical functions, if necessary |
| Existing charting library | Dashboard visualization |

Do not add unnecessary dependencies or duplicate functionality already available in the project.

### 9.3 Visualization Separation

Statistical business logic belongs in the analytics service.

The charting library should visualize already calculated results. It must not become the location where the project's statistical calculations are implemented.

---

## 10. Important Technical Decisions

### 10.1 Reuse Existing Models

- Reuse the existing `Dataset` and `StudentRecord` models.
- Reuse the existing importer and metadata.
- Do not create a second dataset storage system.
- Do not modify the database schema without an approved technical reason.

### 10.2 Server-Side Authorization

Every analytics request must:

- Require authentication.
- Apply existing role permissions.
- Validate the selected dataset.
- Verify user authorization.
- Restrict database queries to the selected dataset.
- Reject invalid, stale or unauthorized references.

### 10.3 Temporary Analysis Lifecycle

- Preserve original imported records in SQLite.
- Keep calculations request-scoped.
- Do not store complete DataFrames or student records in Flask sessions.
- Avoid unprotected process-global analysis state.
- Do not log student-level academic records.
- Discard temporary analysis objects after the request.
- Ensure multiple Waitress workers and separate user sessions remain isolated.

### 10.4 Missing Data

- Do not replace missing values with zero.
- Use analysis-specific eligibility.
- Report missing-value counts.
- Distinguish dataset quality from filtered analysis.
- Return unavailable values for calculations that cannot be performed.

### 10.5 Statistical Consistency

Use the conventions defined in Section 5 for:

- Population standard deviation.
- Linear-interpolation quartiles.
- Grade distribution boundaries.
- Minimum correlation observations.
- Rule-based finding thresholds.

Tests must independently verify these conventions.

### 10.6 Preserve Existing Functionality

- Do not unnecessarily modify authentication.
- Do not break CSV upload and validation.
- Do not break Dataset Management.
- Do not combine datasets.
- Keep changes small and reviewable.
- Run relevant tests after each implementation phase.

---

## 11. Acceptance Criteria

Sprint 7 must not be marked complete until every applicable criterion has been implemented and verified against the current checkout.

### 11.1 Dataset Retrieval and Authorization

- [ ] Authorized users can open Academic Analytics.
- [ ] A valid selected dataset is required.
- [ ] Dataset authorization is validated server-side.
- [ ] Analytics use only the selected dataset.
- [ ] Dataset A never includes Dataset B records.
- [ ] Invalid and unauthorized references are rejected.
- [ ] Existing Dataset Management remains intact.

### 11.2 Preprocessing and Data Quality

- [ ] Import rejection is distinguished from analysis exclusion.
- [ ] Valid G3 records are counted correctly.
- [ ] Missing values are counted correctly.
- [ ] Optional missing values do not unnecessarily exclude valid G3 records.
- [ ] Each analysis uses its own eligibility rules.
- [ ] Empty and invalid values are handled safely.
- [ ] Original SQLite records remain unchanged.

### 11.3 Descriptive Statistics

- [ ] Valid G3 count is correct.
- [ ] Average G3 is correct.
- [ ] Median G3 is correct.
- [ ] Minimum and maximum G3 are correct.
- [ ] Population standard deviation is correct.
- [ ] Q1 and Q3 use linear interpolation.
- [ ] Empty results are represented as unavailable.

### 11.4 Grade Distribution

- [ ] Grade bands respect the configured scale.
- [ ] Decimal values are assigned to exactly one band.
- [ ] Group counts match valid G3 records.
- [ ] Percentages are correct.
- [ ] Chart labels and grade units are accurate.

### 11.5 Assessment Comparison

- [ ] Available assessment means are correct.
- [ ] Missing assessment columns do not break the dashboard.
- [ ] Individual differences use paired valid records.
- [ ] Mean differences between assessment averages are not mislabelled as individual improvement.

### 11.6 Study-Time and Absence Analysis

- [ ] Analysis appears only when usable data exists.
- [ ] Categorical study-time codes are not treated as exact hours.
- [ ] Group counts and average G3 values are correct.
- [ ] Scatter plots use paired valid observations.
- [ ] Correlation safeguards are applied.
- [ ] Missing and constant values are handled safely.

### 11.7 Correlation and Findings

- [ ] Correlation requires at least three paired observations.
- [ ] Zero-variance variables return unavailable results.
- [ ] Correlation findings require at least ten paired observations.
- [ ] Correlation thresholds are applied consistently.
- [ ] Group findings apply the documented minimum counts and grade-point difference.
- [ ] Findings do not imply causation.
- [ ] Unavailable findings are suppressed.

### 11.8 Interactive Filters

- [ ] Available filters are displayed correctly.
- [ ] Combined filters use AND logic.
- [ ] Missing values do not match active filters.
- [ ] Dataset-level quality metrics remain unchanged by filters.
- [ ] Filtered record counts are correct.
- [ ] Metrics and charts update consistently.
- [ ] Reset Filters restores the original analysis.
- [ ] Empty results display a useful state.
- [ ] Filters cannot access another dataset.

### 11.9 Temporary Analysis and Integrity

- [ ] Analysis results are not permanently stored.
- [ ] Student records and DataFrames are not stored in Flask sessions.
- [ ] Request-scoped temporary objects are discarded after processing.
- [ ] Separate users and Waitress workers remain isolated.
- [ ] Original imported records remain unchanged.

### 11.10 Regression and Documentation

- [ ] Authentication tests pass.
- [ ] Authorization tests pass.
- [ ] CSV upload and validation tests pass.
- [ ] Dataset Management tests pass.
- [ ] Sprint 7 analytical tests pass.
- [ ] README and project documentation are updated.
- [ ] Manual verification evidence is recorded.

---

## 12. Testing Requirements

Use the existing pytest setup. Test calculations independently before integrating them with the dashboard.

### 12.1 Base Statistical Test Dataset

| Student | G1 | G2 | G3 | Study hours | Absences |
|---|---:|---:|---:|---:|---:|
| A | 10 | 12 | 14 | 5 | 2 |
| B | 12 | 14 | 16 | 10 | 1 |
| C | 14 | 16 | 18 | 15 | 0 |
| D | 8 | 10 | 12 | 5 | 4 |

Expected results:

| Calculation | Expected result |
|---|---:|
| Valid G3 count | 4 |
| Average G3 | 15 |
| Median G3 | 15 |
| Highest G3 | 18 |
| Lowest G3 | 12 |
| Population standard deviation of G3 | 2.2361 |
| G3 Q1 — linear interpolation | 13.5 |
| G3 Q3 — linear interpolation | 16.5 |
| Average study time | 8.75 hours |
| Average absences | 1.75 days |
| Average G1 | 11 |
| Average G2 | 13 |
| Average G3 minus average G1 | 4 |
| Average G3 minus average G2 | 2 |

The dataset assumes exact numerical study hours and absence days. It is a synthetic calculation fixture, not a claim about the UCI study-time representation.

Use suitable floating-point tolerances in automated tests.

### 12.2 Preprocessing Tests

- [ ] Valid dataset.
- [ ] Missing required identifier.
- [ ] Missing required G3.
- [ ] Invalid numeric values.
- [ ] Negative study-time values.
- [ ] Negative absence values.
- [ ] Grades outside configured scale.
- [ ] Missing G1/G2.
- [ ] Missing study time.
- [ ] Missing absences.
- [ ] Empty dataset.
- [ ] Stored records with optional invalid values.

### 12.3 Statistical Tests

- [ ] Mean, median, minimum and maximum.
- [ ] Population standard deviation.
- [ ] Linear-interpolation quartiles.
- [ ] Grade distribution counts and percentages.
- [ ] Assessment averages.
- [ ] Paired assessment differences.
- [ ] Group averages.
- [ ] Pearson correlation.
- [ ] Zero-variance correlation handling.
- [ ] Insufficient paired observations.
- [ ] Floating-point tolerance.

### 12.4 Dashboard and Filter Tests

- [ ] All supported columns available.
- [ ] G1/G2 unavailable.
- [ ] Study time unavailable.
- [ ] Absences unavailable.
- [ ] Optional values missing in individual records.
- [ ] Each filter independently.
- [ ] Multiple filters together.
- [ ] AND logic.
- [ ] Missing values under active filters.
- [ ] Reset Filters.
- [ ] Empty filter results.
- [ ] Dataset-level quality remains unchanged.
- [ ] Filtered metrics and charts match independently calculated results.

### 12.5 Security and Lifecycle Tests

- [ ] Unauthenticated analytics access.
- [ ] Unauthorized dataset access.
- [ ] Invalid dataset identifier.
- [ ] Dataset switching.
- [ ] Dataset isolation.
- [ ] Separate user sessions.
- [ ] Temporary analysis cleanup.
- [ ] Original SQLite dataset unchanged.
- [ ] Existing full regression suite.

### 12.6 Test Evidence Record

| Date | Command / test group | Result | Notes |
|---|---|---|---|
| — | Not yet executed | Pending | Begin after implementation. |

Previous sprint test results must not be recorded as Sprint 7 test evidence.

---

## 13. Out of Scope

The following are excluded from Sprint 7:

- Machine-learning grade prediction.
- Student risk classification.
- AI-generated recommendations.
- Automated academic interventions.
- Cross-dataset comparison.
- Multi-institution analytics.
- Permanent storage of calculated analytics results.
- Filtered CSV export.
- PDF reports.
- Scheduled reports.
- Advanced hypothesis testing.
- Real-time attendance tracking.
- Changes to the frozen MVP requirements without an approved scope decision.

---

## 14. Definition of Done

Sprint 7 is complete when an authorized Administrator or Educator can:

1. Select one imported dataset.
2. Retrieve its records securely.
3. Explore accurate dataset quality information.
4. View independently verified descriptive statistics.
5. Explore grade distribution and available assessment comparisons.
6. Analyse available study-time and absence information.
7. View supported correlation results and deterministic findings.
8. Apply interactive filters with consistent results.
9. Reset filters.
10. Exit analysis without changing or deleting the original SQLite dataset.

All applicable automated tests must pass, existing functionality must remain intact, and implementation evidence must be recorded.

---

## 15. Phase Completion Record

| Phase | Description | Status | Evidence |
|---|---|---|---|
| 1 | Code review and architecture | Planned | Pending |
| 2 | Dataset retrieval and preprocessing | Planned | Pending |
| 3 | Descriptive statistics and grade distribution | Planned | Pending |
| 4 | Advanced EDA | Planned | Pending |
| 5 | Dashboard interface and visualization | Planned | Pending |
| 6 | Interactive filters | Planned | Pending |
| 7 | Integration and verification | Planned | Pending |

---

## 16. Change Log

| Date | Change / decision | Reason | Status |
|---|---|---|---|
| 2026-11-04 | Initial Sprint 7 planning document created. | Establish analytics scope. | Revised |
| 2026-11-04 | Incorporated review of schema and identifier compatibility. | Avoid unnecessary database changes. | Decision documented; code verification pending |
| 2026-11-04 | Defined analysis-specific eligibility. | Avoid excluding valid records from unrelated calculations. | Defined |
| 2026-11-04 | Selected population standard deviation and linear-interpolation quartiles. | Ensure consistent statistical results. | Defined |
| 2026-11-04 | Defined non-overlapping decimal-grade bands for the 0–20 example scale. | Avoid ambiguous grade boundaries. | Proposed |
| 2026-11-04 | Defined AND filter logic and separate dataset-level quality metrics. | Ensure consistent filtered analysis. | Defined |
| 2026-11-04 | Defined correlation and finding safeguards. | Avoid misleading statistical interpretation. | Defined |
| 2026-11-04 | Extended expected statistical test results. | Improve independent verification. | Defined |
| 2026-11-04 | Moved interactive filters into Sprint 7. | Explicit revision of sprint allocation. | Approved in planning draft |
| 2026-11-04 | Retained filtered CSV export for the subsequent milestone. | Keep Sprint 7 focused. | Defined |

---

**Document status: VERSION 1.1 — REVISED PLANNING DRAFT**

**Implementation status: NOT STARTED**

**Next action: Phase 1 — Code Review and Architecture Verification.**

No analytics code, routes, templates, database migrations or dependencies should be changed until the Phase 1 review confirms compatibility with the existing project.
