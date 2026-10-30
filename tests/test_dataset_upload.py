
from io import BytesIO

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Dataset, Institution, StudentRecord, User


def make_app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        institution = Institution(name="Test Institution")
        db.session.add(institution)
        db.session.flush()
        db.session.add_all([
            User(
                userid="UPLOADADMIN",
                email="uploadadmin@example.com",
                institution_id=institution.id,
                first_name="Upload",
                last_name="Admin",
                role="admin",
                status="active",
                password=generate_password_hash("Password123!"),
            ),
            User(
                userid="UPLOADEDUCATOR",
                email="uploadeducator@example.com",
                institution_id=institution.id,
                first_name="Upload",
                last_name="Educator",
                role="educator",
                status="active",
                password=generate_password_hash("Password123!"),
            ),
            User(
                userid="UPLOADINACTIVE",
                email="uploadinactive@example.com",
                institution_id=institution.id,
                first_name="Inactive",
                last_name="User",
                role="educator",
                status="inactive",
                password=generate_password_hash("Password123!"),
            ),
        ])
        db.session.commit()

    return app


def login_as(client, userid):
    with client.session_transaction() as session:
        session["_user_id"] = userid
        session["_fresh"] = True


def configure_upload(client, **overrides):
    data = {
        "dataset_name": "Grade 10 Mathematics",
        "subject": "Mathematics",
        "grade_scale_max": "100",
        "g3_label": "Final Exam",
    }
    data.update(overrides)
    return client.post("/datasets/upload", data=data, follow_redirects=True)


def upload_csv(client, content, filename="records.csv"):
    return client.post(
        "/datasets/upload/csv",
        data={"csv_file": (BytesIO(content), filename)},
        content_type="multipart/form-data",
        follow_redirects=True,
    )


def test_authenticated_educator_can_view_upload_page():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")

    response = client.post(
        "/datasets/upload",
        data={
            "dataset_name": "Grade 10 Mathematics",
            "subject": "Mathematics",
            "grade_scale_max": "100",
            "g1_label": "Internal 1",
            "g2_label": "Internal 2",
            "g3_label": "Final Exam",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Import an academic dataset" in response.data
    assert b"Download CSV Template" in response.data
    assert b"Student Name" in response.data
    assert b"required-marker" in response.data
    assert b"Study Time" in response.data
    assert b"Absences" in response.data
    assert b">Edit<" in response.data


def test_upload_page_has_explicit_file_picker_and_auto_submit_behavior():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)
    response = client.get("/datasets/upload")
    assert b'id="select-file-button"' in response.data
    assert b'id="csv-file"' in response.data
    assert b"csvInput.click()" in response.data
    assert b"requestSubmit()" in response.data


def test_authenticated_admin_can_view_upload_page():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADADMIN")

    response = client.get("/datasets/upload")

    assert response.status_code == 200


def test_unauthenticated_user_is_redirected_from_upload_page():
    app = make_app()
    response = app.test_client().get("/datasets/upload")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_inactive_user_is_redirected_from_upload_page():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADINACTIVE")

    response = client.get("/datasets/upload")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_authenticated_user_can_download_canonical_template():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")

    configure_upload(client)

    response = client.get("/datasets/template")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.headers["Content-Disposition"].startswith("attachment;")
    assert response.data == b"Student Name *,Final Exam *,Study Time,Absences\n"


def test_uploaded_csv_is_validated_and_previewed():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    client.post(
        "/datasets/upload",
        data={
            "dataset_name": "Grade 10 Mathematics",
            "subject": "Mathematics",
            "grade_scale_max": "100",
            "g3_label": "Final Exam",
        },
        follow_redirects=True,
    )

    response = upload_csv(
        client,
        b"Student Name *,Final Exam *,Study Time,Absences\n"
        b"Student 001,75,5,2\n",
    )

    assert response.status_code == 200
    assert b"Validation passed" in response.data
    assert b"Student 001" in response.data
    assert b"Ready to import" in response.data
    assert b"Do Not Upload" in response.data
    assert b">Confirm</button>" in response.data
    assert b"Import / Confirm" not in response.data
    assert b'class="workflow-button confirm" type="submit" name="action" value="confirm" disabled' not in response.data
    assert b"formnovalidate" in response.data

    reload_response = client.get("/datasets/upload")
    assert reload_response.status_code == 200
    assert b"Student 001" in reload_response.data


def test_uploaded_csv_reports_invalid_grade():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client, grade_scale_max="20")

    response = upload_csv(
        client,
        b"Student Name *,Final Exam *,Study Time,Absences\n"
        b"Student 001,25,5,2\n",
    )

    assert response.status_code == 200
    assert b"Validation needs attention" in response.data
    assert b"enter a number from 0 to 20" in response.data
    assert b">Retry<" in response.data
    assert b"<ul>" not in response.data


