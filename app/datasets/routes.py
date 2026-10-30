from io import BytesIO

import csv
import uuid
from io import BytesIO, StringIO

from flask import current_app, flash, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user

from app.auth.decorators import role_required
from app.datasets import datasets_bp
from app.extensions import db
from app.models import Dataset, StudentRecord

MAX_CSV_ROWS = 10_000
MAX_FIELD_LENGTH = 255
_PREVIEW_STORE = {}


def _column_configuration(metadata):
    """Build the visible CSV headers and stable internal-field mapping."""
    columns = [("Student Name *", "student_name")]
    if metadata["g1_label"]:
        columns.append((f"{metadata['g1_label']} *", "g1"))
    if metadata["g2_label"]:
        columns.append((f"{metadata['g2_label']} *", "g2"))
    columns.extend([
        (f"{metadata['g3_label']} *", "g3"),
        ("Study Time", "studytime"),
        ("Absences", "absences"),
    ])
    return columns


def _current_preview():
    token = session.get("dataset_preview_token")
    return _PREVIEW_STORE.get(token) if token else None


def _validate_csv(file_storage, metadata):
    """Parse and validate an uploaded CSV against the generated columns."""
    raw = file_storage.read()
    if not raw:
        return [], ["The uploaded CSV file is empty."]
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], ["The CSV file must use UTF-8 encoding."]

    first_line = text.splitlines()[0] if text.splitlines() else ""
    if ";" in first_line and "," not in first_line:
        return [], ["Semicolon-delimited files are not supported. Convert the file to the EduAnalytics CSV template."]
    reader = csv.reader(StringIO(text), strict=True)
    try:
        parsed_rows = list(reader)
    except StopIteration:
        return [], ["The uploaded CSV file does not contain a header row."]
    except csv.Error:
        return [], ["The uploaded CSV file is malformed. Check its quoting and column separators."]
    if not parsed_rows:
        return [], ["The uploaded CSV file does not contain a header row."]
    headers, *data_rows = parsed_rows

    expected = [column for column, _internal in metadata["columns"]]
    if headers != expected:
        return [], [
            "CSV headers do not match the generated structure.",
            f"Expected: {', '.join(expected)}",
            f"Received: {', '.join(headers)}",
        ]

    rows = []
    errors = []
    field_map = {header: internal for header, internal in metadata["columns"]}
    for row_number, values in enumerate(data_rows, start=2):
        if row_number > MAX_CSV_ROWS + 1:
            errors.append(f"The CSV exceeds the maximum of {MAX_CSV_ROWS} student records.")
            break
        if not any(value.strip() for value in values):
            continue
        if len(values) != len(headers):
            errors.append(f"Row {row_number}: expected {len(headers)} columns, received {len(values)}.")
            continue

        record = {}
        row_errors = []
        invalid_fields = set()

        def add_error(message, field=None):
            errors.append(message)
            row_errors.append(message)
            if field:
                invalid_fields.add(field)

        for header, value in zip(headers, values):
            internal = field_map[header]
            value = value.strip()
            if len(value) > MAX_FIELD_LENGTH:
                add_error(f"Row {row_number}, {header}: value exceeds {MAX_FIELD_LENGTH} characters.", internal)
                value = value[:MAX_FIELD_LENGTH]
            if internal == "student_name":
                if not value:
                    add_error(f"Row {row_number}, Student Name: a value is required.", internal)
                record[internal] = value
            elif internal == "g3" and not value:
                add_error(f"Row {row_number}, {header}: a final grade is required.", internal)
                record[internal] = value
            elif internal in {"g1", "g2", "g3"}:
                record[internal] = value
                try:
                    grade = float(value)
                    if not 0 <= grade <= metadata["grade_scale_max"]:
                        raise ValueError
                    record[internal] = grade
                except ValueError:
                    add_error(f"Row {row_number}, {header}: enter a number from 0 to {metadata['grade_scale_max']}.", internal)
            elif internal == "studytime":
                if value:
                    try:
                        studytime = float(value)
                        if studytime < 0:
                            raise ValueError
                        record[internal] = studytime
                    except ValueError:
                        add_error(f"Row {row_number}, {header}: enter a non-negative number of hours per week or leave it blank.", internal)
                        record[internal] = value
                else:
                    record[internal] = ""
            elif internal == "absences":
                if value:
                    try:
                        absence = int(value)
                        if absence < 0:
                            raise ValueError
                        record[internal] = absence
                    except ValueError:
                        add_error(f"Row {row_number}, {header}: enter a non-negative whole number or leave it blank.", internal)
                        record[internal] = value
                else:
                    record[internal] = ""
        record["row_number"] = row_number
        record["_remarks"] = row_errors
        record["_invalid_fields"] = invalid_fields
        rows.append(record)

    if not rows:
        errors.append("The CSV does not contain any student records.")
    return rows, errors


