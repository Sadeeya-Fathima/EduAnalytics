# Sprint 6 --- Dataset Management

**Project:** EduAnalytics --- Student Academic Performance Analytics
Platform\
**Sprint:** 6\
**Status:** Complete\
**Previous sprint:** Sprint 5 --- CSV Upload & Validation\
**Next sprint:** Sprint 7 --- Academic Analytics Dashboard

> **Living document:** Update phase statuses, decisions, implementation
> notes, test evidence, and known issues as work progresses. Mark an
> item complete only after it has been implemented and verified against
> the current checkout.

------------------------------------------------------------------------

## 1. What Sprint 6 Will Deliver

**Sprint goal:** Build the dataset management module so authorized users
can view imported datasets, understand their metadata, select a dataset
to work with, and review its import history before the analytics
dashboard is developed.

Sprint 6 connects successful CSV imports from Sprint 5 to a usable
dataset management experience.

### 1.1 Dataset listing

-   Display datasets imported into EduAnalytics in a clear table or card
    layout.
-   Show each dataset's name, subject, class, academic year, uploader,
    record count, and import status where those values are available.
-   Make available imported datasets accessible from the home dashboard.
-   Provide a separate Dataset Management page for the complete listing.

### 1.2 Dataset details and metadata

Allow users to inspect stored metadata, including dataset name, source,
subject and class context, academic year, grade scale, configured
assessment labels, record count, and available import information.

Display values from the database. Unknown or unavailable metadata must
remain unknown; do not fabricate or infer values without an
authoritative source.

### 1.3 Dataset selection

-   Allow a user to explicitly select one dataset as the active dataset
    for subsequent work.
-   Clearly identify the currently selected dataset.
-   Validate the selected dataset on the server.
-   Ensure subsequent dataset-scoped operations use only the selected
    dataset.
-   Do not combine records from different datasets.

### 1.4 Import history

Show the import information available in the current database schema,
such as import date and time, uploader, source, number of imported
records, and recorded import status.

Reuse existing stored information. Do not create a separate
import-history system unless code inspection establishes that the
current schema genuinely lacks required information.

### 1.5 Access control and data integrity

-   Apply existing authentication and authorization rules to dataset
    listing, details, selection, and import history.
-   Preserve existing database relationships.
-   Keep every `StudentRecord` associated with its correct parent
    dataset.
-   Prevent unauthorized or fabricated dataset identifiers from being
    used to access data.

------------------------------------------------------------------------

## 2. Expected User Workflow

1.  **Sign in:** An Administrator or authorized Educator signs in using
    the existing authentication flow.
2.  **Open the home dashboard:** The dashboard displays a convenient
    overview of available imported datasets, if any exist.
3.  **Open Dataset Management:** The user can view the complete list of
    imported datasets.
4.  **Inspect a dataset:** The user opens a dataset's details to review
    its stored metadata, record count, and available import information.
5.  **Select a dataset:** The user explicitly selects one dataset. The
    application confirms which dataset is currently active.
6.  **Continue to Sprint 7:** The selected dataset provides the context
    for the Academic Analytics Dashboard.

### 2.1 Empty state

If no datasets have been imported:

-   Show a clear message explaining that no datasets are available yet.
-   Provide a useful route or link to the existing CSV upload workflow,
    subject to the user's existing permissions.
-   Do not display fabricated example datasets as real application data.

------------------------------------------------------------------------

## 3. Implementation Plan

Implement one phase at a time. Review the existing code before changing
models, routes, templates, or database structure.

  ------------------------------------------------------------------------
  Phase             Work               Expected outcome  Status
  ----------------- ------------------ ----------------- -----------------
  1\. Review        Inspect `Dataset`  Existing          Complete
  existing code     and                structures and    
                    `StudentRecord`    reusable          
                    models, Sprint 5   functionality are 
                    upload             understood;       
                    routes/services,   genuine gaps are  
                    authorization,     documented.       
                    templates, and                       
                    database                             
                    relationships.                       
                    Identify which                       
                    import metadata is                   
                    already stored.                      

  2\. Dataset       Add the management Authorized users  Complete
  listing           route and listing  can see available 
                    template. Query    imported datasets 
                    datasets using     on the dashboard  
                    existing           and complete      
                    relationships and  listing page.     
                    permissions. Add a                   
                    dataset overview                     
                    to the home                          
                    dashboard.                            

  3\. Metadata      Add a dataset      Users can inspect Complete
  details           detail view.       a dataset         
                    Display stored     accurately        
                    metadata and       without           
                    calculate record   fabricated or     
                    counts from        unrelated         
                    associated         information.      
                    `StudentRecord`                      
                    rows.                                

  4\. Dataset       Implement explicit Users can         Complete
  selection         selection and      identify the      
                    server-side        active dataset,   
                    validation.        and invalid or    
                    Persist selection  unauthorized      
                    using the approved selections are    
                    approach in        rejected.         
                    Section 7.                           

  5\. Import        Display import     Users can review  Complete
  history           information        available import  
                    already available  details without   
                    in the current     unnecessary       
                    schema and upload  duplication.      
                    workflow. Document                   
                    information that                     
                    is not currently                     
                    stored.                              

  6\. Testing and   Add Sprint 6       Acceptance        Complete
  documentation     tests, run         criteria are      
                    relevant           verified and the  
                    regression tests,  module is ready   
                    review the         for Sprint 7      
                    implementation,    integration.      
                    and update project                   
                    documentation.                       
  ------------------------------------------------------------------------

