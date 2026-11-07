import csv
from io import StringIO

from tests.test_analytics_preprocessing import make_app
from app.analytics.services import apply_filters, prepare_analysis_input
from app.extensions import db
from app.models import Dataset, Institution, StudentRecord, User


def login_as(client):
    with client.session_transaction() as session:
        session["_user_id"] = "ANALYTICS"
        session["_fresh"] = True


def test_authorized_user_can_open_dataset_analytics():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}")

    assert response.status_code == 200
    assert b"Class Performance Overview" in response.data
    assert b"Overall class performance" in response.data
    assert b"Detailed Statistics" in response.data
    assert b"grade distribution" in response.data
    assert b"Assessment comparison" in response.data
    assert b"analyticsData" in response.data


def test_analytics_requires_login():
    app, dataset_id = make_app()

    response = app.test_client().get(f"/analytics/{dataset_id}")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_dashboard_filters_update_matching_count_and_can_reset():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    filtered = client.get(f"/analytics/{dataset_id}?studytime_min=5&absence_group=low")
    assert filtered.status_code == 200
    assert b"1 matching records" in filtered.data
    assert b"Total students" in filtered.data

    reset = client.get(f"/analytics/{dataset_id}")
    assert reset.status_code == 200
    assert b"3 matching records" in reset.data


def test_dashboard_export_action_preserves_active_filters():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}?g3_min=16&absence_group=low")

    assert response.status_code == 200
    assert b"Export CSV" in response.data
    assert (
        f"/analytics/{dataset_id}/export?g3_min=16&amp;absence_group=low".encode()
        in response.data
    )


def test_dashboard_rejects_invalid_filter():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}?studytime_min=18&studytime_max=10")

    assert response.status_code == 400


def test_dashboard_marks_unavailable_studytime_and_absences():
    app, dataset_id = make_app()
    with app.app_context():
        records = StudentRecord.query.filter_by(dataset_id=dataset_id).all()
        for record in records:
            record.studytime = None
            record.absences = None
        db.session.commit()

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{dataset_id}")

    assert response.status_code == 200
    assert b"Study-time analysis is unavailable for this dataset." in response.data
    assert b"Attendance analysis is unavailable for this dataset." in response.data


def test_dataset_quality_remains_unfiltered_when_filters_are_applied():
    app, dataset_id = make_app()
    with app.app_context():
        dataset = db.session.get(Dataset, dataset_id)
        original = prepare_analysis_input(dataset).quality
        filtered, _ = apply_filters(prepare_analysis_input(dataset).records, {"g3_min": "16"}, dataset.grade_scale_max)

    assert original.total_records == 3
    assert original.valid_g3_records == 3
    assert len(filtered) == 2


def test_authorized_user_can_export_filtered_records_as_csv():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}/export?g3_min=16")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.headers["Content-Disposition"].startswith("attachment;")
    rows = list(csv.DictReader(StringIO(response.get_data(as_text=True))))
    assert list(rows[0]) == ["student_name", "g1", "g2", "g3", "studytime", "absences"]
    assert [row["student_name"] for row in rows] == ["B", "C"]
    assert rows[0]["studytime"] == ""


def test_export_without_filters_contains_all_records_and_approved_headers():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}/export")
    rows = list(csv.reader(StringIO(response.get_data(as_text=True))))

    assert response.status_code == 200
    assert rows[0] == ["student_name", "g1", "g2", "g3", "studytime", "absences"]
    assert [row[0] for row in rows[1:]] == ["A", "B", "C"]
    assert "student=" not in response.get_data(as_text=True)
    assert "attachment;" in response.headers["Content-Disposition"]
    assert "analytics_Analytics_Dataset_1_" in response.headers["Content-Disposition"]


def test_export_combined_filters_match_dashboard_filter_semantics():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(
        f"/analytics/{dataset_id}/export?g3_min=14&g3_max=16&studytime_min=5&absence_group=low"
    )
    rows = list(csv.DictReader(StringIO(response.get_data(as_text=True))))

    assert response.status_code == 200
    assert [row["student_name"] for row in rows] == ["A"]


def test_export_quotes_csv_values_with_commas_and_newlines():
    app, dataset_id = make_app()
    with app.app_context():
        record = StudentRecord.query.filter_by(dataset_id=dataset_id, student=1).one()
        record.student_name = "Doe, Jane\nClass A"
        db.session.commit()

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{dataset_id}/export")
    rows = list(csv.DictReader(StringIO(response.get_data(as_text=True))))

    assert rows[0]["student_name"] == "Doe, Jane\nClass A"


def test_export_handles_a_large_filtered_result_set():
    app, dataset_id = make_app()
    with app.app_context():
        db.session.add_all(
            [
                StudentRecord(
                    student=index,
                    dataset_id=dataset_id,
                    student_name=f"Student {index}",
                    g1=10,
                    g2=11,
                    g3=12,
                    studytime=5,
                    absences=2,
                )
                for index in range(4, 1004)
            ]
        )
        db.session.commit()

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{dataset_id}/export?g3_min=12")

    assert response.status_code == 200
    assert len(response.get_data(as_text=True).splitlines()) == 1004


def test_export_rejects_invalid_filters():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}/export?g3_min=bad")

    assert response.status_code == 400


def test_export_returns_header_only_for_empty_results():
    app, dataset_id = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get(f"/analytics/{dataset_id}/export?g3_min=20")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "student_name,g1,g2,g3,studytime,absences\n"


def test_export_protects_formula_like_student_names():
    app, dataset_id = make_app()
    with app.app_context():
        record = StudentRecord.query.filter_by(dataset_id=dataset_id, student=1).one()
        record.student_name = "=SUM(A1:A2)"
        db.session.commit()

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{dataset_id}/export")

    assert response.status_code == 200
    assert "'=SUM(A1:A2)" in response.get_data(as_text=True)


def test_export_requires_authentication():
    app, dataset_id = make_app()

    response = app.test_client().get(f"/analytics/{dataset_id}/export")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_export_rejects_roles_without_analytics_access():
    app, dataset_id = make_app()
    with app.app_context():
        user = db.session.get(User, "ANALYTICS")
        user.role = "student"
        db.session.commit()

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{dataset_id}/export")

    assert response.status_code == 403


def test_export_hides_dataset_from_another_institution():
    app, dataset_id = make_app()
    with app.app_context():
        other_institution = Institution(name="Other Institution")
        db.session.add(other_institution)
        db.session.flush()
        other_user = User(
            userid="OTHER",
            email="other@example.com",
            institution_id=other_institution.id,
            first_name="Other",
            last_name="User",
            role="educator",
            status="active",
            password="hashed",
        )
        db.session.add(other_user)
        db.session.flush()
        other_dataset = Dataset(
            name="Other Dataset",
            source_filename="other.csv",
            uploaded_by=other_user.userid,
            subject="Science",
            grade_scale_max=20,
            g3_label="G3",
            import_status="complete",
        )
        db.session.add(other_dataset)
        db.session.commit()
        other_dataset_id = other_dataset.id

    client = app.test_client()
    login_as(client)
    response = client.get(f"/analytics/{other_dataset_id}/export")

    assert response.status_code == 404


def test_export_rejects_invalid_dataset_id():
    app, _ = make_app()
    client = app.test_client()
    login_as(client)

    response = client.get("/analytics/999999/export")

    assert response.status_code == 404