def test_uploaded_csv_reports_header_error_when_no_rows_can_be_parsed():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client, grade_scale_max="20")

    response = upload_csv(
        client,
        b"wrong_name,Final Exam *,Study Time,Absences\n"
        b"Student 001,15,5,2\n",
    )

    assert response.status_code == 200
    assert b"CSV headers do not match the generated structure" in response.data
    assert b"Expected:" in response.data
    assert b"Received:" in response.data


def test_dynamic_labels_appear_in_template_and_unconfigured_grades_are_omitted():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")

    response = configure_upload(client, g1_label="Internal 1", g2_label="Internal 2")
    assert b"Internal 1" in response.data
    assert b"Internal 2" in response.data
    assert b"Study Time (optional)" not in response.data
    assert b"Absences (optional)" not in response.data

    template = client.get("/datasets/template")
    assert template.data == (
        b"Student Name *,Internal 1 *,Internal 2 *,Final Exam *,Study Time,Absences\n"
    )


def test_metadata_rejects_missing_g3_invalid_scale_and_duplicate_labels():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")

    missing_g3 = client.post(
        "/datasets/upload",
        data={"dataset_name": "Test", "subject": "Math", "grade_scale_max": "20"},
    )
    assert missing_g3.status_code == 400
    assert b"G3 label are required" in missing_g3.data

    invalid_scale = configure_upload(client, grade_scale_max="0")
    assert invalid_scale.status_code == 400
    assert b"positive whole number" in invalid_scale.data

    duplicate = configure_upload(client, g1_label="Final Exam", g2_label="Final Exam")
    assert duplicate.status_code == 400
    assert b"must be unique" in duplicate.data


def test_mixed_rows_show_original_values_red_invalid_cells_and_remarks():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client, grade_scale_max="20", g1_label="First Internal", g2_label="Second Internal")

    response = upload_csv(
        client,
        b"Student Name *,First Internal *,Second Internal *,Final Exam *,Study Time,Absences\n"
        b"Student 001,18,17,19,2.5,1\n"
        b"Student 002,not-a-grade,22,25,invalid,-1\n",
    )

    assert b"Student 001" in response.data
    assert b"Student 002" in response.data
    assert b"Ready to import" in response.data
    assert b"Remarks" in response.data
    assert b"enter a number from 0 to 20" in response.data
    assert b"invalid" in response.data
    assert b"class=\"invalid-cell\"" in response.data
    assert b'name="exclude_rows" value="3"' in response.data
    assert b'id="exclude-all"' in response.data

    with app.app_context():
        assert Dataset.query.count() == 0


def test_file_failures_are_reported_and_retry_clears_preview():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)

    bad_type = upload_csv(client, b"not really a csv", filename="records.txt")
    assert b"Only CSV files are supported" in bad_type.data

    empty = upload_csv(client, b"", filename="empty.csv")
    assert b"uploaded CSV file is empty" in empty.data

    valid = upload_csv(
        client,
        b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,75,5,2\n",
    )
    assert b"Student 001" in valid.data

    retry = client.get("/datasets/upload/reset", follow_redirects=True)
    assert retry.status_code == 200
    assert b"Student 001" not in retry.data
    assert b"Example Student" in retry.data


def test_study_time_must_be_non_negative_and_absences_are_whole_days():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)
    response = upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,75,-2,1.5\n")
    assert b"non-negative number of hours per week" in response.data
    assert b"non-negative whole number" in response.data


def test_upload_limit_is_five_mib():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)
    response = upload_csv(client, b"a" * (5 * 1024 * 1024), filename="large.csv")
    assert response.status_code == 200
    assert b"too large" in response.data
    assert b"no larger than 5 MiB" in response.data