### 3.1 Phase update record

  ----------------------------------------------------------------------------
  Date           Phase          Changes made     Tests and      Issues / next
                                                 results        action
  -------------- -------------- ---------------- -------------- --------------
  ---            ---            No               ---            Begin Phase 1
                                implementation                  code review.
                                recorded yet.                   

  ----------------------------------------------------------------------------

------------------------------------------------------------------------

## 4. Acceptance Criteria

Sprint 6 must not be marked complete until each applicable criterion has
been implemented and verified against the current checkout.

### 4.1 Verification checklist

-   [x] Authenticated users can open the dataset management page.
-   [x] The home dashboard displays available imported datasets when
    datasets exist.
-   [x] The page lists datasets already imported through Sprint 5.
-   [x] Dataset metadata is displayed accurately from stored values.
-   [x] Record counts match the `StudentRecord` rows associated with
    each dataset.
-   [x] Users can explicitly select a dataset and see which dataset is
    currently selected.
-   [x] Selection is validated server-side; fabricated, invalid,
    nonexistent, or unauthorized dataset identifiers are rejected.
-   [x] Import history displays the information available in the current
    database schema.
-   [x] An installation with no imported datasets shows a useful empty
    state and an appropriate route to CSV upload.
-   [x] Dataset queries and detail pages do not expose unrelated or
    unauthorized data.
-   [x] Automated tests cover listing, details, selection, permissions,
    metadata, and empty states.
-   [x] Existing authentication and CSV upload tests continue to pass.

### 4.2 Definition of done

A signed-in authorized user can browse imported datasets, inspect their
stored metadata and available import information, select one dataset
safely, and proceed to Sprint 7 with the selected dataset clearly
identified.

Existing authentication, authorization, and CSV upload behavior must
remain intact.

------------------------------------------------------------------------

## 5. Testing Requirements

Use the existing pytest setup. Run tests against the current checkout;
do not rely only on previously recorded test results.

### 5.1 Dataset listing

-   [ ] Test when zero datasets exist.
-   [ ] Test when one dataset exists.
-   [ ] Test when multiple datasets exist.
-   [ ] Verify that only datasets the user is authorized to access are
    listed.
-   [ ] Verify the home dashboard's dataset overview and empty state.

### 5.2 Metadata and record counts

-   [ ] Test datasets with missing optional metadata.
-   [ ] Verify configured assessment labels are displayed correctly.
-   [ ] Verify record counts against actual associated `StudentRecord`
    rows.
-   [ ] Verify that unavailable metadata is not fabricated.
-   [ ] Verify that details for one dataset do not include another
    dataset's records.

### 5.3 Dataset selection

-   [ ] Test selection of a valid dataset.
-   [ ] Test invalid and malformed dataset identifiers.
-   [ ] Test a nonexistent dataset identifier.
-   [ ] Test an identifier belonging to a dataset the user is not
    authorized to access.
-   [ ] Verify that the selected dataset is clearly identified.
-   [ ] Verify that selection persists according to the documented
    implementation decision.
-   [ ] Verify that selecting Dataset A does not display records
    belonging to Dataset B.

### 5.4 Import history

-   [ ] Verify that displayed import details match stored values.
-   [ ] Test missing or unavailable optional import information.
-   [ ] Verify that the page does not invent an import status, date,
    uploader, or source.
-   [ ] Verify that history is scoped to the relevant dataset.

### 5.5 Authentication and authorization

-   [ ] Unauthenticated requests are redirected or rejected according to
    the existing security design.
-   [ ] Administrator access follows existing approved permissions.
-   [ ] Educator access follows existing approved permissions.
-   [ ] Unauthorized users cannot access protected dataset functionality
    through direct URL requests.