@datasets_bp.route("/upload", methods=["GET", "POST"])
@role_required("admin", "educator")
def upload():
    if request.method == "POST":
        name = request.form.get("dataset_name", "").strip()
        subject = request.form.get("subject", "").strip()
        department = request.form.get("department", "").strip()
        academic_year_choice = request.form.get("academic_year_choice", "").strip()
        academic_year_custom = request.form.get("academic_year_custom", "").strip()
        academic_year = academic_year_custom if academic_year_choice == "custom" else academic_year_choice
        if not academic_year_choice:
            academic_year = request.form.get("academic_year", "").strip()
        class_section = request.form.get("class_section", "").strip()
        grade_scale_max = request.form.get("grade_scale_max", "").strip()
        g1_label = request.form.get("g1_label", "").strip()
        g2_label = request.form.get("g2_label", "").strip()
        g3_label = request.form.get("g3_label", "").strip()

        if not name or not subject or not g3_label:
            flash("Dataset name, subject, and G3 label are required.", "error")
            return render_template("datasets/upload.html"), 400

        try:
            grade_scale_max = int(grade_scale_max)
            if grade_scale_max <= 0:
                raise ValueError
        except ValueError:
            flash("Grade scale maximum must be a positive whole number.", "error")
            return render_template("datasets/upload.html"), 400

        labels = [label for label in (g1_label, g2_label, g3_label) if label]
        reserved = {"Student Name", "Study Time", "Absences"}
        if len(set(labels)) != len(labels) or any(label in reserved for label in labels):
            flash("Grade labels must be unique and must not use reserved column names.", "error")
            return render_template("datasets/upload.html"), 400

        metadata = {
            "name": name,
            "subject": subject,
            "department": department or None,
            "academic_year": academic_year or None,
            "class_section": class_section or None,
            "grade_scale_max": grade_scale_max,
            "g1_label": g1_label or None,
            "g2_label": g2_label or None,
            "g3_label": g3_label,
        }
        metadata["columns"] = _column_configuration(metadata)
        session["dataset_upload"] = metadata
        flash("Dataset details saved. Use the generated headers for your CSV.", "success")
        return redirect(url_for("datasets.upload"))

    metadata = session.get("dataset_upload")
    if metadata:
        # Rebuild derived columns so older session state cannot retain
        # previously generated labels or optional-column text.
        metadata["columns"] = _column_configuration(metadata)
        session["dataset_upload"] = metadata
    response = render_template(
        "datasets/upload.html",
        metadata=metadata,
        columns=metadata["columns"] if metadata else None,
        upload_result=_current_preview(),
        import_result=session.pop("dataset_import_result", None),
    )
    return response, 200, {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
    }


@datasets_bp.route("/upload/csv", methods=["POST"])
@role_required("admin", "educator")
def upload_csv():
    current_app.logger.info(
        "Dataset CSV upload request received: method=%s files=%s content_length=%s",
        request.method,
        list(request.files.keys()),
        request.content_length,
    )
    metadata = session.get("dataset_upload")
    if not metadata:
        flash("Enter the dataset details before uploading a CSV.", "error")
        return redirect(url_for("datasets.upload"))

    metadata["columns"] = _column_configuration(metadata)
    if request.form.get("action") == "confirm":
        return confirm_import()

    upload_file = request.files.get("csv_file")
    current_app.logger.info(
        "Dataset CSV upload file: present=%s filename=%s content_type=%s",
        upload_file is not None,
        upload_file.filename if upload_file else None,
        upload_file.content_type if upload_file else None,
    )
    if upload_file is None or not upload_file.filename:
        flash("Choose a CSV file to upload.", "error")
        return redirect(url_for("datasets.upload"))

    if not upload_file.filename.lower().endswith(".csv"):
        flash("Only CSV files are supported.", "error")
        return redirect(url_for("datasets.upload"))

    rows, errors = _validate_csv(upload_file, metadata)
    preview_rows = []
    for row in rows:
        preview_row = dict(row)
        preview_row["_invalid_fields"] = list(row["_invalid_fields"])
        preview_rows.append(preview_row)
    preview = {
        "rows": preview_rows,
        "errors": errors,
        "valid": not errors,
        "source_filename": upload_file.filename,
        "import_token": uuid.uuid4().hex,
    }
    _PREVIEW_STORE[preview["import_token"]] = preview
    session["dataset_preview_token"] = preview["import_token"]
    return redirect(url_for("datasets.upload"))


