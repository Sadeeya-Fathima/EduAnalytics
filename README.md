# EduAnalytics

**Student Academic Performance Analytics Platform**

EduAnalytics is a BCD586 mini project designed to help teachers and administrators explore student academic performance using interactive dashboards and data analytics.

## Project Objectives

- Analyze student academic performance using structured datasets.
- Visualize academic results and compare student groups.
- Filter and explore data using relevant academic attributes.
- Import student records from CSV files.
- Export filtered data for further analysis.

## Planned Features

- **Authentication:** Admin and teacher login.
- **Teacher Management:** Admin-controlled teacher accounts.
- **CSV Data Import:** Upload, preview, validate, and import student data.
- **Analytics Dashboard:** Summary statistics, charts, filters, and group comparisons.
- **Data Export:** Export filtered records as CSV.
- **Import History:** Track dataset imports.

> Note: EduAnalytics is under development. Features will be implemented incrementally as part of the mini project.

## Technology Stack

- **Backend:** Python, Flask
- **Data Analysis:** Pandas, NumPy
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Charts:** Plotly.js
- **Testing:** pytest
- **Version Control:** Git and GitHub

## Dataset

The project plans to use the UCI Student Performance dataset, focusing on either the mathematics or Portuguese language dataset.

Selected attributes include:
- `G1` — First-period grade
- `G2` — Second-period grade
- `G3` — Final grade
- `studytime` — Weekly study-time category
- `absences` — Number of school absences

The final grade (`G3`) is recorded on a scale from 0 to 20 in the selected dataset.

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

### Run the Application

```bash
python -m flask --app app:create_app run --debug
```

Open `http://127.0.0.1:5000` in your browser.

### Run Tests

```bash
python -m pytest -q
```

## Project Status

The initial Flask application, dependency setup, automated test, and GitHub repository have been established. Analytics, authentication, CSV processing, and dashboard functionality are planned development tasks.

## Team

BCD586 mini project — team of three students.

Team member names and individual contributions can be added here as development progresses.