-   [ ] Dataset identifiers submitted by the browser are validated on
    the server.

### 5.6 Regression

-   [ ] Existing authentication tests pass.
-   [ ] Existing authorization tests pass.
-   [ ] Existing CSV upload and validation tests pass.
-   [ ] Existing database relationship and model tests pass.
-   [ ] No existing Sprint 5 workflow is unintentionally changed.

### 5.7 Test evidence record

  -----------------------------------------------------------------------
  Date              Command / test    Result            Notes
                    group                               
  ----------------- ----------------- ----------------- -----------------
  2026-11-01        `.venv\Scripts\python.exe -m pytest -q`  136 passed      Full current
                                                        in 63.64s          regression suite
                                                                          passed, including
                                                                          Sprint 6 listing,
                                                                          dashboard, empty
                                                                          state, metadata,
                                                                          record-count, and
                                                                          institution-isolation,
                                                                          selection, import
                                                                          information, role,
                                                                          invalid-ID, and
                                                                          dashboard-to-detail
                                                                          workflow tests.

  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 6. What Is Out of Scope

Keep Sprint 6 focused on dataset management. Do not expand it to
include:

-   Dataset deletion or bulk deletion.
-   Comparing analytics across multiple datasets.
-   Grade calculations, charts, or the full analytics dashboard.
-   Machine learning, predictions, or AI-generated recommendations.
-   Reworking the completed CSV upload process unless a defect blocks
    dataset management.
-   Changes to the frozen MVP requirements or CSV schema without a
    separately reviewed decision.

These boundaries preserve the frozen MVP scope and leave dashboard work
for Sprint 7.

------------------------------------------------------------------------

## 7. Important Technical Decisions

### 7.1 Reuse the existing schema

-   Inspect the existing `Dataset` and `StudentRecord` models before
    proposing schema changes.
-   Reuse existing relationships, upload metadata, authentication,
    authorization, and application conventions.
-   Avoid adding a separate import-history table unless code inspection
    establishes that the current schema genuinely lacks required
    information.
-   Document the reason and impact before implementing any necessary
    schema change.

### 7.2 Keep datasets independent

-   Every student record must remain associated with its correct parent
    dataset.
-   Dataset detail pages and dataset-scoped queries must filter by the
    relevant dataset.
-   Selecting one dataset must not cause records from another dataset to
    appear.
-   Do not introduce cross-dataset analytics in Sprint 6.

### 7.3 Validate selection on the server

-   Never trust a dataset ID simply because it was submitted by the
    browser.
-   Verify that the dataset exists and that the current user is
    authorized to access it.
-   Reject invalid, nonexistent, or unauthorized selections safely.
-   Apply the same validation whenever a selected dataset is used by a
    protected operation.

### 7.4 Active dataset selection mechanism

**Proposed decision: store the selected dataset ID in the Flask
session.**

This is the preferred initial approach because it supports an explicit
active selection without requiring a new database column.

Before implementation, confirm that it fits the existing session and
authorization design. If adopted:

-   Store only the selected dataset identifier, not a copy of dataset
    records.
-   Validate the identifier against the database and the current user's
    permissions whenever it is used.
-   Handle deleted, unavailable, or unauthorized datasets by clearing or
    rejecting the stale selection safely.
-   Make the currently selected dataset visible in the interface.
-   Add tests for persistence, invalidation, and dataset isolation.

If implementation reveals a reason to use a route parameter or another
approach instead, document the reason before changing this decision.

### 7.5 Accurate record counts

Calculate record counts from the actual `StudentRecord` rows associated
with each dataset. Do not assume that a source CSV row count is
identical to the number of successfully imported records.

### 7.6 Accurate metadata and import history

-   Display values from stored database fields or other verified
    existing records.
-   Keep unknown or unavailable values unknown.
-   Do not infer import dates, uploader identities, sources, statuses,
    grade scales, or assessment labels without supporting stored
    information.
-   Reuse existing upload information wherever possible.

### 7.7 Home dashboard and Dataset Management page

-   The home dashboard should provide a convenient overview of available
    imported datasets using responsive dataset cards.
-   The dashboard should show up to six recently imported datasets by
    default. CSS grid behavior may display fewer cards at once on smaller
    screens or in different orientations.
-   The dashboard should provide a clear **View all datasets** route to the
    complete Dataset Management page.
-   Future sorting options may include recently imported, number of students,
    alphabetical order, subject, and academic year. Sorting is deferred until
    the initial management workflow is complete.