def confirm_import():
    """Persist only a validated, non-excluded preview in one transaction."""
    metadata = session.get("dataset_upload")
    preview = _current_preview()
    if not metadata or not preview:
        flash("Upload and validate a CSV before confirming the import.", "error")
        return redirect(url_for("datasets.upload"))
    submitted_token = request.form.get("import_token", "")
    if not submitted_token or submitted_token != preview.get("import_token"):
        flash("This import confirmation has expired. Upload the CSV again before confirming.", "error")
        return redirect(url_for("datasets.upload"))
    if not preview.get("valid"):
        flash("Correct the validation errors before confirming the import.", "error")
        return redirect(url_for("datasets.upload"))

    excluded = {int(value) for value in request.form.getlist("exclude_rows")}
    rows = [row for row in preview["rows"] if row["row_number"] not in excluded]
    if not rows:
        flash("Select at least one valid row to import.", "error")
        return redirect(url_for("datasets.upload"))

    try:
        dataset = Dataset(
            name=metadata["name"],
            source_filename=preview.get("source_filename", "uploaded.csv"),
            uploaded_by=current_user.userid,
            subject=metadata["subject"],
            department=metadata.get("department"),
            academic_year=metadata.get("academic_year"),
            class_section=metadata.get("class_section"),
            grade_scale_max=metadata["grade_scale_max"],
            g1_label=metadata.get("g1_label"),
            g2_label=metadata.get("g2_label"),
            g3_label=metadata["g3_label"],
            import_status="complete",
        )
        db.session.add(dataset)
        db.session.flush()
        next_student_id = (db.session.query(db.func.max(StudentRecord.student)).scalar() or 0) + 1
        for offset, row in enumerate(rows):
            db.session.add(StudentRecord(
                student=next_student_id + offset,
                dataset_id=dataset.id,
                student_name=row["student_name"],
                g1=row.get("g1") if row.get("g1") != "" else None,
                g2=row.get("g2") if row.get("g2") != "" else None,
                g3=row["g3"],
                studytime=row.get("studytime") if row.get("studytime") != "" else None,
                absences=row.get("absences") if row.get("absences") != "" else None,
            ))
        dataset.record_count = len(rows)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("The import could not be completed. No records were saved.", "error")
        return redirect(url_for("datasets.upload"))

    _PREVIEW_STORE.pop(session.pop("dataset_preview_token", None), None)
    session.pop("dataset_upload", None)
    session["dataset_import_result"] = {
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
        "record_count": len(rows),
        "source_filename": dataset.source_filename,
    }
    flash(f"Dataset imported successfully with {len(rows)} student record(s).", "success")
    return redirect(url_for("datasets.upload"))


@datasets_bp.route("/upload/edit", methods=["GET"])
@role_required("admin", "educator")
def edit_upload_details():
    session.pop("dataset_upload", None)
    _PREVIEW_STORE.pop(session.pop("dataset_preview_token", None), None)
    return redirect(url_for("datasets.upload"))


@datasets_bp.route("/upload/reset", methods=["GET"])
@role_required("admin", "educator")
def reset_upload_preview():
    _PREVIEW_STORE.pop(session.pop("dataset_preview_token", None), None)
    return redirect(url_for("datasets.upload"))


@datasets_bp.route("/template", methods=["GET"])
@role_required("admin", "educator")
def template():
    metadata = session.get("dataset_upload")
    if not metadata:
        return redirect(url_for("datasets.upload"))

    headers = [column[0] for column in metadata["columns"]]
    csv_content = StringIO()
    csv.writer(csv_content, lineterminator="\n").writerow(headers)
    return send_file(
        BytesIO(csv_content.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="eduanalytics_template.csv",
    )
