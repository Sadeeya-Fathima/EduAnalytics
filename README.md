# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project designed to help teachers and administrators explore student academic performance using interactive dashboards and data analytics.

The project is being developed incrementally, with an emphasis on data management, meaningful visualizations, and a maintainable Flask application.

## Project Objectives

- Analyze student academic performance using structured datasets.
- Visualize academic results and compare student groups.
- Filter and explore data using relevant academic attributes.
- Import student records from CSV files.
- Export filtered data for further analysis.

## Planned Features

- **Authentication:** Admin and teacher login with secure password hashing.
- **Teacher Management:** Admin-controlled teacher accounts.
- **CSV Data Import:** Upload, preview, validate, and import student data.
- **Analytics Dashboard:** Summary statistics, charts, filters, and group comparisons.
- **Data Export:** Export filtered records as CSV.
- **Import History:** Track dataset imports.

> EduAnalytics is under active development. The features listed above are planned capabilities and are not all implemented yet.

## Technology Stack

- **Backend:** Python, Flask
- **Data Analysis:** Pandas, NumPy
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Charts:** Plotly.js
- **Testing:** pytest
- **Version Control:** Git and GitHub

## Current Implementation

The following components have been implemented:

- Flask application factory and application configuration.
- SQLAlchemy database models for institutions, users, datasets, student records, and upload errors.
- Database relationships and SQLite foreign-key enforcement.
- Initial database setup script for creating the institution and administrator account.
- Automated database tests covering model operations, relationships, and constraints.

The current automated test suite contains eight tests.

Authentication, teacher management, CSV processing, and the analytics dashboard remain future development tasks.

## Dataset

The project plans to use the UCI Student Performance dataset, focusing on either the mathematics or Portuguese language dataset.

Selected attributes include:

- `G1` — First-period grade
- `G2` — Second-period grade
- `G3` — Final grade
- `studytime` — Weekly study-time category
- `absences` — Number of school absences

In the selected UCI dataset, grades are recorded on a scale from 0 to 20. The `studytime` attribute represents categories of weekly study time rather than exact hours.

## Project Documentation

- [MVP Scope and Requirements Specification](docs/MVP_Scope_and_Requirements.md) — Defines the approved features, technology stack, dataset, development plan, team responsibilities, and acceptance criteria.

## Getting Started

### Prerequisites

- Python
- Git
- Visual Studio Code (recommended)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Sadeeya-Fathima/EduAnalytics.git
   cd EduAnalytics
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

### Initialize the Database

Run the initial database setup script:

```bash
python -m scripts.initialize_database
```

Follow the prompts to enter the institution details and initial administrator account information. The administrator password is stored as a hash.

**Important:** Run this setup only when you intend to initialize the local database. Use a strong password and do not commit database files or credentials to Git.

### Run the Application

```bash
python -m flask --app app:create_app run --debug
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The current application provides a basic startup confirmation. Login and dashboard functionality are still under development.

### Run Tests

```bash
python -m pytest -q
```

All eight database tests are currently passing.

## Project Status

**Current milestone:** Database models, initialization, and automated tests completed and pushed to GitHub.

**Next development milestone:** Authentication and authorization, including login, logout, password verification, and role-based route protection.

Subsequent development will cover teacher management, CSV import and validation, analytics dashboards, and filtered data export.

## Team

BCD586 mini project — team of three students.

Team member names and individual contributions can be added here as development progresses.