-   A separate Dataset Management page should provide the complete
    listing and access to dataset details and import information.
-   Both surfaces must apply existing authentication and authorization
    rules.
-   If no datasets exist, show a useful empty state and a permitted link
    to CSV upload.

### 7.8 Preserve existing behavior

-   Do not silently change the completed Sprint 5 CSV workflow.
-   Do not change the frozen Software Requirements Specification or MVP
    acceptance criteria.
-   Keep changes small and reviewable.
-   Run relevant tests after each implementation phase.

------------------------------------------------------------------------

## Sprint 6 Change Log

Use this log to record decisions and meaningful changes to the plan.

  -----------------------------------------------------------------------
  Date              Change / decision Reason            Approved /
                                                        verified by
  ----------------- ----------------- ----------------- -----------------
  2026-11-01        Initial Sprint 6  Establish sprint  Pending code
                    planning document scope and         review
                    created. Home     implementation    
                    dashboard dataset baseline before   
                    overview          Phase 1.          
                    included; full                      
                    listing and                         
                    details remain in                   
                    Dataset                             
                    Management. Flask                   
                    session proposed                    
                    for active                          
                    dataset                             
                    selection,                          
                    subject to code                     
                    review.                             
  2026-11-01        Phase 1 review   Reviewed models,   `.venv\Scripts\python.exe
                    complete.        upload routes,    -m pytest -v`: 124 passed
                                    authorization,    in 54.87s. The earlier
                                    templates, tests,  failure used system
                                    and database       Python, which did not
                                    relationships.    have pytest installed.
                                    Confirmed the     Proceed to Phase 2 with
                                    existing schema   institution-scoped query
                                    is sufficient for  helpers and management
                                    import history.   routes.
                                    Dataset scope must
                                    join through
                                    `Dataset.uploader`
                                    to `User.institution_id`.
  2026-11-01        Phase 2 started  Added institution-  Focused regression  Add dedicated
                                    scoped dataset       suite: 54 passed.  Sprint 6 listing
                                    query helper,        Continue with      tests and UI
                                    management listing,  Phase 2 tests and  polish, then
                                    and dashboard       verification.     proceed to
                                    overview/empty state.                  metadata details.
  2026-11-01        Phase 2 complete Added responsive     127 tests passed  Proceed to Phase 3
                                    dashboard cards for   in the full suite  for dataset details
                                    up to six recent      in 26.23s.        and metadata.
                                    datasets, full
                                    management listing,
                                    institution isolation,
                                    and empty states.
  2026-11-01        Phase 3 complete Added institution-   129 tests passed  Proceed to Phase 4
                                    scoped detail route,   in 28.94s.       for explicit active
                                    stored metadata view,                  dataset selection.
                                    authoritative record
                                    count, and records
                                    table scoped to the
                                    selected dataset.
  2026-11-01        Phase 4 complete Added session-based  132 tests passed  Proceed to Phase 5
                                    active selection,     in 72.73s.       for import-history
                                    server-side access                     presentation.
                                    validation, visible
                                    active-state badges,
                                    stale-selection
                                    cleanup, and logout
                                    cleanup.
  2026-11-01        Phase 5 complete Added explicit       133 tests passed  Proceed to Phase 6
                                    Import information    in 63.59s.       for final review,
                                    section using stored                   documentation, and
                                    Dataset fields, with                    acceptance checklist.
                                    unknown values shown
                                    as Not recorded and
                                    no separate history
                                    table introduced.
  2026-11-01        Phase 6 complete Added final role,    136 tests passed  Sprint 6 complete;
                                    invalid-ID, and       in 63.64s.       hand off selected
                                    dashboard-to-detail                     dataset context to
                                    workflow tests.                         Sprint 7.
                                    Fixed dashboard
                                    dataset cards so they
                                    link to details.
  2026-11-01        Dashboard       Agreed dashboard    Planning decision  Update dashboard
                    display         behavior: show up  recorded.          cards to six recent
                    decision        to six recent                         datasets, keep the
                                    datasets in a                         full `/datasets`
                                    responsive card                       listing, and defer
                                    grid; provide                        sorting options.
                                    View all; defer
                                    sorting options.
  2026-11-02        Final UI and     Completed dashboard, 136 tests passed  Final Sprint 6
                    handoff         setup, admin,        in 31.30s.       documentation and
                                    developer backup,                     README updated;
                                    and error-page                        ready for commit
                                    interface polish.                     and Sprint 7.

  -----------------------------------------------------------------------

**Current sprint status:** Complete --- Phases 1–6 complete; manual and automated verification recorded; ready for Sprint 7.