def test_confirm_import_persists_only_selected_valid_rows_and_clears_workflow():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client, grade_scale_max="20", g1_label="Internal 1")
    upload_csv(
        client,
        b"Student Name *,Internal 1 *,Final Exam *,Study Time,Absences\n"
        b"Student 001,18,19,2.5,1\n"
        b"Student 002,17,16,,0\n",
    )
    with client.session_transaction() as session:
        import_token = session["dataset_preview_token"]

    response = client.post(
        "/datasets/upload/csv",
        data={"action": "confirm", "import_token": import_token, "exclude_rows": "3"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Dataset imported successfully with 1 student record" in response.data
    assert b"Import complete" in response.data
    assert b"Import another dataset" in response.data
    assert b"Generate CSV Structure" not in response.data
    with app.app_context():
        dataset = Dataset.query.one()
        assert dataset.source_filename == "records.csv"
        assert dataset.record_count == 1
        assert StudentRecord.query.count() == 1
        record = StudentRecord.query.one()
        assert record.student_name == "Student 001"
        assert record.g1 == 18
        assert record.g3 == 19
        assert record.studytime == 2.5
        assert record.absences == 1

    with client.session_transaction() as session:
        assert "dataset_upload" not in session
        assert "dataset_preview_token" not in session


def test_confirm_import_rejects_when_all_rows_are_marked_do_not_upload():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)
    upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,75,5,2\nStudent 002,80,4,1\n")
    with client.session_transaction() as session:
        token = session["dataset_preview_token"]

    response = client.post(
        "/datasets/upload/csv",
        data={"action": "confirm", "import_token": token, "exclude_rows": ["2", "3"]},
        follow_redirects=True,
    )
    assert b"Select at least one valid row to import" in response.data
    with app.app_context():
        assert Dataset.query.count() == 0
        assert StudentRecord.query.count() == 0


def test_confirm_is_blocked_when_csv_has_no_valid_rows():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client, grade_scale_max="20")
    response = upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,25,-1,1.5\n")
    assert b"Validation needs attention" in response.data
    assert b"Confirm" in response.data
    assert b"disabled" in response.data
    with app.app_context():
        assert Dataset.query.count() == 0
        assert StudentRecord.query.count() == 0


def test_confirm_import_requires_a_valid_preview_and_does_not_duplicate():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)

    missing_preview = client.post(
        "/datasets/upload/csv",
        data={"action": "confirm"},
        follow_redirects=True,
    )
    assert b"Upload and validate a CSV before confirming" in missing_preview.data

    upload_csv(
        client,
        b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,75,5,2\n",
    )
    with client.session_transaction() as session:
        import_token = session["dataset_preview_token"]
    first = client.post(
        "/datasets/upload/csv",
        data={"action": "confirm", "import_token": import_token},
        follow_redirects=True,
    )
    assert b"Dataset imported successfully" in first.data

    second = client.post(
        "/datasets/upload/csv",
        data={"action": "confirm"},
        follow_redirects=True,
    )
    assert b"Enter the dataset details before uploading" in second.data
    with app.app_context():
        assert Dataset.query.count() == 1
        assert StudentRecord.query.count() == 1


def test_import_token_cannot_be_replayed():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)
    upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,75,5,2\n")
    with client.session_transaction() as session:
        token = session["dataset_preview_token"]
    client.post("/datasets/upload/csv", data={"action": "confirm", "import_token": token}, follow_redirects=True)
    replay = client.post("/datasets/upload/csv", data={"action": "confirm", "import_token": token}, follow_redirects=True)
    assert b"Enter the dataset details before uploading" in replay.data
    with app.app_context():
        assert Dataset.query.count() == 1


def test_import_rolls_back_dataset_and_records_on_database_failure(monkeypatch):
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)
    upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\nStudent 001,75,5,2\n")
    with client.session_transaction() as session:
        token = session["dataset_preview_token"]

    def fail_commit():
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr("app.datasets.routes.db.session.commit", fail_commit)
    response = client.post("/datasets/upload/csv", data={"action": "confirm", "import_token": token}, follow_redirects=True)
    assert b"No records were saved" in response.data
    with app.app_context():
        assert Dataset.query.count() == 0
        assert StudentRecord.query.count() == 0


def test_malformed_encoding_uci_and_oversized_csv_inputs_are_rejected():
    app = make_app()
    client = app.test_client()
    login_as(client, "UPLOADEDUCATOR")
    configure_upload(client)

    malformed = upload_csv(client, b'Student Name *,Final Exam *,Study Time,Absences\n"Student 001,75,5,2\n')
    assert b"malformed" in malformed.data

    invalid_encoding = upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\nStudent \xff,75,5,2\n")
    assert b"UTF-8 encoding" in invalid_encoding.data

    uci = upload_csv(client, b"student;G1;G2;G3;studytime;absences\n001;10;11;12;2;3\n")
    assert b"Semicolon-delimited files are not supported" in uci.data

    oversized_field = upload_csv(client, b"Student Name *,Final Exam *,Study Time,Absences\n" + b"A" * 256 + b",75,5,2\n")
    assert b"exceeds 255 characters" in oversized_field.data
